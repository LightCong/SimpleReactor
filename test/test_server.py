import tcp_server
class TestServer(tcp_server.TcpServer):
	def on_message(self, tcp_connection, buffer):
		print buffer.get_all()
		tcp_connection.send("hello world")
		pass

	def write_complete(self):
		print 'server write done!'
		pass



server_ins=TestServer(('',8080),timeout=0.01)
server_ins.run()