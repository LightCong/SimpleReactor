# SimpleReactor
基于reactor 模型的双端通讯框架

## 简介

SimpleReactor一个用python编写的基于reactor 模型的tcp双端通讯框架。
在架构设计上参考了陈硕的muduo库架构。
在异常处理方面参考了python 的asyncore 的处理。

## 特点介绍

- SimpleReactor 无论在客户端还是服务端都会独占一个io线程
，并基于事件驱动运行。因此建议将SimpleReactor放在单独的io线程里运行。

- SimpleReactor 的send，shutdown 等主动接口对于跨线程调用是安全的，其真正执行的时机会发生在io线程执行时。因此当需要向网络上发送消息时，无论实在io线程里，还是在逻辑执行线程中都可以直接调用发送接口。

- SimpleReactor 对于消息接受的处理执行是基于事件驱动的。
用户可以通过覆写on_app_data函数定义接受到消息时需要采用的操作。


## 使用教程

服务端示例：

```
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




```

客户端示例：


```
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
	client_ins = EchoClient(0.0001,10000,"hello world",100,('127.0.0.1', 8080))  # 绑定服务器监听socket地址和poller的阻塞间隔
	client_ins.begin_test()

	while True:
		pass



```


## 服务端架构简介

![tcp_server](https://github.com/LightCong/SimpleReactor/blob/master/pic/reactor_server.png)


## 客户端结构简介

![tcp_client](https://github.com/LightCong/SimpleReactor/blob/master/pic/reactor_client.png)

## TODO List




4. 增加对 epoll 等不同平台下高性能poller的支持
 
6. 压力测试


## Done List
1. logger接入
5. 传输信息的压缩解压缩 
2. 异常行为处理完善
7. 心跳服务
3. 增加更多对外接口
4. 增加kqueue支持



