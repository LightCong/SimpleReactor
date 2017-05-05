#encoding=utf8
class RunInLoop(object):
	'''
	主动接口包装器,目的是让接口在非io线程调用时,转移到io线程里执行
	'''

	def __init__(self,functor):
		self._functor=functor
		self._loop=None
		self.calle_ins=None
		pass

	def __get__(self, instance, owner):
		if instance and '_loop' in instance.__dict__:
			self.calle_ins = instance
			self._loop=instance._loop

		else:
			#调用functor 的类里没有loop,应该报错
			raise Exception()

		return self

	def __call__(self, *args, **kwargs):
		import loop
		if self._loop.local_thread():
			# 如果在local线程里,则直接调用
			self._functor(self.calle_ins,*args,**kwargs)
		else:
			# 否则构造一个闭包,塞到队列里
			self._loop.add_inloop_functor((self._functor,self.calle_ins,args,kwargs))


if __name__ == '__main__':
	import logger
	class Test(object):
		def __init__(self):
			import loop
			self._loop=loop.EventLoop(0.1,logger.Logger())
			pass

		@RunInLoop
		def test(self,a,b):
			print a,b


	t=Test()
	t.test(1,2)
