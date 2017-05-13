# encoding=utf-8
import time


class Encrptor(object):
	def __init__(self, key=None):
		self.key = "mini10_cheer_up!!"

	def kernel(self, val):
		en_byte_array = bytearray()
		val_byte_array = bytearray(val)  # 将待加密串转为bytearray
		key_byte_array = bytearray(self.key)  # 将模式串转为bytearray

		for i in range(0, min(len(val), len(self.key))):
			# 按位异或
			en_byte = val_byte_array[i] ^ key_byte_array[i]
			# 放入结果集
			en_byte_array.append(en_byte)
		en_byte_array.reverse()
		return str(en_byte_array)

	def de_kernel(self, val):
		de_byte_array = bytearray()
		val_byte_array = bytearray(val)  # 将待解密串转为bytearray
		key_byte_array = bytearray(self.key)  # 将模式串转为bytearray

		val_byte_array = val_byte_array[:min(len(val), len(self.key))]
		val_byte_array.reverse()
		for i in range(0, min(len(val), len(self.key))):
			# 按位异或
			en_byte = val_byte_array[i] ^ key_byte_array[i]
			# 放入结果集
			de_byte_array.append(en_byte)
		return str(de_byte_array)

	def encrypt(self, val):
		encrypt_result = ''
		while len(encrypt_result) != len(val):
			# 待加密串比加密模式串长，一次加密加密不完，用模式串分批加密
			part_result = self.kernel(val[len(encrypt_result):])
			encrypt_result += part_result
		return encrypt_result

	def decrypt(self, val):
		decrypt_result = ''
		while len(decrypt_result) != len(val):
			# 待加密串比加密模式串长，一次加密加密不完，用模式串分批加密
			part_result = self.de_kernel(val[len(decrypt_result):])
			decrypt_result += part_result
		return decrypt_result


if __name__ == '__main__':
	encryptor = Encrptor()
	val = 'conxgiaflkasujfoaw;emfnaw;cfuawo;jmawel;fhaweo;ajl;kfaw'
	result = encryptor.encrypt(val)
	# print aa,len(aa)
	re = encryptor.decrypt(result)
	# print time.time()-start_time
	print re, len(re)
