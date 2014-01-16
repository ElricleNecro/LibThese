#! /usr/bin/env python
# -*- coding:Utf8 -*-

import numpy         as np

from ..dir.rw        import File

from scipy.integrate import trapz

def f_distribtheo(E, jac=None, El=None, rc=None, m=None, sig2=None, W0=None, rho0=None, fileparam="ci_param.dat"):
	"""Retourne la fonction de distribution du modèle de King, 1966. Se sert des paramètres donné dans le fichier fileparam.
	Si l'un des paramètres est donnée en utilisant les paramètres optionnels, il écrase celui donné dans le fichier.

	Paramètre obligatoire :
	E :: np.array contenant les valeurs d'énergie pour lesquelles la fonction de distribution doit être évaluée. Typiquement : les valeurs contenu dans la première colonne du np.array contenant la distribution en énergie des particules retourné par load.launch.

	Paramètres optionnels :
	jac       = None           :: np.array de même taille que E contenant le jacobien de la fonction de distribution. Typiquement : celui retourné par la fonction load.f_jacobien.
	El        = None           :: scalaire, valeur de l'énergie de libération, énergie maximale du système.
	rc        = None           :: scalaire, rayon de cœur tel que définit dans le modéle de King, 1966.
	m         = None           :: scalaire, masse d'une particule.
	sig2      = None           :: scalaire, dispersion de vitesse du système (cf : celle du catalogue de Harris).
	W0        = None           :: scalaire, condition initiale du modèle de King adimensionné.
	rho0      = None           :: scalaire, densité centrale.
	fileparam = "ci_param.dat" :: chaîne de caractère, nom du fichier dans lequel lire les données principale sur le système (ie : le fichier généré par le programme de génération des conditions initiale).

	Valeur de retour :
	np.array de même taille que E contenant la fonction de distribution de King, 1966.
	"""

	param = File.Read_File(fileparam)

	if rc == None: rc   = param[0][0]
	if m == None: m    = param[0][1]
	if El == None: El   = param[1][0]
	if sig2 == None: sig2 = param[1][1]
	if W0 == None: W0   = param[2][0]
	if rho0 == None: rho0 = param[2][1]

	print("Paramètres :\n\t(x) rc = "
			+ str(rc) + "\n\t(x) m = "
			+ str(m) + "\n\t(x) El = "
			+ str(El) + "\n\t(x) sigma2 = "
			+ str(sig2) + "\n\t(x) W0 = "
			+ str(W0) + "\n\t(x) rho0 = "
			+ str(rho0) + "\n")

	f    = rho0 * (2.0 * np.pi * m * sig2)**(-3.0/2.0) * (np.exp((El - E)/sig2) - 1.0)
	if jac == None:
		return f
	else:
		return jac * f

def f_jacobien(E, Pot, m):
	"""Calcule le jacobien permettant de passer de f(x, p) à f(E) à partir du potentiel issu de la simulation/du snapshot.

	Paramètres obligatoires :
	E   :: Énergie.
	Pot :: np.array contenant le rayon et le potentiel (cf le tableau issu de launch).
	m   :: masse d'une particule.

	Valeur de retour :
	np.array contenant le jacobien, de même taille que E.
	"""
	from scipy.integrate import trapz
	JAC = []
	for nbE in E[:]:
		tmp = nbE - m*Pot[:,1]
		i = 0
		for j in tmp:
			i += 1
			if j < 0.0:
				break
		tmp_psi = (4.0 * np.pi)**(2.0) * m * (Pot[0:i-1,0])**(2.0) * np.sqrt( 2.0*m * tmp[0:i-1])
		JAC.append(trapz(tmp_psi, x=Pot[0:i-1,0]))

	return np.array(JAC)

#@np.vectorize(excluded=['r', 'Pot', 'm'])

#def MyVectorize(*args, **kwargs):
#	def internal(func):
#		def retour():
#			return np.vectorize(func, *args, **kwargs)
#		return retour
#	return internal

