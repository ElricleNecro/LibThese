# -*- encoding: utf-8 -*-

class SIS(object):
	#u, v = 1, 2
	#Lambda, Mu = -1./4., 2
	def __init__(self):
		self._lambda = -1./4.
		self._mu     = 2

		self._u      = 1
		self._v      = 2

	@property
	def Lambda(self):
		return self._lambda
	@Lambda.setter
	def Lambda(self, n):
		self._lambda = n

	@property
	def mu(self):
		return self._mu
	@mu.setter
	def mu(self, n):
		self._mu = n

	@property
	def u(self):
		return self._u
	@u.setter
	def u(self, n):
		self._u = n

	@property
	def v(self):
		return self._v
	@v.setter
	def v(self, n):
		self._v = n

