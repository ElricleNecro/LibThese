#! /usr/bin/env python3
# -*- coding:Utf8 -*-

import numpy as np
from   .dir.rw                         import File

class KingParam:
	"""Lit les paramètres du modèle de King dans un fichier de paramètre issu du générateur de condition initiale.
	"""
	def __init__(self, fileparam):
		if type(fileparam) is not str:
			raise TypeError("La classe doit être construite à l'aide d'un fichier")
		param = File.Read_File(fileparam)
		param = File.Read_File(fileparam)

		self.rc   = param[0][0]
		self.m    = param[0][1]
		self.El   = param[1][0]
		self.sig2 = param[1][1]
		self.W0   = param[2][0]
		self.rho0 = param[2][1]

	def __str__(self):
		return "{ W0: " + str(self.W0) + ", El: " + str(self.El) + ", Sigma2: " + str(self.sig2) + ", rc: " + str(self.rc) + ", m: " + str(self.m) + ", Rho0: " + str(self.rho0) + "}"

class Distribution:
	"""Classe gérant les calculs autour de la fonction de distribution.
	"""
	def __init__(self, distrib, fileparam=None, Pot=None):
		self.btheo = False
		self.King  = None
		self.Jac   = None
		if type(distrib) is str:
			self.Distrib = np.array(File.Read_File(distrib))
		else:
			self.Distrib = distrib

		if fileparam is not None and Pot is None:
			raise ValueError("Vous devez donnez les valeurs du potentiel !!!")
		elif fileparam is not None and Pot is not None:
			self.btheo = True
			self.King  = KingParam(fileparam)
			self.f_jacobien(Pot)
			self.Theo = self.Jac * self.f_distribtheo() * (self.Distrib[1,0] - self.Distrib[0,0]) / self.King.m
			print("Paramètre du King :\n", self.King)

	def f_jacobien(self, Pot):
		"""Calcule le jacobien permettant de passer de f(x, p) à f(E) à partir du potentiel issu de la simulation/du snapshot.
		"""
		from scipy.integrate import trapz, simps
		JAC = []
		for E in self.Distrib[:,0]:
			tmp = E - self.King.m*Pot[:,1]
			tmp = tmp[np.where(tmp > 0.0)]
			tmp_psi = (4.0 * np.pi)**(2.0) * self.King.m * (Pot[0:len(tmp),0])**(2.0) * np.sqrt( 2.0*self.King.m * tmp)
			JAC.append(trapz(tmp_psi, x=Pot[0:len(tmp),0]))

		self.Jac = np.array(JAC)

	def f_distribtheo(self):
		"""Retourne la fonction de distribution du modèle de King, 1966. Se sert des paramètres donné dans le fichier fileparam.
		Si l'un des paramètres est donnée en utilisant les paramètres optionnels, il écrase celui donné dans le fichier.

		Valeur de retour :
		np.array de même taille que E contenant la fonction de distribution de King, 1966.
		"""
		return self.King.rho0 * (2.0 * np.pi * self.King.m * self.King.sig2)**(-3.0/2.0) * (np.exp((self.King.El - self.Distrib[:,0])/self.King.sig2) - 1.0)

	def plotDistrib(self, ax1=None, prefix="", suppose = False, info=""):
		"""Calcul la distribution d'énergie théorique et la distribution de la simulation,
		puis les tracent ensemble sur le même graphe.

		Paramètres optionnels :
		ax1       = None           :: matplotlib.axes sur lequel tracer.
		prefix    = ""             :: Préfixe de la simulation. En combinaison avec save, enregistre les graphiques dans un fichier pdf de nom prefix + ".pdf".
		suppose   = False          :: Superpose ou non les graphiques.
		info      = ""             :: Quelques informations à rajouter dans le titre des graphiques.

		Valeur de retour :
		classe figure matplotlib associé au graphique.
		"""

		if ax1 is None:
			fig    = plt.figure(prefix + "Distribution")
			if not suppose:
				fig.clf()

			ax1    = fig.add_subplot(111)

		ax1.set_title("Distribution en énergie des particules " + info)
		ax1.set_ylabel(r'$N_{\mathrm{Particules}}$')
		ax1.set_xlabel(r'Énergie en Yotta-Joule ($1 YJ = 10^{24} J$)')

		if fileparam != None:
			ax1.plot(Distrib[:,0]/1e24, Distrib[:,2], '+', Distrib[:,0]/1e24, Theo, 'g-')
			ax1.plot()
			ax1.legend(('Distribution de la simulation', 'Distribution théorique',), 'upper left', shadow=True)
		else:
			ax1.plot(Distrib[:,0]/1e24, Distrib[:,2], '+')
			ax1.legend(('Distribution de la simulation', ), 'upper left', shadow=True)

		return fig

