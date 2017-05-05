#encoding=utf8
import decorator
class SystemServiceCenter(object):
	'''
	系统服务类,用于处理心跳的系统服务
	'''
	def __init__(self,logger,loop):
		self.data_handler_map={}
		self._logger=logger
		self._loop=loop

	def register_message_handler(self,data_id,func):
		'''
		注册服务
		'''
		from payload_codec import PayLoadCodec
		if data_id in self.data_handler_map:
			self._logger.write_log('data_id %d has been registered'%data_id,'error')

		else:
			# 将data_id 注册到PayLoadCodec 里
			PayLoadCodec.PAYLOAD_SYS_LST.append(data_id)
			self.data_handler_map[data_id]=func

	def register_timer_handler(self,internal,func):
		'''
		增加一个每隔internal 时间执行的timer
		'''
		import timer,time
		tme=timer.Timer(time.time(),internal,func)
		self._loop.add_timer(tme)
		return tme.timer_id

	def remove_timer(self,timer_id):
		self._loop.remove_timer(timer_id)

	def data_handle(self,data_id,tcp_connection,data):
		'''
		系统消息事件的触发处理
		'''
		if not data_id in self.data_handler_map:
			self._logger.write_log('data_id %d not found' % data_id, 'error')

		else:
			self.data_handler_map[data_id](tcp_connection,data)

	

class ClientHeartBeatService(object):
	SERVICEID=2
	def __init__(self,logger,system_service_center,tcp_client):
		import time
		self._system_service_center=system_service_center
		self._tcp_client=tcp_client # 这里保存tcp_clent 引用,而不直接保存tcp_connection 的引用
		self.heartbeat_internal=1
		self._logger=logger
		self.last_recv = 0
		self.timer_id=-1
		pass

	def register(self):
		'''
		将定时任务和消息处理函数注册到服务中心里
		'''
		import time
		self.last_recv=time.time()
		self.timer_id=self._system_service_center.register_timer_handler(self.heartbeat_internal,self.check_heartbeat_recv)
		self._system_service_center.register_message_handler(ClientHeartBeatService.SERVICEID,self.heartbeat_recv_handler)

	def check_heartbeat_recv(self):
		from tcp_connection import TcpConnectionState
		import time

		if not self._tcp_client.tcp_connection or \
						self._tcp_client.tcp_connection.state!=TcpConnectionState.CONNECTED:
			#不是连接状态
			if self.timer_id!=-1:
				#已经被分配了定时任务,则删除定时任务
				self._system_service_center.remove_timer(self.timer_id)
				self.timer_id=-1
			self.last_recv=0
			pass

		elif time.time() - self.last_recv > 2 * self.heartbeat_internal:
			# 超时,关闭连接
			self._tcp_client.tcp_connection.shutdown()
			self.last_recv = 0



	def heartbeat_recv_handler(self, tcp_connection,heartbeat_data):
		'''
		心跳消息处理函数
		'''
		print heartbeat_data
		import time
		if self.check_heartbeat_data(tcp_connection,heartbeat_data):
			self.last_recv = time.time()

		else:
			# 心跳消息不正确
			self._logger.write_log('wrong heartbeat data','error')



	def check_heartbeat_data(self,tcp_connection,heartbeat_data):
		'''
		心跳消息验证
		'''
		#  心跳格式:src_host#dst_host#start_time
		if len(heartbeat_data.split('#'))==3:
			return True
		else:
			return False




class ServerHeartBeatService(object):
	SERVICEID=2
	def __init__(self,system_service_center,tcp_connection_map):
		self._system_service_center=system_service_center
		self.heartbeat_internal = 1
		self._tcp_connection_map=tcp_connection_map
		pass

	def register(self):
		'''
		将定时任务和消息处理函数注册到服务中心里
		'''
		self._system_service_center.register_timer_handler(self.heartbeat_internal,self.send_heartbeat)

	def send_heartbeat(self):
		'''
		定时对所有处于连接状态的连接发送心跳
		'''
		for item in self._tcp_connection_map.iteritems():
			conn_key=item[0]
			tcp_connection=item[1]
			tcp_connection.send_data(conn_key,ServerHeartBeatService.SERVICEID)
		pass



if __name__ == '__main__':
	pass

