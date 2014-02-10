# -*- encoding: utf-8 -*-

import abc
import numpy	       as np
import scipy.integrate as ig

"""http://www.doughellmann.com/PyMOTW/abc/"""

class Ode(object,metaclass=abc.ABCMeta):
	"""Cette classe permet de gérer un Modèle de King Adimensionné,
	et d'en tirer les différentes quantités intéressantes.
	"""
	def __init__(self, tmax=100, ti=0, dt=1e-4, N=None):
		self.X0    = np.array([0.0, 0.0], dtype=np.float64)
		self._tmax = tmax
		self._ti   = ti
		if N is None:
			self._dt = dt
			self._N  = (self._tmax - self._ti) / self._dt
		else:
			self._N  = N
			self._dt = (self._tmax - self._ti) / self.N

	@abc.abstractproperty
	def X0(self):
		raise NotImplementedError("You MUST implement setter AND getter for X0!")

	@X0.setter
	def X0(self, newval):
		raise NotImplementedError("You MUST implement setter AND getter for X0!")

	@abc.abstractmethod
	def func(self, x, t=0):
		raise NotImplementedError("You MUST implement this method!")

	@property
	def tmax(self):
		return self._tmax
	@tmax.setter
	def tmax(self, n):
		self._tmax = n
		self._dt = (self._tmax - self._ti) / self._N

	@property
	def NumPoints(self):
		return self._N
	@NumPoints.setter
	def NumPoints(self, n):
		self._N  = n
		self._dt = (self._tmax - self._ti) / self._N

	@property
	def timeStep(self):
		return self._dt
	@timeStep.setter
	def timeStep(self, n):
		self._dt = n
		self._N  = (self._tmax - self._ti) / self._dt

	def Generate_x(self):
		self.x                = np.arange(self._ti, self._tmax, self._dt)

	def Solve(self):
		"""Résout l'équation différentielle définie par la fonction "func".
		Le résultat est placé dans l'attribut X, l'axe "temporelle" dans x.
		"""
		self.Generate_x()
		self.X, self.infodict = ig.odeint(self.func, self.X0, self.x, full_output=True, rtol=1e-8)

