# encoding=utf8
class TcpClient(object):
	'''
	TCP 客户端
	'''

	def __init__(self, timeout, logger):
		import connector, loop, system_service
		self._logger = logger
		self.loop = loop.EventLoop(timeout, self._logger)
		self.tcpconnection_map = {}  # 一个客户端也可以维持多个tcp连接
		self.connector = connector.Connector(self.loop, self._logger)
		self.connector.set_new_connection_callback(self.new_connection)

		# 系统服务中心
		self.system_service_center = system_service.SystemServiceCenter(self._logger, self.loop)

		self.app_data_callback = None

	def new_connection(self, conn_socket, peer_addr):
		# 在connect成功时被调用
		import tcp_connection, time
		host_addr = conn_socket.getsockname()
		conn_key = '{}#{}#{}'.format(str(host_addr), str(peer_addr), str(time.time()))
		connection = tcp_connection.TcpConnection(self.loop, conn_socket, conn_key, self._logger)
		# 指定连接断开时tcp server 的操作
		connection.set_close_callback(self.remove_connection)
		# 指定负载到来时的操作
		connection.set_payload_callback(self.on_payload)
		self.tcpconnection_map[conn_key] = connection

	def remove_connection(self, connection):
		# 注册为 tcp_connection 的回调函数
		import sys
		conn_key = connection._conn_key
		if not conn_key in self.tcpconnection_map:
			return
		del self.tcpconnection_map[conn_key]

	def on_payload(self, tcp_connection, payload):
		'''
		处理负载消息,根据payload 的类型分别处理,
		如果是系统数据,则转去已注册的handler 去处理
		如果是应用层数据,则调用应用层数据的回调函数处理
		'''
		import payload_codec
		data_type, data = tcp_connection.payload_codec.get_data_from_payload(payload)
		if data_type in payload_codec.PayLoadCodec.PAYLOAD_SYS_LST:
			# 系统层数据处理
			self.system_service_center.data_handle(data_type, tcp_connection, data)

		elif data_type == payload_codec.PayLoadCodec.PAYLOAD_APP and self.app_data_callback:
			# 应用层数据
			self.app_data_callback(tcp_connection, data)

		else:
			# 数据格式出错
			self._logger.write_log('wrong format payload', 'error')

	'''接口'''

	def run(self):
		'''
		客户端启动
		'''
		self.loop._is_running = True
		self.loop.loop()

	def connect(self, dst_addr):
		'''
		客户端连接
		'''
		import connector
		connector_ins=connector.Connector(self.loop,self._logger)
		connector_ins.set_new_connection_callback(self.new_connection)
		connector_ins.connect(dst_addr)


	def disconnect(self, conn_key):
		'''
		客户端断开某个连接
		'''
		if not conn_key in self.tcpconnection_map:
			return
		self.tcpconnection_map[conn_key].shutdown()

	def set_app_data_callback(self, method):
		'''
		设置消息事件回调函数
		'''
		self.app_data_callback = method

	def add_timer_task(self, internal, func, delay=0):
		'''
		增加定时器任务
		'''
		import timer, time
		tme = timer.Timer(time.time() + delay, internal, func)
		self.loop.add_timer(tme)
		return tme.timer_id

	def remove_timer(self, timer_id):
		'''
		删除定时器任务
		'''
		self.loop.remove_timer(timer_id)
		pass

	def send_data(self, conn_key, data):
		'''
		发送消息
		'''
		if not conn_key in self.tcpconnection_map:
			return

		self.tcpconnection_map[conn_key].send_data(data)

	def check_connected(self, conn_key):
		'''
		检测是否连接正常
		'''
		from tcp_connection import TcpConnectionState

		if conn_key in self.tcpconnection_map and \
						self.tcpconnection_map[conn_key].state == TcpConnectionState.CONNECTED:
			return True
		return False

	def use_heartbeat(self):
		import system_service
		# 心跳服务
		self.heartbeat_service = system_service.ClientHeartBeatService(self._logger, self.system_service_center, self)
		# 服务注册
		self.heartbeat_service.register()


	def close(self):
		self.loop._is_running = False
		for conn_key,connection in self.tcpconnection_map.iteritems():
			self.disconnect(conn_key)




if __name__ == '__main__':
	pass
