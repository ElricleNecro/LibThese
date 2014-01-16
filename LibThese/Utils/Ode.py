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
		self.X0   = np.array([0.0, 0.0], dtype=np.float64)
		self.tmax = tmax
		self.ti   = ti
		self.dt   = dt
		if N is None:
			self.N     = (self.tmax - self.ti) / self.dt
		else:
			self.dt    = (self.tmax - self.ti) / self.N

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
	def Tmax(self):
		return self.tmax
	@Tmax.setter
	def Tmax(self, n):
		self.tmax = n
		self.dt = (self.tmax - self.ti) / self.N

	@property
	def NumPoints(self):
		return self.N
	@NumPoints.setter
	def NumPoints(self, n):
		self.N  = n
		self.dt = (self.tmax - self.ti) / self.N

	@property
	def TimeStep(self):
		return self.dt
	@TimeStep.setter
	def TimeStep(self, n):
		self.dt = n
		self.N  = (self.tmax - self.ti) / self.dt

	def Generate_x(self):
		self.x                = np.arange(self.ti, self.tmax, self.dt)

	def Solve(self):
		"""Résout l'équation différentielle définie par la fonction "func".
		Le résultat est placé dans l'attribut X, l'axe "temporelle" dans x.
		"""
		self.Generate_x()
		self.X, self.infodict = ig.odeint(self.func, self.X0, self.x, full_output=True, rtol=1e-8)

