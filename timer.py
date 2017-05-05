#encoding=utf8
import decorator
class Timer(object):
	'''
	定时事件
	'''
	timer_seq=0 # 静态变量
	def __init__(self,expiration,internal,method,*args,**kwargs):
		self._expiration=expiration # 到期,(第一次)执行的时间点
		self._internal=internal #间隔

		self._method=method
		self._args=args
		self._kwargs=kwargs

		self.timer_id=Timer.timer_seq #全系统内,以一个累加的序号标识一个timer
		Timer.timer_seq+=1


		self.canceled=False
		pass

	@property
	def repeatable(self):
		if self._internal>0:
			return True
		return False

	def __le__(self,other):
		# 相当于重载<=符号
		# 用作堆中两个timer 的比较操作
		return self._expiration<=other._expiration




class TimerQueue(object):
	'''
	存放定时器事件的优先级队列(堆)
	'''

	def __init__(self,loop):
		import Queue
		self._loop=loop # 调用decorator.RunInLoop的类一定要有_loop 成员
		self.heap=Queue.PriorityQueue()
		self.cancel_timer_count=0
		pass


	@decorator.RunInLoop
	def add_timer(self,timer):
		self.heap.put(timer)
		pass

	def schedule(self):
		import time
		now=time.time()
		#print "schedule:",self.heap.queue,self.heap.queue[0].timer_id,self.heap.queue[0].canceled,self.heap.queue[0]._method
		while not self.heap.empty():
			if now<self.heap.queue[0]._expiration:
				# 没有到时间的任务
				break

			expired_timer=self.heap.queue[0] #先不要出队列
			assert (isinstance(expired_timer,Timer))

			if expired_timer.canceled:
				# 如果到期的timer是一个被取消掉的,那么减少cancel_timer_count 计数
				# 弹堆
				self.heap.get()
				self.cancel_timer_count-=1
				continue

			# 执行method函数
			expired_timer._method(*expired_timer._args,**expired_timer._kwargs)
			self.heap.get()
			if expired_timer.repeatable and not expired_timer.canceled:
				# 如果是一个循环timer
				# 利用间隔时间去计算下一次到期时间,然后入堆
				expired_timer._expiration=time.time()+expired_timer._internal
				self.heap._put(expired_timer)



	@decorator.RunInLoop
	def remove_timer(self,timer_id):
		'''
		从堆中去除一个timer
		'''
		for timer in self.heap.queue:
			if timer.timer_id==timer_id:
				timer.canceled=True
				self.cancel_timer_count+=1
				break

		heap_size=self.heap.qsize()
		if heap_size >0 and self.cancel_timer_count*1.0/heap_size>0.25:
			self.rebuild_heap()


	def rebuild_heap(self):
		'''
		当被表识为cancel的timer数量很多时,重新建堆
		:return:
		'''
		import heapq
		tmp_timer_lst = []
		for timer in self.heap.queue:
			# 将没有被标识为cancel 的timer 添加到临时列表里
			if timer.canceled:
				continue
			tmp_timer_lst.append(timer)

		# 重新建堆,现在堆里没有被标识为cancel的元素了
		self.heap.queue = tmp_timer_lst
		heapq.heapify(self.heap.queue)
		self.cancel_timer_count = 0




if __name__ == '__main__':
	import time,loop,logger
	timer_queue=TimerQueue(loop.EventLoop(0.01,logger.Logger()))

	def test_func():
		print 'hello'

	def test_func1():
		print 'hello repeat'
	timer_ins=Timer(time.time()+2,2,test_func)
	print timer_ins.timer_id
	timer_ins1=Timer(time.time()+2,1,test_func1)
	print timer_ins1.timer_id
	timer_queue.add_timer(timer_ins)
	timer_queue.add_timer(timer_ins1)
	i=0
	while 1:
		timer_queue.schedule()
		time.sleep(1)
		i+=1
		if i==4:
			timer_queue.remove_timer(timer_ins1.timer_id)
	pass








