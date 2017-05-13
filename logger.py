# encoding=utf8
import logging


class LoggerBackend(object):
	'''
	队列后端,每个进程一个,负责从queue中取出字符串写入文件
	'''

	def __init__(self, change_log_internal=3600 * 24, log_dir='Log', log_basename='SimpleLog'):
		import Queue, time, os
		self.queue = Queue.Queue()
		self._log_dir = log_dir
		if not os.path.exists(self._log_dir):
			os.mkdir(self._log_dir)

		self.log_name_prefix = os.path.join(self._log_dir, log_basename)

		self.log_start_time = time.time()
		self._change_log_internel = change_log_internal
		self.filename = self.get_filename()

	def get_filename(self):
		import datetime
		return '{}_{}'.format(self.log_name_prefix,
							  datetime.datetime.fromtimestamp(self.log_start_time).strftime("%Y-%m-%d"))

	def work(self):
		import time, threading
		while True:
			log_str = self.queue.get()
			now = time.time()
			if now - self._change_log_internel > self.log_start_time:
				# 超过时间间隔了,需要开一个新日志
				self.log_start_time = now
				self.filename = self.get_filename()

			# 写日志到文件
			wfp = open(self.filename, 'a')
			wfp.write(log_str)
			wfp.close()
			self.queue.task_done()
		pass


# 日志后端是一个单例对象,独占一个worker线程,从queue里取出日志写入文件
import threading

logger_backend = LoggerBackend()
logger_backend_thread = threading.Thread(target=logger_backend.work)
logger_backend_thread.setDaemon(True)
logger_backend_thread.start()


class Logger(object):
	'''
	异步日志系统,每个线程一个
	'''

	def __init__(self, flush_internal=1, buffer_len_bound=100, queue=logger_backend.queue):
		import cStringIO, time

		self.logger = None
		self.file_handler = None
		self.thread = None
		self._queue = queue  # 向日志后端发送内容的队列

		self.last_flush_time = time.time()
		self._flush_internal = flush_internal  # 缓冲区刷新间隔

		self.buffer = cStringIO.StringIO()  # 缓冲区
		self._buffer_len_bound = buffer_len_bound  # 缓冲区上限1024,到达上限需写入离线文件
		self.buffer_len = 0

		# 日志输出用tab分割,方便脚本处理
		self.fmt = "%(asctime)s	%(thread)d	%(levelname)s	%(pathname)s:%(lineno)d	%(message)s"
		self.create_logger()

	def create_logger(self):
		import logging

		if self.logger:
			return
		# 创建logger
		logger_name = 'simple_logger'
		self.logger = logging.getLogger(logger_name)
		self.logger.setLevel(logging.DEBUG)

		# logger 写入的是缓冲区,后端日志线程会读取缓冲区写入文件
		self.file_handler = logging.StreamHandler(self.buffer)
		self.file_handler.setFormatter(logging.Formatter(self.fmt))

		# 为logger 设置handler
		self.logger.addHandler(self.file_handler)

	def write_log(self, log_message, level, sync=False):
		'''
		写入log
		:param sync:是否阻塞直至缓冲区全部写入文件
		运行在逻辑线程(非日志线程)
		'''
		import logging, time, sys
		'''
		if not level in logging.Logger.__dict__:
			return

		logging.Logger.__dict__[level](self.logger,message)
		self.buffer_len+=len(message)
		'''

		call_frame = sys._getframe().f_back  # 获取调用write_log 的pyFrameObject

		# 获取事发地点的文件名,行号和函数名
		fn, lno, func = call_frame.f_code.co_filename, call_frame.f_lineno, call_frame.f_code.co_name

		# 制造记录
		record = self.logger.makeRecord(self.logger.name, logging._levelNames[level.upper()],
										fn=fn, lno=lno, msg=log_message,
										args=None, exc_info=None, func=func, extra=None)
		# 处理记录
		self.logger.handle(record)
		# 维护缓冲区消息长度
		self.buffer_len += len(log_message)

		now = time.time()
		if sync == True:
			self.flush()
			self.last_flush_time = now
			self._queue.join()  # 阻塞直到worker 完成工作


		elif self.buffer_len >= self._buffer_len_bound or now - self.last_flush_time > self._flush_internal:
			# 如果缓冲满了或者刷新间隔超过flush_internal,则向后端写入缓冲区
			self.flush()
			self.last_flush_time = now

	def flush(self):
		# 将整个缓存写入队列
		import cStringIO
		self._queue.put(self.buffer.getvalue())
		self.buffer.seek(0)
		self.buffer.truncate()
		self.buffer_len = 0
		# self.file_handler.stream=self.buffer

		pass


if __name__ == '__main__':
	logger = Logger(flush_internal=3, buffer_len_bound=2048)

	import time, logging

	i = 0
	start = time.time()
	while i < 100000:
		logger.write_log("hello world {}".format(i), 'error')
		i += 1
	delta = time.time() - start
	print delta

	# 对比试验
	logger_name = 'simple_logger'
	logger = logging.getLogger(logger_name)
	logger.setLevel(logging.DEBUG)
	file_handler = logging.FileHandler('test.log')
	file_handler.setFormatter(
		logging.Formatter("%(asctime)s	%(thread)d	%(levelname)s	%(pathname)s:%(lineno)d	%(message)s"))
	logger.addHandler(file_handler)
	start = time.time()
	i = 0
	while i < 100000:
		logger.error("hello world {}".format(i))
		i += 1

	delta = time.time() - start
	print delta
