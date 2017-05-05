#encoding=utf8
class TcpServer(object):
	'''
	TCP 服务器类
	'''
	def __init__(self,host_addr,timeout):
		import acceptor,loop,logger,system_service
		self._host_addr=host_addr
		self.logger=logger.Logger() # 每个server一个logger
		self.loop=loop.EventLoop(timeout,self.logger)
		self.acceptor=acceptor.Acceptor(self.loop,host_addr,self.logger)
		self.tcpconnection_map={}
		self.acceptor.set_new_connection_callback(self.new_connection)

		# 系统服务中心
		self.system_service_center=system_service.SystemServiceCenter(self.logger,self.loop)
		# 心跳服务
		self.heartbeat_service=system_service.ServerHeartBeatService(self.system_service_center,self.tcpconnection_map)
		# 服务注册
		self.heartbeat_service.register()


	def new_connection(self,conn_socket,peer_addr):
		# 注册为 acceptor 的回调函数
		# server 的acceptor 收到一个新连接请求
		import time,tcp_connection
		# 生成连接的名字 四元组+时间戳
		conn_key='{}#{}#{}'.format(str(self._host_addr),str(peer_addr),str(time.time()))
		connection=tcp_connection.TcpConnection(self.loop,conn_socket,conn_key,self.logger)
		# 指定连接断开时tcp server 的操作
		connection.set_close_callback(self.remove_connection)

		# 指定负载到来时的操作
		connection.set_payload_callback(self.on_payload)

		# 消息发送完的操作
		connection.set_write_complete_callback(self.write_complete)

		self.tcpconnection_map[conn_key]=connection
		pass

	def remove_connection(self,connection):
		# 注册为 tcp_connection 的回调函数
		conn_key=connection._conn_key
		if not conn_key in self.tcpconnection_map:
			return
		del self.tcpconnection_map[conn_key]

	def run(self):
		self.loop._is_running=True
		self.loop.loop()

	def on_message(self, tcp_connection, payload):
		'''
		由继承类填写
		'''
		pass



	def on_payload(self, tcp_connection, payload):
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
			self.logger.write_log('wrong format payload','error')


	def on_app_data(self, tcp_connection, payload):
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
