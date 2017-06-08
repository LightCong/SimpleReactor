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
		if not channel:
			return
		fd = channel._fd
		self.channel_map[fd] = channel

	def remove_channel(self, channel):
		'''
		将某个channel 从 channel_map 中删除
		'''
		if not channel:
			return
		if not channel._fd in self.channel_map:
			return

		del self.channel_map[channel._fd]


class KqueuePoller(object):
	'''
	基于kqueue 的poller
	'''

	def __init__(self, logger):
		import select
		self.channel_map = {}
		self.channel_count = 0
		self._logger = logger
		self.kq = select.kqueue()

	def poll(self, timeout):
		active_channel = []
		import select, error
		try:
			re_kevent_lst = self.kq.control(None, 2 * self.channel_count, timeout)  # 读写分开添加
		except select.error, err:
			if err.args[0] != error.EINTR:
				# poller error
				raise Exception()
			else:
				# 阻塞调用被信号打断
				return active_channel

		for kevent in re_kevent_lst:
			if kevent.filter == select.KQ_FILTER_READ:
				# 可读
				channel_fd = kevent.ident
				channel_ins = self.channel_map[channel_fd]
				channel_ins.readable = True
				active_channel.append(channel_ins)

			if kevent.filter == select.KQ_FILTER_WRITE:
				# 可写
				channel_fd = kevent.ident
				channel_ins = self.channel_map[channel_fd]
				channel_ins.writable = True
				active_channel.append(channel_ins)

		return active_channel

	def update_channel(self, channel):
		'''
		更新channel_map,同时也要更新kevent_lst
		'''
		import select
		if not channel:
			return
		fd = channel._fd

		if not fd in self.channel_map:
			# 第一次添加,而不是修改
			self.channel_count += 1

		self.channel_map[fd] = channel

		change_event_lst = []
		# 读监听与写监听,要添加两次

		if channel.need_read == True:
			# 增加读监听,重复增加不会有影响
			kevent = select.kevent(channel._fd, filter=select.KQ_FILTER_READ,
								   flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE)
			change_event_lst.append(kevent)
		else:
			# 删除读监听
			kevent = select.kevent(channel._fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_DELETE)
			change_event_lst.append(kevent)

		if channel.need_write == True:
			# 增加写监听,重复增加不会有影响
			kevent = select.kevent(channel._fd, filter=select.KQ_FILTER_WRITE,
								   flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE)
			change_event_lst.append(kevent)
			pass

		else:
			# 删除写监听
			kevent = select.kevent(channel._fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_DELETE)
			change_event_lst.append(kevent)

		try:
			self.kq.control(change_event_lst, len(change_event_lst), 0)
		except select.error, err:
			# 修改kqueue失败
			raise Exception()

	def remove_channel(self, channel):
		'''
		将某个channel 从channel_map 中删除
		同时也要更新kevent_lst
		'''
		import select
		if not channel:
			return

		if not channel._fd in self.channel_map:
			return

		del self.channel_map[channel._fd]
		self.channel_count = self.channel_count - 1

		# 删除读写监听
		change_event_lst = []
		kevent = select.kevent(channel._fd, filter=select.KQ_FILTER_WRITE, flags=select.KQ_EV_DELETE)
		change_event_lst.append(kevent)

		kevent = select.kevent(channel._fd, filter=select.KQ_FILTER_READ, flags=select.KQ_EV_DELETE)
		change_event_lst.append(kevent)

		try:
			self.kq.control(change_event_lst, len(change_event_lst), 0)
		except select.error, err:
			# 修改kqueue失败
			raise Exception()


# todo 测试epoller
'''
class  EpollPoller(object):
	#基于epoll的poller
	def __init__(self,logger):
		import select
		self.channel_map={}
		self.channel_count=0
		self._logger=logger
		self.epoller=select.epoll()

	def poll(self,timeout):
		active_channel = []
		import select, error
		try:
			re_event_lst = self.epoller.poll(timeout,self.channel_count)
		except select.error, err:
			if err.args[0] != error.EINTR:
				# poller error
				raise Exception()
			else:
				# 阻塞调用被信号打断
				return active_channel


		for fd,event in re_event_lst:
			#可读
			if event&(select.EPOLLIN|select.EPOLLPRI):
				channel_ins = self.channel_map[fd]
				channel_ins.readable = True
				active_channel.append(channel_ins)
			#可写
			if event&select.EPOLLOUT:
				channel_ins = self.channel_map[fd]
				channel_ins.readable = True
				active_channel.append(channel_ins)
			#异常
			if event&(select.POLLHUP | select.EPOLLERR | select.EPOLLNVAL):
				channel_ins = self.channel_map[fd]
				channel_ins.err = True
				active_channel.append(channel_ins)


		return active_channel




	def update_channel(self,channel):
		#更新channel_map,同时也要更新监听列表
		import select
		if not channel:
			return
		fd = channel._fd

		event_task=0
		#设置时间监听选项
		if channel.need_read == True:
			event_task=event_task|(select.EPOLLIN|select.EPOLLPRI)

		if channel.need_write == True:
			event_task=event_task|select.EPOLLOUT


		if not fd in self.channel_map:
			# 第一次添加,而不是修改
			self.channel_count += 1
			self.epoller.register(fd,event_task)
		else:
			#修改
			self.epoller.modify(fd,event_task)

		self.channel_map[fd] = channel

		pass


	def remove_channel(self,channel):
		#将某个channel 从channel_map 中删除
		#同时也要更新监听列表

		if not channel:
			return

		if not channel._fd in self.channel_map:
			return

		del self.channel_map[channel._fd]
		self.channel_count = self.channel_count - 1

		#更新列表
		self.epoller.unregister(channel._fd)

'''
poller = KqueuePoller

if __name__ == '__main__':
	pass
