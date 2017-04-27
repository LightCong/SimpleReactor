#encoding=utf8
class PayLoadCodec(object):
	'''
	负责原始信息的加解密,压缩解压缩,以及加减length_header(用于处理tcp的粘包)
	'''
	MESSAGE_HEAD_LENGTH_FORMAT='<I'
	MESSAGE_HEAD_LENGTH_LEN=4
	def __init__(self):
		import compress,encrypt
		self._compressor=compress.Compressor()
		self._encryptor=None #暂时不启用

		pass


	def generate_wrap_message_with_payload(self,payload):
		'''
		对负载进行包装
		'''
		import struct
		if not payload:
			return None
		tmp_message=payload

		if self._compressor:
			# 如果指定了压缩套件
			tmp_message = self._compressor.compress(tmp_message)

		if self._encryptor:
			# 如果指定了加密套件
			tmp_message=self._encryptor.encrypt(tmp_message)


		message_len=len(tmp_message) #待传输消息的长度
		message_len_str=struct.pack(PayLoadCodec.MESSAGE_HEAD_LENGTH_FORMAT,message_len)
		message=message_len_str+tmp_message

		return message



	def get_payload_from_buffer(self,buffer):
		'''
		#从buffer中解析消息
		'''
		if not buffer:
			return

		import struct
		if buffer.size<PayLoadCodec.MESSAGE_HEAD_LENGTH_LEN:
			# 当前缓冲区的长度过小,长度头没有接收全
			return None

		message_len_str=buffer.read(PayLoadCodec.MESSAGE_HEAD_LENGTH_LEN)
		message_len=struct.unpack(PayLoadCodec.MESSAGE_HEAD_LENGTH_FORMAT,message_len_str)[0]

		if buffer.size<message_len:
			# 当前缓冲区的长度过小,message 没有接收全
			return None

		tmp_payload=buffer.read(message_len)

		if self._encryptor:
			# 如果指定了加密套件,则解密
			tmp_payload = self._encryptor.decrypt(tmp_payload)

		if self._compressor:
			# 如果指定了压缩套件,则解压缩
			tmp_payload = self._compressor.decompress(tmp_payload)

		payload=tmp_payload

		return payload


if __name__ == '__main__':
	payload="Almost all other scenarios will work; but if you ask a client to connect to multiple addresses, and at least one of them has no server at the end, the client will ultimately block. A client can, however, bind multiple addresses, and will dispatch requests to available workers. If you want to connect to multiple remote servers for high availability purposes, you insert something like HAProxy in the middle."
	payload='Wait, there is more! You can even mix "--bind" and "--connect". That means that your server will wait for requests on a given address, and connect as a worker on another. Likewise, you can specify "--connect" multiple times, so your worker will connect to multiple queues. If a queue is not running, it wons the magic of zeromq).'

	import buffer
	buffer_ins=buffer.Buffer()
	payload_codec=PayLoadCodec()


	message=payload_codec.generate_wrap_message_with_payload(payload)
	print message,len(message)

	buffer_ins.append(message)

	payload=payload_codec.get_payload_from_buffer(buffer_ins)

	print payload,len(payload)

	pass

