# -*- encoding: utf-8 -*-

import numpy as np
from ..Utils import Ode as o

"""Package contenant méthodes et classes travaillant autour du modèle de
sphère auto-gravitante, isotherme et tronquée.
"""

class SIB(o.Ode):
	"""Cette classe dérive de la classe de résolution des ODE du
	package Outils et implémente la résolution des équations pour la
	sphère isotherme et tronquée, en utilisant le changement de
	variable de Milne.
	"""
	def __init__(self, t=100, ti = 0, dt=1e-4, N=None):
		super(SIB, self).__init__(t, ti, dt, N)
		self._X0 = np.array([3.0, 0.0], dtype=np.float64)

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
		"""Calcul les u, v, $\mu$, $\lambda$ pour la SIB.
		"""
		super(SIB, self).Solve()
		self.Mu     = self.X[self.X[:,1]!=0.0,1]
		self.Lambda = (1.5 - self.X[self.X[:,1]!=0.0,0]) / self.Mu

