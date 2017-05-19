# encoding=utf8
import decorator


class EventLoop(object):
	'''
	事件主循环类
	'''

	def __init__(self, timeout, logger):
		import poller, timer, threading, Queue, pipe_event
		self._logger = logger  # 日志输出
		#self._poller = poller.SelectPoller(self._logger)  # io复用api的封装
		self._poller = poller.KqueuePoller(self._logger)  # io复用api的封装
		self._timer_queue = timer.TimerQueue(self)  # 定时器
		self._is_running = False  # 是否启动
		self._timeout = timeout  # io复用阻塞时间,这也决定了定时器的精度

		self._thread_id = threading.currentThread()  # 当前线程id

		self.pipe_event = pipe_event.PipeEvent(self, self._logger)  # 其他线程用于写入唤醒阻塞poller的管道对象

		# 其它线程塞进来的要在io线程里执行的函数以及参数
		# funtor_with_args : (functor,args,kwargs)
		self.inloop_functor_with_args_queue = Queue.Queue()

		self.excuting_inloop_functors = False

		pass

	def local_thread(self):
		# 验证当前执行local thread 的函数是否是在loop 所在的io线程里运行
		import threading
		current_thread_id = threading.currentThread()
		return current_thread_id == self._thread_id

	def excute_inloop_funtctors(self):
		# 将截止此刻,其他线程存入本io线程inloop队列的函数,都执行掉
		self.excuting_inloop_functors = True
		functor_count = self.inloop_functor_with_args_queue.qsize()  # 获取这一刻一共有多少个functor要执行,之后加入队列的,下个周期执行
		while functor_count > 0:
			functor, calle_ins, args, kwargs = self.inloop_functor_with_args_queue.get()
			functor(calle_ins, *args, **kwargs)  # 执行
			functor_count -= 1

		self.excuting_inloop_functors = False

	def add_inloop_functor(self, functor_with_args):
		# 向io线程的inloop队列里添加函数和函数调用的参数
		self.inloop_functor_with_args_queue.put(functor_with_args)

		if self.local_thread() == False:
			# 当其他线程塞进来一个函数,为能够即使执行到,需要唤醒poller
			self.pipe_event.wake_up()

		elif self.excuting_inloop_functors:
			# 某个从队列里取出的操作,执行时将另一个操作压进了队列里,为使这个操作能够被即时执行,需要唤醒poller
			self.pipe_event.wake_up()

	def loop(self):
		'''
		事件主循环
		'''

		while self._is_running:
			active_channel_lst = self._poller.poll(self._timeout)
			for channel in active_channel_lst:
				channel.handle_event()
			# 处理定时任务
			self._timer_queue.schedule()
			# 处理其他线程塞进来的任务
			self.excute_inloop_funtctors()
		pass

	def update_channel(self, channel):
		# loop 应该对上层屏蔽poller 的接口
		self._poller.update_channel(channel)

		pass

	def remove_channel(self, channel):
		# loop 应该对上层屏蔽poller 的接口
		self._poller.remove_channel(channel)
		pass

	def add_timer(self, tme):
		self._timer_queue.add_timer(tme)

	def remove_timer(self, timer_id):
		self._timer_queue.remove_timer(timer_id)


if __name__ == '__main__':
	import logger

	event_loop_ins = EventLoop(1, logger.Logger())
	event_loop_ins._is_running = True
	event_loop_ins.loop()
	pass
