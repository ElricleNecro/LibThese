# -*- encoding: utf-8 -*-

import numpy as np
from ..Utils import Ode as o

"""Package contenant méthodes et classes travaillant autour du modèle de
sphère auto-gravitante, isotherme et tronquée.
"""

class Fujiwara1983(object):
	"""Cette classe implémente la fonction de distribution d'une sphère de Hénon tel que décrite dans Fujiwara, 1983.
	Elle permet d'accéder facilement à l'espace des phases en masses et en densité pour comparaison avec les données
	de simulation.
	Une évolution possible est la résolution de l'équation de poisson afin d'accéder en plus aux profils de densité,
	potentiel...
	"""
	def __init__(self, M, R, sig_v, u_max=2.0, j_max=1.6, j_min=0.0, R_min=0.1):
		self.M = M
		self.R = R
		self.u = [-u_max, u_max]
		self.j = [j_min, j_max]
		self.R_min = 0.1
		self.rho_0 = 3. * M / ( 4.*np.pi * R**3)
		self.sig_v = sig_v

	def __call__(self, r, u, j):
		return self.rho0 * (2.*np.pi*self.sig_v**2)**(-3./2.) * np.exp( -(u**2 + j**2/r**2)/(2*self.sig_v**2) )

class Henon(o.Ode):
	"""Cette classe dérive de la classe de résolution des ODE du
	package Outils et implémente la résolution des équations pour la
	sphère de Hénon.
	"""
	def __init__(self, M, R, N=1e4, beta=1.0, t=100, ti = 0):
		super(Henon, self).__init__(t, ti)
		self._X0  = np.array([3.0, 0.0], dtype=np.float64)
		self.beta = beta
		self.R    = R
		self.m    = M/N
		self.rho0 = M / ( (4./3.)*np.pi*R**3.0 )

	@property
	def X0(self):
		return self._X0

	@X0.setter
	def X0(self, newval):
		self._X0 = newval

	def func(self, v, x=0):
		y = np.zeros(2)
		if x/2.0 >= 1.0e-3:
			y[0] = v[0]*(3.0 - v[0] - v[1])/x	# u(x)
			y[1] = v[1]*(v[0] - 1.0)/x		# v(x)
		else:
			y[0] = -2.0/5.0*x + 19.0*4.0/1050.0*x**3.0 - 823.0*6.0/189000.0*x**5.0
			y[1] = 2.0/3.0*x - 4.0/30.0*x**3.0 + 6.0/315.0*x**5.0
		return y

	def Solve(self):
		"""Calcul le potentiel pour la sphère de Hénon.
		"""
		super(Henon, self).Solve()

	def __call__(self, r, v):
		return self.r_distrib(r) * self.v_distrib(v)

	def v_distrib(self, v):
		raise NotImplementedError

	def r_distrib(self, r):
		if r <= self.R:
			return self.rho0 / self.m * self.beta
		else:
			return 0.0

class HenonVcte(Henon):
	"""Sphère de Hénon ayant un profil de vitesse uniforme.
	"""
	def __init__(self, v0, rho0, R, m, t=100, ti = 0):
		self.v0 = v0
		beta = self.normalize(lambda v:1.0/v0, 0, v0)
		super(HenonVcte, self).__init__(rho0, R, m, beta=1.0/beta, t=t, ti=ti)

	@staticmethod
	def normalize(f, a, b):
		"""Intègre la fonction f entre a et b."""
		from scipy.integrate import quad
		res, *ret = quad(f, a, b)
		return res

	def v_distrib(self, v):
		if v <= self.v0:
			return 1.0 / self.v0**3.0
		else:
			return 0.0

class HenonVGauss(Henon):
	"""Sphère de Hénon ayant un profil de vitesse uniforme.
	"""
	def __init__(self, v0, sig_v, M, R, N, t=100, ti = 0):
		self.v0 = v0
		self.sig_v = sig_v
		beta = self.normalize(lambda v:1.0/v0, 0, v0)
		super(HenonVGauss, self).__init__(M, R, N, beta=1.0/beta, t=t, ti=ti)

	@staticmethod
	def normalize(f, a, b):
		"""Intègre la fonction f entre a et b."""
		from scipy.integrate import quad
		res, *ret = quad(f, a, b)
		return res

	def v_distrib(self, v):
		return 1.0 / ( self.sig_v * np.sqrt(2.*np.pi) ) * np.exp( ( v - self.v0 )**2.0 / (2.0*self.sig_v**2.0) )
