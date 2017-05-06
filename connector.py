#encoding=utf8
import decorator
class ConnectorState(object):
	'''
	执行非阻塞connect 过程中 的状态
	'''
	CONNECTED=0
	CONNECTING=1
	ERROR=2


class Connector(object):
	'''
	连接器
	'''
	def __init__(self,loop,logger):
		import simple_socket, channel
		self._loop = loop
		self._logger=logger
		self.socket = simple_socket.Socket(self._logger)
		self.connect_channel=channel.Channel(loop,self.socket.fd)
		self.connect_channel.set_write_callback(self.handle_write)

		self.connect_channel.set_error_callback(self.handle_error)


		self.new_connection_callback=None # 由tcp_client 注册,在连接建立成功时调用


	@decorator.RunInLoop
	def connect(self,dst_addr):
		'''
		客户端连接的主动接口
		'''
		connect_state=self.socket.connect(dst_addr)
		if connect_state ==ConnectorState.CONNECTING:
			# 连接正在建立
			# 通过底层poller 去监控socket 对应的描述符是否可写
			self.connect_channel.need_write=True
			pass

		elif connect_state==ConnectorState.CONNECTED:
			# 连接建立完成
			self.new_connection_callback(self.socket)
			pass

		else:
			#连接建立失败
			log_message='connect failed'
			self._logger.write_log(log_message,'error')
			pass


	def handle_write(self):
		#(1) 如果连接建立好了，对方没有数据到达，那么 sockfd 是可写的
		#(2) 如果在 select 之前，连接就建立好了，而且对方的数据已到达，那么 sockfd 是可读和可写的。
		#(3) 如果连接发生错误，sockfd 也是可读和可写的。


		# 在任何平台下,这里只要能成功获得对端host,则说明连接成功建立了
		peer_addr,if_success=self.socket.get_peer_name()
		if if_success:
			# 关闭channel 的全部监听
			self.connect_channel.disable_all()
			# 执行channel.close,将channel 从 poller.channel_map 中去掉
			self.connect_channel.close()
			self.new_connection_callback(self.socket.sock,peer_addr)

		else:
			# 连接建立失败了
			log_message = "connect failed"
			self._logger.write_log(log_message, 'error')
			# todo 重新连接?



	def handle_error(self):
		# 注册为channel 的回调
		log_message = "connector error while fd is listened by poller"
		self._logger.write_log(log_message, 'error')

	def set_new_connection_callback(self,method):
		self.new_connection_callback=method