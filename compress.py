# encoding=utf-8
import zlib


class Compressor(object):
	def __init__(self):
		self.compress_obj = zlib.compressobj()
		self.decompress_obj = zlib.decompressobj()

	def compress(self, data):
		# 压缩
		return self.compress_obj.compress(data) + self.compress_obj.flush(zlib.Z_SYNC_FLUSH)

	def decompress(self, data):
		# 解压缩
		return self.decompress_obj.decompress(data)


if __name__ == '__main__':
	compressor_ins = Compressor()
	s = "efasldkfjancecaca;iceaaacalsjsssssssssssjjjkeklsiecmdl"
	print s, len(s)
	c_s = compressor_ins.compress(s)
	print c_s, len(c_s)
	d_c_s = compressor_ins.decompress(c_s)
	print d_c_s, len(d_c_s)

	s = "efasldkfjancecaca;iceaaacalsjsssssssssssjjjkeklsiecmdl"
	print s, len(s)
	c_s = compressor_ins.compress(s)
	print c_s, len(c_s)
	d_c_s = compressor_ins.decompress(c_s)
	print d_c_s, len(d_c_s)
