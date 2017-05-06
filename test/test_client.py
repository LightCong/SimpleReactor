#encoding=utf8
import threading
import sys
import time
sys.path.append(sys.path[0]+'/..')
import tcp_client

class TestClient(object):
	def __init__(self,timeout):
		import logger,tcp_client
		self.logger=logger.Logger()
		self.tcp_client=tcp_client.TcpClient(timeout,self.logger)
		self.tcp_client.set_app_data_callback(self.on_app_data)
		self.condition = threading.Condition()
		self.io_thread = threading.Thread(target=self.io_thread_func)
		self.io_thread.setDaemon(True)
		self.io_thread.start()
		self.c=0
		self.start_time=0


	def io_thread_func(self):
		self.tcp_client.run()


	def run(self):
		'''
		在主线程调用send接口
		'''
		self.tcp_client.connect(('127.0.0.1', 8080))
		while not self.tcp_client.tcp_connection:
			pass
		self.start_time=time.time()
		i = 0
		while i < 100000:
			if self.tcp_client.tcp_connection:
				self.tcp_client.tcp_connection.send_data(str(i))  # 跨线程调用安全
			i += 1


		while True:
			pass

	def on_app_data(self, tcp_connection, data):
		'''
		定义连接接收到消息时的操作
		'''
		print 'client recv :',data,self.c
		self.c+=1
		if self.c==9999:
			print time.time()-self.start_time

		pass

if __name__ == '__main__':
	t=TestClient(0.01)
	t.run()