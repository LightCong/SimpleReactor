#encoding=utf8
import sys
# sys.path[0] 当前module 所在目录
sys.path.append(sys.path[0]+'/..') #将test包的父目录reactor加进来,这样才能引用到reactor中的组件
class EchoServer(object):

	def __init__(self,host_addr,timeout):
		import logger,tcp_server
		self.logger=logger.Logger()
		self.tcp_server=tcp_server.TcpServer(host_addr,timeout,self.logger)
		self.tcp_server.set_app_data_callback(self.on_app_data)


	def on_app_data(self, tcp_connection, data):
		'''
		ping pong 测试,收到数据就原样返回
		'''
		#print 'server recv:',data
		tcp_connection.send_data(data)
		pass

	def start(self):
		self.tcp_server.run()



if __name__ == '__main__':
	server_ins=EchoServer(('127.0.0.1',8080),timeout=0.0001)#绑定服务器监听socket地址和poller的阻塞间隔
	server_ins.start()

	while True:
		pass


