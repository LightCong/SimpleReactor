#encoding=utf8
import sys,threading
sys.path.append(sys.path[0]+'/..')
class TestServer(object):

	'''
	继承TcpServer类
	'''
	def __init__(self,host_addr,timeout):
		import logger,tcp_server
		self.logger=logger.Logger()
		self.tcp_server=tcp_server.TcpServer(host_addr,timeout,self.logger)
		self.tcp_server.set_app_data_callback(self.on_app_data)
		self.io_thread = threading.Thread(target=self.io_thread_func)
		self.io_thread.setDaemon(True)
		self.condition=threading.Condition()
		self.mutex=threading.Lock()
		self.ready=False



	def io_thread_func(self):
		#开启服务器
		self.tcp_server.run()


	def on_app_data(self, tcp_connection, data):
		'''
		定义连接接收到消息时的操作
		'''
		print 'server recv:',data
		tcp_connection.send_data("hello world")
		pass

	def start(self):
		self.io_thread.start()
		#self.tcp_server.run()



if __name__ == '__main__':
	server_ins=TestServer(('127.0.0.1',8080),timeout=0.01)#绑定服务器监听socket地址和poller的阻塞间隔
	server_ins.start()
	#while True:
		#print threading.activeCount()
	#	pass
	while True:
		pass
		#print server_ins.io_thread.is_alive()


