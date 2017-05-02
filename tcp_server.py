#encoding=utf8
class TcpServer(object):
	'''
	TCP 服务器类
	'''
	def __init__(self,host_addr,timeout):
		import acceptor,loop,logger
		self._host_addr=host_addr
		self.logger=logger.Logger() # 每个server一个logger
		self.loop=loop.EventLoop(timeout,self.logger)
		self.acceptor=acceptor.Acceptor(self.loop,host_addr,self.logger)
		self.tcpconnection_map={}

		self.acceptor.set_new_connection_callback(self.new_connection)


	def new_connection(self,conn_socket,peer_addr):
		# 注册为 acceptor 的回调函数
		# server 的acceptor 收到一个新连接请求
		import time,tcp_connection
		# 生成连接的名字 四元组+时间戳
		conn_key='{}#{}#{}'.format(str(self._host_addr),str(peer_addr),str(time.time()))
		connection=tcp_connection.TcpConnection(self.loop,conn_socket,conn_key,self.logger)
		# 指定连接断开时tcp server 的操作
		connection.set_close_callback(self.remove_connection)

		# 指定消息到来时的操作
		connection.set_message_callback(self.on_message)

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

	def on_message(self, tcp_connection, buffer):
		'''
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
