# encoding=utf8
import sys


class Buffer(object):
	'''
	基于cstringIO 实现的字节buffer
	'''

	def __init__(self, max_size=65535):
		import cStringIO
		self._buf = cStringIO.StringIO()
		self.read_index = 0
		self.write_index = 0
		self._max_size = max_size

	@property
	def size(self):
		return self.write_index - self.read_index

	def reset(self):
		import cStringIO
		self._buf.seek(0)
		self._buf.truncate()
		self.read_index = 0
		self.write_index = 0

	def append(self, data):
		'''
		写buff
		'''
		if not data or len(data) == 0:
			return

		# 将文件指针移到末尾
		self._buf.seek(0, 2)
		self._buf.write(data)
		# 标识写指针位置
		self.write_index += len(data)
		pass

	def read(self, size):
		'''
		读buff
		'''
		assert (size >= 0 and self.read_index <= self.write_index)

		# 要求读取的尺寸过大,只能返回有限多的内容
		real_size = min(size, self.write_index - self.read_index)

		if real_size == 0:
			return ''

		# 调整读指针位置
		self._buf.seek(self.read_index, 0)
		content = self._buf.read(real_size)
		self._buf.seek(self.read_index, 0)  # 恢复原位置
		return content

	def add_read_index(self, count):
		self.read_index += count
		if self.read_index > self.write_index:
			self.read_index = self.write_index
		if self.read_index == self.write_index and self.read_index > self._max_size:
			# 已经被读取,然而还存在buf里的数据尺寸太大了,要clear 一下
			self.reset()

	# ---------------以下api 针对于output_buffer 使用-------------------
	def get_all(self):
		# 一次性将当前缓冲拿出来发送,
		self._buf.seek(self.read_index, 0)
		content = self._buf.read()
		return content


if __name__ == '__main__':
	buf = Buffer(max_size=10)

	buf.append("0123456789abcdef")
	print buf.read(2)
	print buf.read(2)
	print buf.read(16)
	print buf.write_index, buf.read_index  # reset

	buf.append("0123456789abcdef")
	print buf._buf.getvalue()
	print buf.get_all()
	print buf.read(2)
	print buf.get_all()
	buf.add_read_index(16)
	print buf.write_index, buf.read_index
