# SimpleReactor

## 简介

SimpleReactor一个用python编写的基于reactor 模型的tcp双端通讯框架。
在架构设计上参考了陈硕的muduo库架构。
在异常处理方面参考了python 的asyncore 的处理。

## 特点介绍

- SimpleReactor 无论在客户端还是服务端都会独占一个io线程
，并基于事件驱动运行。因此建议将SimpleReactor放在单独的io线程里运行。

- SimpleReactor 的send，shutdown 等主动接口对于跨线程调用是安全的，其真正执行的时机会发生在io线程执行时。因此当需要向网络上发送消息时，无论实在io线程里，还是在逻辑执行线程中都可以直接调用发送接口。

- SimpleReactor 对于消息接受的处理执行是基于事件驱动的。
用户可以通过覆写onmessage函数定义接受到消息时需要采用的操作。


## 使用教程

服务端示例：

```
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
```

客户端示例：


```

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
```


## 服务端架构简介

撰写中。。。


## 客户端结构简介

撰写中。。。

## TODO List

1. logger接入
2. 异常行为处理完善
3. 增加更多对外接口
4. 增加对 epoll，kqueue 等不同平台下高性能poller的支持
5. 处理tcp粘包
6. 传输信息的压缩解压缩
7. 压力测试

    # SimpleReactor
基于reactor 模型的双端通讯框架
