#encoding=utf8
import sys,threading
import time
# sys.path[0] 当前module 所在目录
sys.path.append(sys.path[0]+'/..') #将test包的父目录reactor加进来,这样才能引用到reactor中的组件


class EchoClient(object):
	def __init__(self, timeout,max_msg_count,msg,connect_num,dst_addr):
		import logger, tcp_client
		self.logger = logger.Logger()
		self.tcp_client = tcp_client.TcpClient(timeout, self.logger)
		self.tcp_client.set_app_data_callback(self.on_app_data)
		self.io_thread = threading.Thread(target=self.io_thread_func)
		self.io_thread.setDaemon(True)
		self.io_thread.start()


		self._max_msg_count=max_msg_count#接受消息数量的上限
		self._msg=msg
		self._connect_num=connect_num
		self._dst_addr=dst_addr

		self.start_time = 0#开始测试的时间
		self.end_time = 0  # 测试结束时间

		self.recv_bytes=0#接受到的字节
		self.recv_msg_count=0



	def io_thread_func(self):
		'''
		启动io线程
		'''
		self.tcp_client.run()



	def begin_test(self):
		for i in xrange(self._connect_num):
			self.tcp_client.connect(self._dst_addr)

		while len(self.tcp_client.tcpconnection_map)!=self._connect_num:
			#同步等待连接都建立完
			pass

		for conn_key,connection in self.tcp_client.tcpconnection_map.iteritems():
			#初始消息发送
			connection.send_data(self._msg)

		self.start_time=time.time()


		pass

	def on_app_data(self, tcp_connection, data):
		'''
		ping-pong
		'''
		self.recv_bytes+=len(data)
		self.recv_msg_count+=1
		if self.recv_msg_count==self._max_msg_count:
			#测试结束
			self.end_time=time.time()

			#关掉整个客户端
			self.tcp_client.close()

			# todo calc and print
			print 'done',self.end_time-self.start_time


		#echo
		tcp_connection.send_data(data)

if __name__ == '__main__':
	client_ins = EchoClient(0.0001,
							10000,
							"hello world",
							100,
							('127.0.0.1', 8080))  # 绑定服务器监听socket地址和poller的阻塞间隔


	client_ins.begin_test()

	while True:
		pass


