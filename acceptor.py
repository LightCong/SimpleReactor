# encoding=utf8
class Acceptor(object):
	'''
	用于对监听socket 执行 accept,并创建一个新的tcp_connection
	'''

	def __init__(self, loop, host_addr, logger):
		import simple_socket, channel
		self._loop = loop
		self._logger = logger
		self.socket = simple_socket.Socket(self._logger)
		self.socket.change_to_listen_socket(host_addr)
		self.accept_channel = channel.Channel(loop, self.socket.fd)
		self.new_connection_callback = None

		self.accept_channel.set_read_callback(self.handle_read)  # 将handle_read 注册为所属channel 的read_callback
		self.accept_channel.need_read = True

		self.accept_channel.set_error_callback(self.handle_error)
		pass

	def set_new_connection_callback(self, method):
		# 由tcp server 设置,让tcp server 在连接建立时执行相应逻辑
		self.new_connection_callback = method

	def handle_read(self):
		'''
		接受一个新连接,建立一个channel 并且调用loop->update(channel)
		'''
		conn_socket = None
		peer_host = None
		conn_socket, peer_host = self.socket.accept()

		if self.new_connection_callback and conn_socket != None and peer_host != None:
			# 上层tcp_server 会注册这个回调,创建一个新的tcpconnection
			self.new_connection_callback(conn_socket, peer_host)

	def handle_error(self):
		# 注册为channel 的回调
		log_message = "acceptor error while fd is listened by poller"
		self._logger.write_log(log_message, 'error')


if __name__ == '__main__':
	import logger

	a = Acceptor(None, ('', 8080), logger.Logger())
