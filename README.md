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

	while True:
		pass

```

客户端示例：


```

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



