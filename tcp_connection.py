#encoding=utf8

import decorator
class TcpConnectionState(object):
	'''
	TcpConnection 的状态(已经连接上,正在断开连接,连接断开)
	'''
	CONNECTED=0
	DISCONNECTING=1
	DISCONNECTED=2



class TcpConnection(object):
	'''
	每个客户端连接,对应一个tcp connection
	'''

	def __init__(self,loop,conn_socket,conn_key):
		import simple_socket,channel,buffer

		self._loop=loop
		self._conn_key=conn_key
		self.socket=simple_socket.Socket(conn_socket)

		self.channel=channel.Channel(self._loop,self.socket.fd)
		self.channel.set_read_callback(self.handle_read)
		self.channel.need_read=True
		self.channel.set_write_callback(self.handle_write)
		# 由于poller,采取水平触发,所以不能一直设定channel可写.否则造成busy loop
		self.channel.need_write=False

		self.channel.set_error_callback(self.handle_error)


		self.read_buffer = buffer.Buffer()
		self.output_buffer=buffer.Buffer()

		self.state = TcpConnectionState.CONNECTED

		self.close_callback = None
		self.message_callback = None
		self.write_complete_callback=None

	@decorator.RunInLoop
	def send(self,data):
		# 不同于read,发送信息,是在tcpconnection中的一个主动调用接口
		sent_count,if_close=self.socket.send(data)
		if if_close:
			self.handle_close()

		if sent_count<len(data):
			# 剩余内容要入output_buffer
			self.output_buffer.append(data[sent_count:])
			self.channel.need_write=True

		elif sent_count==len(data) and self.write_complete_callback:
			# 一次发送完毕
			self.write_complete_callback()

		pass

	@decorator.RunInLoop
	def shutdown(self):
		# tcpconnection 的主动关闭
		if self.state!=TcpConnectionState.CONNECTED:
			return

		if self.channel.need_write:
			# 还有内容没有写完
			self.state=TcpConnectionState.DISCONNECTING
		else:
			self.handle_close()
			self.state=TcpConnectionState.DISCONNECTED
		pass

	def handle_read(self):
		# 注册为channel 里的回调
		recv_data, if_close = self.socket.recv(65535)
		if if_close:
			self.handle_close()

		# 接受到的内容,放到buffer里
		self.read_buffer.append(recv_data)

		if self.message_callback:
			self.message_callback(self,self.read_buffer)


	def handle_write(self):
		# 当channel.need_write ==True 时会被调用
		import buffer
		assert(isinstance(self.output_buffer,buffer.Buffer))
		sent_data=self.output_buffer.get_all() # 这是还没有移动read_index
		sent_count, if_close = self.socket.send(sent_data)
		if if_close:
			self.handle_close()
		if sent_count==len(sent_data):
			# 缓冲区发送干净了
			self.channel.need_write=False # 数据发送完了,就要关闭channel的写监听,防止
			self.output_buffer.add_read_index(sent_count) # 调整read_index


			if self.write_complete_callback:
				self.write_complete_callback()

			if self.state==TcpConnectionState.DISCONNECTING:
				# 连接已经被下达了主动关闭的指令
				self.handle_close()
				self.state = TcpConnectionState.DISCONNECTED

		else:
			self.output_buffer.add_read_index(sent_count) # 调整read_index


	def handle_error(self):
		# 注册为channel 的回调
		#todo 输出出错信息
		pass


	def handle_close(self):
		# 关闭channel 的全部监听
		self.channel.disable_all()

		# socket 的关闭
		self.socket.close()

		# 执行close_callback 将tcp_connection 从map中去除
		if self.close_callback:
			self.close_callback(self)
		# 执行channel.close,将channel 从 poller.channel_map 中去掉
		self.channel.close()
		pass

	def set_close_callback(self, method):
		# 由tcp_server 去指定在连接断开时,应该执行的操作
		# 具体操作如:从connection_map 中清除 tcp_connection
		self.close_callback = method

	def set_message_callback(self, method):
		self.message_callback = method


	def set_write_complete_callback(self,method):
		self.write_complete_callback=method
		pass




