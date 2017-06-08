# encoding=utf8
class MessageCodec(object):
	'''
	报文,头部指示了整个报文的长度
	'''
	MESSAGE_LENGTH_FORMAT = '<I'
	MESSAGE_LENGTH_LEN = 4

	def __init__(self, if_comress=True, if_encrypt=False):
		import compress, encrypt
		self._compressor = compress.Compressor()
		self._encryptor = encrypt.Encrptor()
		self._if_compress = if_comress
		self._if_encrypt = if_encrypt

	def generate_message_with_payload(self, payload):
		'''
		对负载进行包装,生成完整的报文
		'''
		import struct
		if not payload:
			return None
		tmp_message = payload

		if self._compressor and self._if_compress:
			# 如果指定压缩
			tmp_message = self._compressor.compress(tmp_message)

		if self._encryptor and self._if_encrypt:
			# 如果指定加密
			tmp_message = self._encryptor.encrypt(tmp_message)

		message_len = len(tmp_message)  # 待传输消息的长度
		message_len_bytes = struct.pack(MessageCodec.MESSAGE_LENGTH_FORMAT, message_len)
		message = message_len_bytes + tmp_message
		return message

	def get_payload_from_buffer(self, buffer):
		'''
		#从buffer中解析报文负载
		'''
		if not buffer:
			return

		import struct
		if buffer.size < MessageCodec.MESSAGE_LENGTH_LEN:
			# 当前缓冲区的长度过小,长度头没有接收全
			return None

		message_len_bytes = buffer.read(MessageCodec.MESSAGE_LENGTH_LEN)
		message_len = struct.unpack(MessageCodec.MESSAGE_LENGTH_FORMAT, message_len_bytes)[0]

		if buffer.size - MessageCodec.MESSAGE_LENGTH_LEN < message_len:
			# 当前缓冲区的长度过小,message 没有接收全
			return None

		buffer.add_read_index(MessageCodec.MESSAGE_LENGTH_LEN)

		tmp_payload = buffer.read(message_len)
		buffer.add_read_index(message_len)

		if self._encryptor and self._if_encrypt:
			# 如果指定了加密,则解密
			tmp_payload = self._encryptor.decrypt(tmp_payload)

		if self._compressor and self._if_compress:
			# 如果指定了压缩,则解压缩
			tmp_payload = self._compressor.decompress(tmp_payload)

		payload = tmp_payload

		return payload


if __name__ == '__main__':
	payload = 'Wait, there is more! You can even mix "--bind" and "--connect". That means that your server will wait for requests on a given address, and connect as a worker on another. Likewise, you can specify "--connect" multiple times, so your worker will connect to multiple queues. If a queue is not running, it wons the magic of zeromq).'

	import buffer

	buffer_ins = buffer.Buffer()
	message_codec = MessageCodec()

	message = message_codec.generate_message_with_payload(payload)
	print message, len(message)

	buffer_ins.append(message)

	payload = message_codec.get_payload_from_buffer(buffer_ins)

	print payload, len(payload)

	pass