#@MyVectorize(excluded=['r', 'Pot', 'm'])
def CalcJac(E, r, Pot, m):
	"""Calcule le jacobien permettant de passer de f(x, p) à f(E) à partir du potentiel issu de la simulation/du snapshot.

	Paramètres obligatoires :
	E   :: Énergie.
	Pot :: np.array contenant le rayon et le potentiel (cf le tableau issu de launch).
	m   :: masse d'une particule.

	Valeur de retour :
	Le jacobien à l'énergie E.
	"""
	res = list()
	for Et in E:
		tmp = Et - m*Pot
		ind = np.where( tmp >= 0.0 )
		tmp = tmp[ ind ]
		res.append(trapz( (4.0 * np.pi)**(2.0) * m * (r[ind])**(2.0) * np.sqrt( 2.0*m * tmp), x=r[ind]))
	return res

def CalcJac2(Et, r, Pot, m):
	"""Calcule le jacobien permettant de passer de f(x, p) à f(E) à partir du potentiel issu de la simulation/du snapshot.

	Paramètres obligatoires :
	E   :: Énergie.
	Pot :: np.array contenant le rayon et le potentiel (cf le tableau issu de launch).
	m   :: masse d'une particule.

	Valeur de retour :
	Le jacobien à l'énergie E.
	"""
	tmp = Et - m*Pot
	ind = np.where( tmp >= 0.0 )
	tmp = tmp[ ind ]
	return trapz( (4.0 * np.pi)**(2.0) * m * (r[ind])**(2.0) * np.sqrt( 2.0*m * tmp), x=r[ind])

vCalcJac = np.vectorize(CalcJac2, excluded=['r', 'Pot', 'm'])

def plotDistrib(Distrib, Pot, m, prefix="", fileparam="ci_param.dat", suppose = False, info=""):
	"""Calcul la distribution d'énergie théorique et la distribution de la simulation,
	puis les tracent ensemble sur le même graphe.

	Paramètres obligatoires :
	Distrib :: numpy.array contenant la distribution d'énergie sortie par le programme de Vérification (commande load.launch)
	Pot     :: numpy.array contenant le Potentiel sortie par le programme de Vérification (commande load.launch)
	m       :: float, masse d'une particule

	Paramètres optionnels :
	prefix    = ""             :: Préfixe de la simulation. En combinaison avec save, enregistre les graphiques dans un fichier pdf de nom prefix + ".pdf".
	fileparam = "ci_param.dat" :: Fichier contenant certains paramètre du Modèle.
	info      = ""             :: Quelques informations à rajouter dans le titre des graphiques.

	Valeur de retour :
	classe figure matplotlib associé au graphique.
	"""

	if fileparam != None:
		tmpjac = f_jacobien(Distrib[:,0], Pot, m)
		Theo   = f_distribtheo(Distrib[:,0], jac=tmpjac, El=Distrib[-1,0], fileparam=fileparam)

		dE     = Distrib[1,0] - Distrib[0,0]
		Theo   = Theo * dE / m

	fig    = plt.figure(prefix + "Distribution")
	if not suppose:
		fig.clf()

	ax1    = fig.add_subplot(111)

	ax1.set_title("Distribution en énergie des particules " + info)
	ax1.set_ylabel(r'$N_{\mathrm{Particules}}$')
	ax1.set_xlabel(r'Énergie en Yotta-Joule ($1 YJ = 10^{24} J$)')

	ax1.plot(Distrib[:,0]/1e24, Distrib[:,2], '+')
	if fileparam != None:
		ax1.plot(Distrib[:,0]/1e24, Theo, 'g-')
	ax1.legend(('Distribution de la simulation', ), 'upper left', shadow=True)
	if fileparam != None:
		ax1.legend(('Distribution théorique', ), 'upper left', shadow=True)

	return fig


