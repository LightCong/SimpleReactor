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
	def __init__(self,loop,conn_socket,conn_key,logger):
		import simple_socket,channel,buffer,message_codec,payload_codec,time
		self._logger=logger
		self._loop=loop
		self._conn_key=conn_key
		self.socket=simple_socket.Socket(self._logger,conn_socket)

		self.message_codec=message_codec.MessageCodec()#处理tcp粘包,压缩/解压缩,加密/解密
		self.payload_codec = payload_codec.PayLoadCodec()  # payload 与data 之间的转换

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
		self.payload_callback = None

		self.last_recv_time=time.time()

	import payload_codec

	def send_data(self,data,tpe=payload_codec.PayLoadCodec.PAYLOAD_APP):
		'''
		tcp_connection 的send_data 接口负责从payload 层向下处理
		'''
		payload=self.payload_codec.generate_payload_with_data(data,tpe)
		self.send(payload)

	def send(self,payload):
		'''
		tcp_connection 的send 接口负责从payload 层向下处理
		'''
		if self.state != TcpConnectionState.CONNECTED:
			log_message='tcp connection has been closed'
			self._logger.write_log(log_message,'info')
			return

		# 不同于read,发送信息,是在tcpconnection中的一个主动调用接口
		message=self.message_codec.generate_message_with_payload(payload)
		if not message:
			return

		sent_count,if_close=self.socket.send(message)
		if if_close:
			self.handle_close()
		if sent_count<len(message):
			# 剩余内容要入output_buffer
			self.send_in_loop(message[sent_count:])


	@decorator.RunInLoop
	def send_in_loop(self,piece):
		self.output_buffer.append(piece)
		self.channel.need_write = True


	@decorator.RunInLoop
	def shutdown(self):
		# tcpconnection 的主动关闭
		if self.state!=TcpConnectionState.CONNECTED:
			log_message = 'tcp connection has been closed'
			self._logger.write_log(log_message, 'info')
			return

		if self.channel.need_write:
			# 还有内容没有写完
			self.state=TcpConnectionState.DISCONNECTING
		else:
			self.handle_close()


	def handle_read(self):
		# 注册为channel 里的回调
		import time
		recv_fragment, if_close = self.socket.recv(65535*100)
		if if_close:
			self.handle_close()
			return
		# 接受到的内容,放到buffer里
		self.read_buffer.append(recv_fragment)
		while True:
			'''
			收到的数据,每一个报文都要处理完
			'''
			payload=self.message_codec.get_payload_from_buffer(self.read_buffer)
			if not payload:
				break
			self.last_recv_time = time.time() #以每次收到一个 payload
			if self.payload_callback:
				self.payload_callback(self,payload)


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

			if self.state==TcpConnectionState.DISCONNECTING:
				# 连接已经被下达了主动关闭的指令
				self.handle_close()
		else:
			self.output_buffer.add_read_index(sent_count) # 调整read_index


	def handle_error(self):
		# 注册为channel 的回调
		log_message="connection error while fd is listened by poller"
		self._logger.write_log(log_message,'error')
		self.handle_close()
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
		self.state = TcpConnectionState.DISCONNECTED
		pass

	def set_close_callback(self, method):
		# 由tcp_server 去指定在连接断开时,应该执行的操作
		# 具体操作如:从connection_map 中清除 tcp_connection
		self.close_callback = method

	def set_payload_callback(self, method):
		self.payload_callback = method






