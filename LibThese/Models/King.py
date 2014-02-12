# -*- encoding: utf-8 -*-

import numpy	         as np
import scipy.special     as ss
import scipy.integrate   as ig
import scipy.interpolate as ip

from ..Utils import Ode  as o

"""Package contenant des classes et méthodes permettant de travailler
sur la sphére de King.
"""

class ADimKing(o.Ode):
	"""Cette classe permet de gérer un Modèle de King Adimensionné,
	et d'en tirer les différentes quantités intéressantes.
	"""
	def __init__(self, W0, t=100, ti=0, dt=1e-4, N=None):
		super(ADimKing, self).__init__(t, ti, dt, N)
		self.W0 = W0
		self._X0 = np.array( [ W0, 0.0 ], dtype=np.float64 )

	@property
	def X0(self):
		return self._X0

	@X0.setter
	def X0(self, newval):
		self._X0 = newval

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

def FromConfig(conf_file, **kwargs):
	nblig = 4
	sep = ' '
	res = list()
	#####################
	#       Lecture du fichier de donnée à ajuster :
	################################################
	with open(conf_file, "r") as fich:
		for i, lig in enumerate(fich):
			if i > nblig:
				break
			lig = lig.replace('"', '')
			lig = lig.replace('\'', '')
			lig = lig.split("#")[0]
			lig = lig.split("\n")[0]
			lig = lig.split("\r")[0]
			lig = lig.expandtabs(1)
			if lig != '':
				lig = lig.split(sep)
				while sep in lig:
					lig.remove(sep)
				while ' ' in lig:
					lig.remove(' ')
				while '' in lig:
					lig.remove('')
				res.append([eval(i) for i in lig])

	while [] in res:
		res.remove([])

	a  = -10.0698
	b  = 0.220152
	c  = -1.63409
	d  = -2.3341
	e  = 16.913

	rc = res[2][1] * np.tan(res[0][0]/60.0 * np.pi/180.0) * 1e3 * 3.086e13
	W0 = np.abs( (1.0/b) * np.log( (d*res[2][0] + e - c) / a ) )
	sv = res[1][0] * 1e3

	print(rc, W0, sv)

	kwargs["G"] = res[3][0]
	return DimKing(W0, rc, sv, **kwargs)

