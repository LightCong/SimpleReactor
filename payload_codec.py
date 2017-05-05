#encoding=utf8
class PayLoadCodec(object):
	'''
	报文负载,前面有type 头指示是应用数据,还是系统数据(如心跳)
	'''
	PAYLOADCODEC_TYPE_FORMAT='<I'
	PAYLOADCODEC_TYPE_LEN=4

	# 负载类型
	PAYLOAD_APP=1
	PAYLOAD_SYS_LST=[]

	def __init__(self):
		pass


	def generate_payload_with_data(self,data,tpe=PAYLOAD_APP):
		'''
		将上层应用数据(data)构造成负载(payload)
		'''
		import struct
		if not data or len(data)==0:
			return ''

		tpe_bytes=struct.pack(PayLoadCodec.PAYLOADCODEC_TYPE_FORMAT,tpe)
		return tpe_bytes+data


	def get_data_from_payload(self,payload):
		'''
		从负载中解析上层应用数据和数据类型
		'''
		import struct
		if not payload or len(payload)<=PayLoadCodec.PAYLOADCODEC_TYPE_LEN:
			return None,None

		#解析payload
		tpe=struct.unpack(PayLoadCodec.PAYLOADCODEC_TYPE_FORMAT,payload[:PayLoadCodec.PAYLOADCODEC_TYPE_LEN])[0]
		data=payload[PayLoadCodec.PAYLOADCODEC_TYPE_LEN:]

		if tpe!=PayLoadCodec.PAYLOAD_APP and (not tpe in PayLoadCodec.PAYLOAD_SYS_LST):
			# 类型不在范围内
			return None,data

		return tpe,data


if __name__ == '__main__':
	data="hello world"
	payload_codec_ins=PayLoadCodec()
	payload=payload_codec_ins.generate_payload_with_data(data)
	print payload,len(payload)

	tpe,new_data=payload_codec_ins.get_data_from_payload(payload)
	print tpe,new_data
