#encoding=utf8

import socket
class Socket(object):
	def __init__(self,conn_socket=None):
		if conn_socket:
			self.sock=conn_socket
		else:
			self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 地址复用,解决因为tcp time_wait 导致的服务器监听无法快速重启
		self.sock.setsockopt(socket.SOL_SOCKET,socket.SO_KEEPALIVE,0) #停止tcp 保活,因为要在上层做心跳
		self.sock.setblocking(0) #非阻塞
		self.sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,0) #关闭tcp nagle 机制,提高实时性

	def change_to_listen_socket(self,host_addr):
		self.sock.bind(host_addr)
		self.sock.listen(socket.SOMAXCONN) # 监听队列的最大长度,这是系统独立的

	def change_to_client_socket(self):
		pass


	@property
	def fd(self):
		return self.sock.fileno()



	def recv(self,buffer_size):
		#返回接受的数据,以及是否连接关闭
		import socket,error
		if_close=False
		try:
			recv_data=self.sock.recv(buffer_size)
			if not recv_data:
				# a closed connection is indicated by signaling
				# a read condition, and having recv() return 0.
				if_close=True
				return '',if_close
			else:
				return recv_data,if_close

		except socket.error,err:
			if err.args[0] in error._SHOULDCONTINUE:
				return '',if_close
			elif err.args[0] in error._DISCONNECTED:
				if_close=True
				return '',if_close
			else:
				# TODO 输出错误日志
				raise


	def send(self,data):
		#返回发送数据的长度,以及连接是否关闭
		import socket,error
		if_close=False
		try:
			sent_count=self.sock.send(data)
			return sent_count,if_close

		except socket.error,err:
			if err.args[0] in error._SHOULDCONTINUE:
				return 0,if_close
			elif err.args[0] in error._DISCONNECTED:
				if_close=True
				return 0,if_close
			else:
				# TODO 输出错误日志
				raise




	def close(self):
		import socket,error
		try:
			self.sock.shutdown(socket.SHUT_RDWR)
		except socket.error,err:
			if err.args[0] in (error.ENOTCONN, error.EBADF):
				# error.ENOTCONN: 关闭一个已经被关闭了的连接
				# error.EBADF: 描述符失效
				return
			else:
				# TODO 输出错误日志
				raise


	def connect(self,dst_addr):
		'''
		客户端socket 的connect 操作
		'''
		import error,os
		from connector import ConnectorState as ConnectorState
		ret=self.sock.connect_ex(dst_addr)
		ret_state=None
		if ret in error._CONNECTING:
			# 正在建立连接
			ret_state=ConnectorState.CONNECTING
			return ret_state

		elif ret == error.EINVAL and os.name in ('nt', 'ce'):
			# 正在建立连接
			ret_state = ConnectorState.CONNECTING
			return ret_state

		elif ret in(0,error.EISCONN):
			# 连接直接建立了
			ret_state=ConnectorState.CONNECTED
			return ret_state
			pass

		else:
			# 连接出现错误
			ret_state=ConnectorState.ERROR
			# TODO 输出错误日志
			raise


	def accept(self):
		'''
		服务端监听socket 的accept 操作
		'''
		import socket,error
		conn_socket=None
		peer_host=None
		try:
			conn_socket, peer_host = self.sock.accept()
			return conn_socket,peer_host
		except socket.error,err:
			if err.args[0] in error._SHOULDCONTINUE:
				return None,None
			elif err.args[0] == error.ECONNABORTED:
				# ECONNABORTED : 客户端发送了rst
				return None,None
			else:
				#TODO 输出错误日志
				raise


	def get_peer_name(self):
		if_success=True
		try:
			peer_name=self.sock.getpeername()
			return peer_name,if_success
		except socket.error,err:
			if_success=False
			# TODO 输出错误日志
			return None,if_success




if __name__ == '__main__':
	a=Socket()
	print socket.SOMAXCONN





