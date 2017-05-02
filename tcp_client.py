#encoding=utf8
class TcpClient(object):
	'''
	TCP 客户端
	'''
	def __init__(self,timeout):
		import connector,loop,logger
		self.logger=logger.Logger()
		self.loop=loop.EventLoop(timeout,self.logger)
		self.tcp_connection=None
		self.connector=connector.Connector(self.loop,self.logger)
		self.connector.set_new_connection_callback(self.new_connection)

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
		# 指定消息到来时的操作
		self.tcp_connection.set_message_callback(self.on_message)

		# 消息发送完的操作
		self.tcp_connection.set_write_complete_callback(self.write_complete)
		pass

	def on_message(self, tcp_connection,buffer):
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




