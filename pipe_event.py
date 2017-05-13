# encoding=utf8


class PipeEvent(object):
	'''
	将loop 从 poller 的阻塞态中唤醒,去执行别的线程通过主动接口发起的,在本io线程执行的操作
	'''

	def __init__(self, loop, logger):
		import os, channel
		self._loop = loop
		self._logger = logger
		self.rfd, self.wfd = os.pipe()
		self.pipe_channel = channel.Channel(self._loop, self.rfd)  # 将管道的读描述符放到loop.poller 里去监听

		self.chr = 'p'
		# 注册读事件
		self.pipe_channel.read_callback = self.handle_read
		self.pipe_channel.need_read = True

	def wake_up(self):
		'''
		向管道中写入一个字节
		'''
		import os
		os.write(self.wfd, self.chr)

	def handle_read(self):
		'''
		被channel 回调
		'''
		import os
		recv_chr = os.read(self.rfd, 1)


if __name__ == '__main__':
	import loop, timer, logger

	loop_ins = loop.EventLoop(0.01, logger.Logger())
	event_ins = PipeEvent(loop_ins, logger.Logger())
	timer_ins = timer.Timer(0, 1, event_ins.wake_up)
	loop_ins.add_timer(timer_ins)
	loop_ins._is_running = True
	loop_ins.loop()
