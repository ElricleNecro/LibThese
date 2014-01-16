# -*- encoding: utf-8 -*-

import numpy	       as np
import scipy.integrate as ig
import scipy.special   as ss

class ADimKing:
	"""Cette classe permet de gérer un Modèle de King Adimensionné,
	et d'en tirer les différentes quantités intéressantes.
	"""
	def __init__(self, W0):
		self.W0 = W0
		self.X0 = np.array( [ W0, 0.0 ], dtype="float64" )

	def __call__(self, x, t=0):
		return self.func(x, t)

	def func(self, x, t=0):
		if t > 1e-6:
			return np.array( [ x[1], -self.rho(x[0]) - 2.0*x[1]/t ], dtype="float64" )

		g0 = self.W0
		g2 = -self.rho(g0)/3.0
		g4 = 2.0 * self.rho(g0) * (np.sqrt(g0/np.pi) - np.exp(g0) * ss.erf(np.sqrt(g0))/2.0)/5.0
		
		return np.array( [ g2 * t + g4 * (t**3.0) / 6.0,
				   g2     + g4 * (t**2.0) / 2.0 ], dtype="float64" )

	def rho(self, phi):
		"""Retourne la densité volumique de masse adimensionnée
		et normalisé au point phi.
		"""
		return np.exp(phi)*ss.erf(np.sqrt(phi)) - np.sqrt(4.0*phi/(np.pi))*(1.0+2.0*phi/(3.0))

	def Solve(self):
		"""Résout les équations du modèle de King.
		"""
		self.x           = np.arange(0.0, 100.0, 1e-4) #np.linspace(0, 100,  1000)
		self.X, infodict = ig.odeint(self.func, self.X0, self.x, full_output=True, rtol=1e-8)

class DimKing(ADimKing):
	"""Cette classe gére un modèle de King dimensionné.
	"""
	def __init__(self, W0, rc, sig_v, G=6.67e-11, N=10000):
		"""Construit un objet King avec toutes les quantités nécessaire pour le dimensionnement.
		Attention à être cohérent avec vos unités.
		W0           :: Condition initiale du King,
		rc           :: Rayon de coeur du King,
		sig_v        :: Dispersion de vitesse de l'objet,
		G = 6.67e-11 :: Constante gravitationnelle en Kg^-1.m^3.s^-2
		N = 10000    :: Nopmbre de particules du système (nécessaire pour avoir la masse d'une particule).
		
		Attention, hormis pour W0, les unités des autres paramètres doivent être cohérents entre eux :
		si rc est donnée en parsec, il faudra adapter les unités de sig_v et G.
		"""
		super().__init__(W0)
		self.rc    = rc
		self.sig_v = sig_v
		self.G     = G
		self.rho0  = sig_v / (8.0*np.pi*G*rc**2.0)
		self.N     = N

	def Solve(self):
		"""Résoud et redimensionne le problème.
		"""
		super().Solve()
		self.X   = self.X[np.isfinite(self.X)]
		self.X.shape = len(self.X) / 2, 2
		self.x   = self.x[0:len(self.X)]
		self.Rho = np.zeros(len(self.x))
		
		for i, _ in enumerate(self.x):
			self.x[i]   *= self.rc
			self.Rho[i]  = self.rho(self.X[i,0]) * self.rho0
		
		self.Mtot = ig.trapz(4.0*np.pi*(self.x**2.0)*self.Rho, self.x)#, even='avg')
		self.m    = self.Mtot / self.N
		self.sig2 = self.m * self.sig_v / 2.0
		self.El   = -self.m * self.G * self.Mtot / self.x[-1]
		
		for i, _ in enumerate(self.X):
			self.X[i,0]  = (self.El - self.X[i,0]*self.sig2) / self.m
			self.X[i,1] *= -self.sig2 / self.m

	def Param(self, filename):
		"""Enregistre les paramètres pour comparaison avec la librairie C."""
		with open(filename, 'w') as fich:
			fich.write(str(self.rc) + " " + str(self.m) + "\n")
			fich.write(str(self.El) + " " +  str(self.sig2) + "\n")
			fich.write(str(self.W0) + " " +  str(self.rho0) + "\n")
			fich.write(str(self.G)  + " " +  str(self.Mtot) + "\n")

	def Temperature(self):
		"""Calcul la température et la retourne.
		"""
		ig.quad()
