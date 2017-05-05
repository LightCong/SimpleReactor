#encoding=utf8
class TcpClient(object):
	'''
	TCP 客户端
	'''
	def __init__(self,timeout):
		import connector,loop,logger,system_service
		self.logger=logger.Logger()
		self.loop=loop.EventLoop(timeout,self.logger)
		self.tcp_connection=None
		self.connector=connector.Connector(self.loop,self.logger)
		self.connector.set_new_connection_callback(self.new_connection)

		# 系统服务中心
		self.system_service_center = system_service.SystemServiceCenter(self.logger, self.loop)
		# 心跳服务
		self.heartbeat_service = system_service.ClientHeartBeatService(self.logger,self.system_service_center,self)


	def connect(self,dst_addr):
		self.connector.connect(dst_addr)
		pass

	def run(self):
		self.loop._is_running = True
		self.loop.loop()

	def disconnect(self):
		if not self.tcp_connection:
			return
		self.tcp_connection.shutdown()

	def new_connection(self,conn_socket,peer_addr):
		# 在connect成功时被调用
		import tcp_connection,time
		host_addr=conn_socket.getsockname()
		conn_key = '{}#{}#{}'.format(str(host_addr), str(peer_addr), str(time.time()))
		self.tcp_connection=tcp_connection.TcpConnection(self.loop,conn_socket,conn_key,self.logger)
		# 指定连接断开时tcp server 的操作
		self.tcp_connection.set_close_callback(self.remove_connection)

		# 指定负载到来时的操作
		self.tcp_connection.set_payload_callback(self.on_payload)

		# 消息发送完的操作
		self.tcp_connection.set_write_complete_callback(self.write_complete)


		# 客户端连接成功以后,再进行心跳服务的注册
		self.heartbeat_service.register()
		pass


	def remove_connection(self, connection):
		# 注册为 tcp_connection 的回调函数
		self.tcp_connection=None
		pass


	def on_payload(self,tcp_connection,payload):
		'''
		处理负载消息,根据payload 的类型分别处理,
		如果是系统数据,则转去已注册的handler 去处理
		如果是应用层数据,则调用应用层数据的回调函数处理
		'''
		import payload_codec
		data_type, data = tcp_connection.payload_codec.get_data_from_payload(payload)
		if data_type in payload_codec.PayLoadCodec.PAYLOAD_SYS_LST:
			# 系统层数据处理
			self.system_service_center.data_handle(data_type,tcp_connection,data)

		elif data_type == payload_codec.PayLoadCodec.PAYLOAD_APP:
			# 应用层数据
			self.on_app_data(tcp_connection, data)

		else:
			# 数据格式出错
			self.logger.write_log('wrong format payload', 'error')


	def on_app_data(self,tcp_connection,payload):
		'''
		用户数据处理
		由继承类填写
		'''
		pass

	def write_complete(self):
		'''
		由继承类填写
		'''
		pass

if __name__ == '__main__':
	pass




