#encoding=utf8
import threading
import sys
sys.path.append(sys.path[0]+'/..')
import tcp_client

class TestClient(tcp_client.TcpClient):
	'''
	继承TcpClient 类
	'''
	def on_message(self, tcp_connection, buffer):
		'''
		定义连接接收到消息时的操作
		'''
		print buffer.get_all()
		pass

	def write_complete(self):
		'''
		定义消息发送完毕以后的操作
		'''
		print 'client write done!'
		pass


class Test(object):
	def __init__(self):
		self.tcp_client = None
		# self.mutex=threading.Lock()
		self.condition = threading.Condition()
		self.thread = threading.Thread(target=self.thread_start)
		self.thread.setDaemon(True)
		self.thread.start()

	def thread_start(self):
		'''
		在io 线程,启动tcp_client
		'''
		with self.condition:
			self.tcp_client = TestClient(0.01)
			self.tcp_client.connect(('127.0.0.1', 8080))
			self.condition.notify()
		self.tcp_client.run()

	def run(self):
		'''
		在主线程调用send接口
		'''
		with self.condition:
			while not self.tcp_client:
				self.condition.wait()

		while not self.tcp_client.tcp_connection:
			pass

		i = 0
		while i < 100:
			self.tcp_client.tcp_connection.send(str(i)) #跨线程调用安全
			i += 1

		while 1:
			pass

if __name__ == '__main__':
	t=Test()
	t.run()