class DimKing(ADimKing):
	"""Cette classe gére un modèle de King dimensionné.
	"""
	def __init__(self, W0, rc, sig_v, G=6.67e-11, N=10000, t=100, ti=0, dt=1e-4, Npas=None):
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
		super(DimKing, self).__init__(W0, t=t, ti=ti, dt=dt, N=Npas)
		self.rc    = rc
		self.sig_v = sig_v
		self.G     = G
		self.rho0  = sig_v*sig_v / (8.0*np.pi*G*rc**2.0)
		self.N     = N
		self._XAxis_transform = False

	@staticmethod
	def f_jacobien(nbE, r, pot, m):
		"""Calcule le jacobien permettant de passer de f(x, p) à f(E) à partir du potentiel issu de la simulation/du snapshot.

		Paramètres obligatoires :
		E   :: Énergie.
		Pot :: np.array contenant le rayon et le potentiel (cf le tableau issu de launch).
		m   :: masse d'une particule.

		Valeur de retour :
		np.array contenant le jacobien, de même taille que E.
		"""
		from scipy.integrate import trapz
		tmp = nbE - m*pot[:]
		i = 0
		for j in tmp:
			i += 1
			if j < 0.0:
				break
		tmp_psi = (4.0 * np.pi)**(2.0) * m * (r[0:i-1])**(2.0) * np.sqrt( 2.0*m * tmp[0:i-1])
		return trapz(tmp_psi, x=r[0:i-1])

	def __call__(self, r, v, jac = False):
		E = 0.5*self.m*v**2 + self.m*self.Potentiel(r)
		if E > self.El:
			return 0
		else:
			res = self.rho0 * (2.0*np.pi*self.m*self.sig2)**(-3.0/2.0) * (np.exp((self.El - E)/self.sig2) - 1)
			if jac:
				return self.f_jacobien(E, self.x, self.X[:,0], self.m)*res
			else:
				return res

	def DimSolve2(self):
		"""Résoud et redimensionne le problème.
		"""
		super(DimKing, self).Solve()
		self.X   = self.X[np.isfinite(self.X)]
		self.X.shape = len(self.X) / 2, 2
		self.x   = self.x[0:len(self.X)]

	def CalcRho(self):
		"""Redimensionne la densité de masse volumique.
		"""
		self.Rho = self.rho(self.X[:,0])*self.rho0

	def CalcMtot(self):
		if self._XAxis_transform:
			self.Mtot = ig.trapz(4.0*np.pi*(self.x**2.0)*self.Rho, self.x)
		else:
			self.Mtot = 4.0*np.pi*self.rho0 * (self.rc**3) * ig.trapz((self.x**2.0) * ( -np.sqrt(4.0 * self.X[:,0]/np.pi) * (1.0 + 2./3.0 * self.X[:,0]) + np.exp(self.X[:,0]) * ss.erf(np.sqrt(self.X[:,0])) ), self.x)

	def DimXAxis(self):
		self._XAxis_transform = True
		self.x = self.x * self.rc

	def Calcm(self):
		self.m    = self.Mtot / self.N
		self.sig2 = self.m * self.sig_v / 2.0
		self.El   = -self.m * self.G * self.Mtot / self.x[-1]

	def CalcOther(self):
		for i, _ in enumerate(self.X):
			self.X[i,0]  = (self.El - self.X[i,0]*self.sig2) / self.m
			self.X[i,1] *= -self.sig2 / self.m

		#Calcul de la température (éq 3.21) :
		#	-> Variable intermédiaire de Calcul :
		msig = self.m * self.sig2
		cte  = np.sqrt(2.0 * msig /np.pi) / self.m**2.0
		cte2 = 3.0/2.0 * np.sqrt(2.0*np.pi*msig)
		phi  = self.El - self.m * self.X[:,0]
		gam  = phi / self.sig2
		fcts = (2.0*self.m * phi)**(5.0/2.0) * msig**(-2.0) / (5.0*self.rho(gam))

		self.tmp_test    = cte * (cte2 - fcts)
		self.Temperature = ip.UnivariateSpline(self.x, cte * (cte2 - fcts), s=0.1)
		self.Potentiel   = ip.UnivariateSpline(self.x, self.X[:,0], s=0.1)

		self.rmax = self.x[-1]
		self.vmax = np.sqrt( 2.0*( self.El/self.m - self.X[0,0] ) )

	def DimSolve(self):
		"""Résoud et redimensionne le problème.
		"""
		super(DimKing, self).Solve()
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

		#Calcul de la température (éq 3.21) :
		#	-> Variable intermédiaire de Calcul :
		msig = self.m * self.sig2
		cte  = np.sqrt(2.0 * msig /np.pi) / self.m**2.0
		cte2 = 3.0/2.0 * np.sqrt(2.0*np.pi*msig)
		phi  = self.El - self.m * self.X[:,0]
		gam  = phi / self.sig2
		fcts = (2.0*self.m * phi)**(5.0/2.0) * msig**(-2.0) / (5.0*self.rho(gam))

		self.tmp_test    = cte * (cte2 - fcts)
		self.Temperature = ip.UnivariateSpline(self.x, cte * (cte2 - fcts), s=0.1)
		self.Potentiel   = ip.UnivariateSpline(self.x, self.X[:,0], s=0.1)

		self.rmax = self.x[-1]
		self.vmax = np.sqrt( 2.0*( self.El/self.m - self.X[0,0] ) )

		#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		#!	  Vérifier les équations avec un logiciel calcul formel		 !
		#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

	def Param(self, filename):
		"""Enregistre les paramètres pour comparaison avec la librairie C."""
		with open(filename, 'w') as fich:
			fich.write(str(self.rc) + " " + str(self.m) + "\n")
			fich.write(str(self.El) + " " +  str(self.sig2) + "\n")
			fich.write(str(self.W0) + " " +  str(self.rho0) + "\n")
			fich.write(str(self.G)  + " " +  str(self.Mtot) + "\n")

#	def Temperature(self):
#		"""Calcul la température et la retourne.
#		"""
#		ig.quad()

@np.vectorize
def FromKing(w0, rc, sig, N=2e5, withDimXAxis=False):
	tmp = kg.DimKing(w0, rc, sig, N=N)
	tmp.DimSolve2()
	tmp.CalcRho()
	if withDimXAxis:
		tmp.DimXAxis()
	tmp.CalcMtot()

	return tmp.Mtot

