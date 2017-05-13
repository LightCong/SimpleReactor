# encoding=utf8

class Channel(object):
	def __init__(self, loop, fd):
		self._loop = loop
		self._fd = fd
		self.need_write = False  # 需要被检测读
		self.need_read = False  # 需要被检测写
		self.accept = False  # 是否是listen_socket

		self.readable = False  # 是否有读事件
		self.writable = False  # 是否有写事件
		self.err = False  # 描述符被poller检测时,是否出错

		self.read_callback = None
		self.write_callback = None
		self.error_callback = None

		# 生成一个channel 实例,就把自己放入到loop.poller 的map中
		self._loop.update_channel(self)

	def disable_all(self):
		# 停止当前channel 的所有监听活动
		self.need_read = False
		self.need_write = False
		self.accept = False
		pass

	def close(self):
		# 将当前channel 从loop.poller 的map中去掉
		self._loop.remove_channel(self)

	def set_read_callback(self, method):
		self.read_callback = method

	def set_write_callback(self, method):
		self.write_callback = method

	def set_error_callback(self, method):
		self.error_callback = method

	def handle_event(self):
		if self.readable and self.read_callback:
			self.read_callback()

		if self.writable and self.write_callback:
			self.write_callback()

		if self.error_callback and self.err:
			self.error_callback()
