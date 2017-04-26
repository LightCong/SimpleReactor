import tcp_client
import threading

class Test(object):
	def __init__(self):
		self.tcp_client=None
		#self.mutex=threading.Lock()
		self.condition=threading.Condition()
		self.thread=threading.Thread(target=self.thread_start)
		self.thread.setDaemon(True)
		self.thread.start()

	def thread_start(self):
		with self.condition:
			self.tcp_client=tcp_client.TcpClient(0.01)
			self.tcp_client.connect(('127.0.0.1',8080))
			self.condition.notify()

		self.tcp_client.run()

	def run(self):
		with self.condition:
			while not self.tcp_client:
				self.condition.wait()

		while not self.tcp_client.tcp_connection:
			pass

		i=0
		while i<100:
			self.tcp_client.tcp_connection.send(str(i))
			i+=1

		while 1:
			pass
		pass



if __name__ == '__main__':
	t=Test()
	t.run()