#encoding=utf8
import tcp_server
class TestServer(tcp_server.TcpServer):
	'''
	继承TcpServer类
	'''
	def on_message(self, tcp_connection, buffer):
		'''
		定义连接接收到消息时的操作
		'''
		tcp_connection.send("hello world")
		pass

	def write_complete(self):
		'''
		定义消息发送完毕以后的操作
		'''
		print 'server write done!'
		pass


if __name__ == '__main__':
	server_ins=TestServer(('',8080),timeout=0.01)#绑定服务器监听socket地址和poller的阻塞间隔
	server_ins.run()# 启动服务器