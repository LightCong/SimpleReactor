# encoding=utf8
class SelectPoller(object):
	'''
	基于select 的poller
	'''

	def __init__(self, logger):
		self.channel_map = {}  # fd:channel_ins
		self._logger = logger

	def poll(self, timeout):
		import select, error
		if not self.channel_map or len(self.channel_map) == 0:
			# 没有需要被关注的channel
			return

		rlist = []
		wlist = []
		xlist = []
		active_channel = []
		for channel_fd in self.channel_map:
			channel = self.channel_map[channel_fd]
			if channel.need_read:
				# 需要被监视读
				rlist.append(channel._fd)
				pass
			if channel.need_write:
				# 需要被监视写
				wlist.append(channel._fd)
				pass

			if channel.need_read or channel.need_write:
				# 需要被监视读或者写的描述符,都需要被检测是否异常
				xlist.append(channel._fd)
				pass
		# print rlist,wlist,xlist
		# 阻塞
		try:
			rlist, wlist, xlist = select.select(rlist, wlist, xlist, timeout)
		except select.error, err:
			if err.args[0] != error.EINTR:
				# poller error
				raise Exception()
			else:
				# 阻塞调用被信号打断
				return active_channel
		# 对于就绪的描述符,将其对应的channel ,放入到active_channel 中

		for rfd in rlist:
			channel_ins = self.channel_map[rfd]
			channel_ins.readable = True
			active_channel.append(channel_ins)

		for wfd in wlist:
			channel_ins = self.channel_map[wfd]
			channel_ins.writable = True
			active_channel.append(channel_ins)

		for efd in xlist:
			channel_ins = self.channel_map[efd]
			channel_ins.err = True
			active_channel.append(channel_ins)

		return active_channel

	def update_channel(self, channel):
		'''
		更新channel_map
		'''
		fd = channel._fd
		self.channel_map[fd] = channel

	def remove_channel(self, channel):
		'''
		将某个channel 从 channel_map 中删除
		'''
		if channel._fd in self.channel_map:
			return

		del self.channel_map[channel.fd]


if __name__ == '__main__':
	pass
