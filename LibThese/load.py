# -*- encoding: utf-8 -*-

import os
import subprocess	          as sb
import numpy                      as np
if not os.getenv("DISPLAY"):
	import matplotlib as ml
	ml.use('PDF')
import matplotlib.pyplot          as plt
import LibPerso.ListDir.directory as dir

from   shlex		               import split
from   numpy                           import pi
from   matplotlib.backends.backend_pdf import PdfPages
from   .dir.rw                         import File

"""
Module de gestion des données de simulation.

Ce module contient un set de fonction permettant d'analyser, de calculer et de tracer des données physique de simulation Gadget2 (format de fichier Gadget-1 ou Gadget-2)
"""

TParam = { 'p_ratio': 0, 'g_ratio': 1, 'Viriel': 2, 'Tmoy': 3, 'Aniso':4 }

p2m = 3.086e16

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

	f    = rho0 * (2.0 * pi * m * sig2)**(-3.0/2.0) * (np.exp((El - E)/sig2) - 1.0)
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

def plot(Dens, Pot, Distrib, data=None, m=1.42478e+29, prefix="", aff=True, save=False, fileparam="ci_param.dat", filesave=("Densite.pdf", "Potentiel.pdf", "Anisotropie.pdf", "Temperature.pdf", "Distribution.pdf"), suppose=False, video=False, info="", nbbin=300, BoxSize=180.12*p2m, center=0.0):
	"""Trace les différentes observables des simulations d'évolution d'amas globulaire faîtes à l'aide de Gadget-2, lors de la thèse de Guillaume Plum.
	Tracé de :
		(1) la densité contre le rayon,
		(2) le potentiel contre le rayon,
		(3) l'anisotropie du système contre le rayon,
		(4) la température du système contre le rayon,
		(5) la distribution en énergie du système.

	Paramètres obligatoires :
	Dens    :: np.array contenant la densité, sortie de la fonction load.launch.
	Pot     :: np.array contenant le potentiel, sortie de la fonction load.launch.
	Distrib :: np.array contenant la distribution en énergie des particules dans le snapshot, sortie de la fonction load.launch

	Paramètres optionnels :
	data     = None        :: np.array contenant tout les informations théoriques sur le système, sortie de la fonction load.launch
	m        = 1,42478e+29 :: masse d'une particule
	save     = False       :: booléen indiquant si la fonction doit enregistrer les graphiques (l'affichage se fait tout de même)
	filesave = (...)       :: Tuple contenant les noms des fichiers dans l'ordre : ("Densite.pdf", "Potentiel.pdf", "Anisotropie.pdf", "Temperature.pdf", "Distribution.pdf")
	prefix   = ""          :: Préfixe de la simulation. En combinaison avec save, enregistre les graphiques dans un fichier pdf de nom prefix + ".pdf".
	suppose  = False       :: Doit on superposer les nouveaux graphes aux précédents !?
	info     = ""          :: Quelques informations à rajouter dans le titre des graphiques.
	"""

	if prefix:
		pp = PdfPages(prefix + '.pdf')

	fig1 = plt.figure(prefix + "Densité")
	if not suppose:
		fig1.clf()
	ax1  = fig1.add_subplot(111)

	ax1.set_title("Densité " + info)
	ax1.set_ylabel(r'$\rho(r) = m(r)/\frac{4}{3}\pi r^3$ en $kg m^{-3}$')
	ax1.set_xlabel(r'$r$ en $m$')

	ax1.loglog(Dens[:,0], Dens[:,1], '+')
	if data != None:
		ax1.loglog(data[:,0], data[:,3], 'r-')
	xaxe = ax1.get_xlim()
	yaxe = ax1.get_ylim()
	ax1.set_xlim( (1e15,xaxe[1]) )
	ax1.set_ylim( (np.min(Dens[:,1]),yaxe[1]) )
	ax1.legend(('Densité de la simulation', 'Densité théorique'), 'lower left', shadow=True)

	if save:
		if prefix:
			fig1.savefig(pp, format="pdf", transparent=True)
		else:
			fig1.savefig(filesave[0], format="pdf", transparent=True)

	if aff:
		fig1.show()
	else:
		plt.close()

	fig2 = plt.figure(prefix + "Potentiel")
	if not suppose:
		fig2.clf()
	ax2  = fig2.add_subplot(111)

	ax2.set_title("Potentiel " + info)
	ax2.set_ylabel(r'$\psi(r)$ en $km^2 s^{-2}$').set_fontsize('large')
	ax2.set_xlabel(r'$r$ en $m$')

	ax2.plot(Pot[:,0], Pot[:,1], '+')
	if data != None:
		ax2.plot(data[:,0], data[:,1], 'r-')
	ax2.legend(('Potentiel de la simulation', 'Potentiel théorique'), 'lower right', shadow=True)

	if save:
		if prefix:
			fig2.savefig(pp, format="pdf", transparent=True)
		else:
			fig2.savefig(filesave[1], format="pdf", transparent=True)

	if aff:
		fig2.show()
	else:
		plt.close()

	fig3 = plt.figure(prefix + "Anisotropie")
	if not suppose:
		fig3.clf()
	ax3  = fig3.add_subplot(111)

	ax3.set_title("Anisotropie " + info)
	ax3.set_ylabel(r'$\beta$')
	ax3.set_xlabel(r'$r$ en $m$')

	ax3.plot(Dens[:,0], Dens[:,3])
	ax3.legend(('Anisotropie',), 'lower center', shadow=True)

	if save:
		if prefix:
			fig3.savefig(pp, format="pdf", transparent=True)
		else:
			fig3.savefig(filesave[2], format="pdf", transparent=True)

	if aff:
		fig3.show()
	else:
		plt.close()

	fig4 = plt.figure(prefix + "Température")
	if not suppose:
		fig4.clf()
	ax4  = fig4.add_subplot(111)

	ax4.set_title("Température " + info)
	ax4.set_xlabel(r'$r$ en $m$')
	ax4.set_ylabel(r'$T(r)$ en $km^2 s^{-2}$')

	ax4.loglog(Dens[:,0], Dens[:,2])
	ax4.legend(('Température',), 'lower left', shadow=True)

	if save:
		if prefix:
			fig4.savefig(pp, format="pdf", transparent=True)
		else:
			fig4.savefig(filesave[3], format="pdf", transparent=True)

	if aff:
		fig4.show()
	else:
		plt.close()

	fig5 = plotDistrib(Distrib, Pot, m, fileparam=fileparam, info=info)
	if save:
		if prefix:
			fig5.savefig(pp, format="pdf", transparent=True)
		else:
			fig5.savefig(filesave[4], format="pdf", transparent=True)

	if aff:
		fig5.show()
	else:
		plt.close()

	if aff:
		plt.show()
	else:
		plt.close()

	if prefix:
		PlotCarte(prefix=prefix, pp=pp, save=save, aff=aff, video=video, info=info, nbbin=nbbin, BoxSize=BoxSize, center=center)
	else:
		PlotCarte(prefix=prefix, save=save, aff=aff, video=video, info=info, nbbin=nbbin, BoxSize=BoxSize, center=center)

	if prefix:
		pp.close()

def PlotParam(name="TimeParam.dat", prefix="", Param=None, aff=True, save=False, info="", filelist=("Axial Ratio", "Viriel", "Temperature", "Anisotropie", "Rayon", "Vitesse du centre"), tmax=0.1, UT=9.77894e8, Td=8.02191e6):
	if Param is None:
		Param = np.array(File.Read_File(name))

	pp = None
	if prefix:
		pp = PdfPages(prefix + '.pdf')


	#info = " temps : %g"%( tmax * (i+1) * UT / (len(liste) * Td) )
	x    = np.arange(0, len(Param), 1)
	x    = tmax * (x+1) * UT / (len(x) * Td)

	fig1 = plt.figure(prefix + "Axial Ratio")
	axAR = fig1.add_subplot(111)

	axAR.set_title("Axial Ratio " + info)
	axAR.set_ylabel(r'Axial ratio')
	axAR.set_xlabel(r'Time (temps dynamique)')

	axAR.axis([0, tmax * (len(Param)+1) * UT / (len(x) * Td), 0.75, 1.2])

	print(Param)
	print(len(Param), len(x))

	axAR.plot(x, Param[:,1], 'r-', x, Param[:,2], 'b-')
	axAR.legend(('Petit axe', 'Grand axe'), 'lower right', shadow=True, fancybox=True)

	if save or pp is not None:
		if prefix and pp is not None:
			fig1.savefig(pp, format="pdf", transparent=True)
		else:
			fig1.savefig(prefix + filelist[0] + ".pdf", format="pdf", transparent=True)

	if aff:
		fig1.show()
	else:
		plt.close()

	fig2 = plt.figure(prefix + "Rapport du Viriel")
	axV  = fig2.add_subplot(111)

	axV.set_title("Rapport du Viriel " + info)
	axV.set_xlabel(r'Time (temps dynamique)')
	axV.set_ylabel(r'Rapport du Viriel')

	axV.axis([0, tmax * (len(Param)+1) * UT / (len(x) * Td), -1.5, -0.5])

	axV.plot(x, Param[:,3], 'r-')
	axV.legend(('Rapport du Viriel', ), 'lower right', shadow=True, fancybox=True)

	if save or pp is not None:
		if prefix and pp is not None:
			fig2.savefig(pp, format="pdf", transparent=True)
		else:
			fig2.savefig(prefix + filelist[1] + ".pdf", format="pdf", transparent=True)

	if aff:
		fig2.show()
	else:
		plt.close()

	fig3 = plt.figure(prefix + "Température moyenne")
	axTm = fig3.add_subplot(111)

	axTm.set_title("Température moyenne " + info)
	axTm.set_xlabel(r'Time (temps dynamique)')
	axTm.set_ylabel(r'Température moyenne en $km^2 s^{-2}$')

	axTm.axis([0, tmax * (len(Param)+1) * UT / (len(x) * Td), np.min(Param[:,4]) - 0.1*np.min(Param[:,4]), np.max(Param[:,4]) + np.max(Param[:,4])*0.1])

	axTm.plot(x, Param[:,4], 'r-')
	axTm.legend(('Température moyenne', ), 'lower right', shadow=True, fancybox=True)

	if save or pp is not None:
		if prefix and pp is not None:
			fig3.savefig(pp, format="pdf", transparent=True)
		else:
			fig3.savefig(prefix + filelist[2] + ".pdf", format="pdf", transparent=True)

	if aff:
		fig3.show()
	else:
		plt.close()

	fig4 = plt.figure(prefix + "Anisotropie")
	axA  = fig4.add_subplot(111)

	axA.set_title("Anisotropie " + info)
	axA.set_ylabel(r'Anisotropie')
	axA.set_xlabel(r'Time (temps dynamique)')

	axA.axis([0, tmax * (len(Param)+1) * UT / (len(x) * Td), -0.5, 0.5])

	axA.plot(x, Param[:,5], 'r-')
	axA.legend(('Anisotropie', ), 'lower right', shadow=True, fancybox=True)

	if save or pp is not None:
		if prefix and pp is not None:
			fig4.savefig(pp, format="pdf", transparent=True)
		else:
			fig4.savefig(prefix + filelist[3] + ".pdf", format="pdf", transparent=True)

	if aff:
		fig4.show()
	else:
		plt.close()

	fig5 = plt.figure(prefix + "Rayon")
	fig5.subplots_adjust(hspace=2.0)
	axR  = fig5.add_subplot(111)

	axR.set_title("Rayon " + info)
	axR.set_xlabel(r'Time (temps dynamique)')
	axR.set_ylabel(r'Rayon $m$')

	axR.axis(xmax=tmax * (len(Param)+1) * UT / (len(x) * Td))

	axR.plot(x, Param[:,6], 'r-', x, Param[:,7], 'b-', x, Param[:,8], 'g-')
	leg = axR.legend((r'Rayon à $10%$', r'Rayon à $50%$', r'Rayon à $90%$'), 'lower left', bbox_to_anchor=(0., 0.02, 1., 0.102), ncol=3, mode="expand", fancybox=True)
	leg.get_frame().set_facecolor("wheat")
	leg.get_frame().set_alpha(0.7)

	if save or pp is not None:
		if prefix and pp is not None:
			fig5.savefig(pp, format="pdf", transparent=True)
		else:
			fig5.savefig(prefix + filelist[4] + ".pdf", format="pdf", transparent=True)

	if aff:
		fig5.show()
	else:
		plt.close()

	fig6 = plt.figure(prefix + "Vitesse du centre de densité")
	axC  = fig6.add_subplot(111)

	axC.set_title("Vitesse du centre de densité " + info)
	axC.set_ylabel(r'Vitesse $km\,s^{-1}$')
	axC.set_xlabel(r'Time (temps dynamique)')

	axC.axis([0, tmax * (len(Param)+1) * UT / (len(x) * Td), -0.5, 0.5])

	axC.plot(x, Param[:,5], 'r-')
	axC.legend(('Vitesse du centre', ), 'lower right', shadow=True, fancybox=True)

	if save or pp is not None:
		if prefix and pp is not None:
			fig6.savefig(pp, format="pdf", transparent=True)
		else:
			fig6.savefig(prefix + filelist[5] + ".pdf", format="pdf", transparent=True)

	if aff:
		fig6.show()
	else:
		plt.close()


	if prefix:
		pp.close()

def PlotCarte(name="Particule-it.dat", Part=None, prefix="", pp=None, save=False, aff=True, video=False, info="", nbbin=300, arrow=None, BoxSize=180.12*p2m, center=[0.0,0.0,0.0]): #3.086e16, center=0.0): #180.12*3.086e16/2.0):
	"""Trace la carte des particule sur les plans xOy, xOz et yOz.

	Paramètres optionnels :
	name   = "Particule-it.dat" :: Nom du fichier à charger.
	prefix = ""		    :: Chaîne à ajouter devant le nom des fichiers
	pp     = None		    :: Si un fichier à déjà été ouvert et que l'on veut écrire à sa suite.
	save   = False		    :: Si l'on doit écrire dans un fichier les graphiques.
	aff    = True		    :: Doit on afficher les graphiques.
	video  = False		    :: Enregistre les cartes au format png dans le but de créer une vidéo avec un logiciel comme mencoder.
	info   = ""                 :: Quelques informations à rajouter dans le titre des graphiques.
	arrow  = None		    :: Trace un flèche du point arrow[0] au point arrow[1]. Les coordonnées sont associées aux entiers : x : 0, y : 1, z : 2.
	center = [ 0.0, 0.0, 0.0 ]  :: Liste contenant les coordonnées (x, y, z) sur lesquelles centré l'objet.
	"""
	if Part is None:
		Part   = np.array(File.Read_File(name))

	#FieldRange = [[center - BoxSize/2.0, center + BoxSize/2.0], [center - BoxSize/2.0, center + BoxSize/2.0]]

	Carte1 = plt.figure(prefix + "Carte xOy")
	axCar1 = Carte1.add_subplot(111)

	axCar1.set_title("Carte xOy " + info)
	axCar1.set_xlabel(r'$x$ en $m$')
	axCar1.set_ylabel(r'$y$ en $m$')

	hist, X, Y = np.histogram2d(Part[:,0], Part[:,1], bins=nbbin)#, range=FieldRange)

	axCar1.axis([np.min(Part[:,0]), np.max(Part[:,0]), np.min(Part[:,1]), np.max(Part[:,1])])
	tmp = axCar1.pcolor(X, Y, hist.T)
	Carte1.colorbar(tmp)
	if arrow is not None:
		arr1 = plt.Arrow(arrow[0,0], arrow[0,1], arrow[1,0] - arrow[0,0], arrow[1,1] - arrow[0,1], color='k', figure=Carte1)
		axCar1.add_patch(arr1)

	if pp is not None:
		if prefix and pp is not None:
			Carte1.savefig(pp, format="pdf", transparent=True)
		else:
			Carte1.savefig(prefix + "Carte_xOy.pdf", format="pdf", transparent=True)
	if video:
		Carte1.savefig(prefix + "Carte_xOy.png", format="png", transparent=True)

	if aff:
		Carte1.show()
	else:
		plt.close()

	Carte2 = plt.figure(prefix + "Carte xOz")
	axCar2 = Carte2.add_subplot(111)

	axCar2.set_title("Carte xOz " + info)
	axCar2.set_xlabel(r'$x$ en $m$')
	axCar2.set_ylabel(r'$z$ en $m$')

	hist, X, Y = np.histogram2d(Part[:,0], Part[:,2], bins=nbbin)#, range=FieldRange)

	axCar2.axis([np.min(Part[:,0]), np.max(Part[:,0]), np.min(Part[:,2]), np.max(Part[:,2])])
	tmp = axCar2.pcolor(X, Y, hist.T)
	Carte2.colorbar(tmp)
	if arrow is not None:
		arr2 = plt.Arrow(arrow[0,0], arrow[0,2], arrow[1,0] - arrow[0,0], arrow[1,2] - arrow[0,2], color='k', figure=Carte2)
		axCar2.add_patch(arr2)

	if pp is not None:
		if prefix and pp is not None:
			Carte2.savefig(pp, format="pdf", transparent=True)
		else:
			Carte2.savefig(prefix + "Carte_xOz.pdf", format="pdf", transparent=True)

	if video:
		Carte2.savefig(prefix + "Carte_xOz.png", format="png", transparent=True)

	if aff:
		Carte2.show()
	else:
		plt.close()

	Carte3 = plt.figure(prefix + "Carte yOz")
	axCar3 = Carte3.add_subplot(111)

	axCar3.set_title("Carte yOz " + info)
	axCar3.set_xlabel(r'$y$ en $m$')
	axCar3.set_ylabel(r'$z$ en $m$')

	hist, X, Y = np.histogram2d(Part[:,1], Part[:,2], bins=nbbin)#, range=FieldRange)

	axCar3.axis([np.min(Part[:,1]), np.max(Part[:,1]), np.min(Part[:,2]), np.max(Part[:,2])])
	tmp = axCar3.pcolor(X, Y, hist.T)
	Carte3.colorbar(tmp)
	if arrow is not None:
		arr3 = plt.Arrow(arrow[0,1], arrow[0,2], arrow[1,1] - arrow[0,1], arrow[1,2] - arrow[0,2], color='k', figure=Carte3)
		axCar3.add_patch(arr3)

	if save or pp is not None:
		if pp is not None:
			Carte3.savefig(pp, format="pdf", transparent=True)
		else:
			Carte3.savefig(prefix + "Carte_yOz.pdf", format="pdf", transparent=True)

	if video:
		Carte3.savefig(prefix + "Carte_yOz.png", format="png", transparent=True)

	if aff:
		Carte3.show()
	else:
		plt.close()


def DistribVit(filename, prefix="", save=False, filesave="DistribVit.pdf", gaussianfits=False, indmax=3, offset=4):
	"""Trace les distributions en vitesses (v_x, v_y, v_z) des particules.

	Paramètres obligatoires :
	filename :: Nom du fichier contenant les positions-vitesses des particules au format colonne : x, y, z, r, v_x, v_y, v_z, v.

	Paramètres optionnels :
	save     = False            :: booléen valant True si il faut sauvegarder le graphique sous forme de fichier.
	filesave = "DistribVit.pdf" :: Nom du fichier sous lequel sauvegarder le graphique si save == True.
	"""

	if isinstance(filename, str):
		Part = np.array(File.Read_File(filename), dtype=np.float64)
	else:
		Part = filename
	mean = np.mean(Part, axis=0, dtype=np.float64)
	sig  = np.std(Part, axis=0, dtype=np.float64)

	textstr = "mean : $%g$\nstd     : $%g$"
	labels  = [r'$v_x$',r'$v_y$',r'$v_z$', r'$v$']

	# new style method 2; use an axes array
	fig, axs = plt.subplots(indmax, 1, num=prefix + "Distribution des vitesses", sharex=True)

	for i in range(0, indmax):
		nb= axs[i].hist(Part[:,i+offset], bins=100, label=labels[i], alpha=0.7)
		if gaussianfits:
			fit = lambda t : nb[0].max()*np.exp(-(t-mean[i+offset])**2/(2*sig[i+offset]**2))
			axs[i].plot(nb[1], fit(nb[1]), 'r-', label='Gaussian fit')

		leg = axs[i].legend(loc='upper right', shadow=False)
		leg.get_frame().set_alpha(0.5)
		# these are matplotlib.patch.Patch properies
		props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

		# place a text box in upper left in axes coords
		axs[i].text(0.05, 0.95, textstr%(mean[i+offset], sig[i+offset]),
				transform=axs[i].transAxes, fontsize=14,
			        verticalalignment='top', bbox=props)

		print(labels[i] + ", mean : %g, std : %g"%(mean[i+offset], sig[i+offset]))

	if save:
		plt.savefig("DistribVit.pdf", format="pdf")

#	plt.show()

def plotpot(Pot, Brute, data):
	"""Trace le potentiel tel que calculé par les fonction load.launch, et load.BruteForce, ainsi que le potentiel théorique.

	Paramètres obligatoires :
	Pot   :: np.array contenant le potentiel calculé par la fonction laod.launch.
	Brute :: np.array contenant le potentiel calculé par la fonction load.BruteForce.
	data  :: np.array contenant les données théoriques retourné par la fonction load.launch
	"""
	fig2 = plt.figure("Tous les potentiel")
	ax2  = fig2.add_subplot(111)

	ax2.set_title("Potentiel")
	ax2.set_ylabel(r'$\psi(r)$').set_fontsize('large')
	ax2.set_xlabel(r'$r$')

	ax2.plot(Pot[:,0], Pot[:,1], 'b+', Brute[:,0], Brute[:,1], 'g+', data[:,0], data[:,1], 'r-')
	ax2.legend(('Potentiel de la simulation', 'Potentiel Force Brute', 'Potentiel théorique'), 'lower right', shadow=True)

	plt.show()

def GetNum(string, sep="_"):
	return string.split(sep)[-1]

def SuperposDensity(list_file, title, xlim=[0.07, 7], ylim=None, Other=""):
	"""Récupère les densité logarithmique des fichiers données en argument et les traces en les superposant.
	list_file        :: Liste des fichiers à tracer.
	title            :: Titre du graphique.
	xlim = [0.07, 7] :: Borne du graphique en x.
	ylim = None      :: Borne du graphique en y. Utilise par défaut les maximum et minimum sur toutes les courbes
	Other = ""       :: Paramètres en plus à passer au programme de Vérification.
	"""
	m = []
	r = []
	for fich in list_file:
		tmp1, tmp2, _, _, _ = launch(fich, rsoft=0.0, opang=0.5, filetheo=None, Rmax=-1.0, vexec="/home/plum/Documents/These/src/VerificationTree/Verif", Other=Other)
		m.append(tmp1)
		r.append(tmp2)

	Sup = plt.figure("Superposition")
	Sup.clf()

	ax = Sup.add_subplot(111)

	ax.set_title(title)
	ax.set_xlabel(r'$\frac{r}{r_{50}}$')
	ax.set_ylabel(r'$\rho(r)$')

	max = None
	min = None
	for i, gr in enumerate(r):
		#r50 = m[i][int(len(m[i])/2), 0]
		ax.loglog((10.0**gr[:,4]), gr[:,5], "-")

		if max is None or gr[:,5].max() > max:
			max = gr[:,5].max()

		if min is None or gr[:,5].min() > min:
			min = gr[:,5].min()

	ax.grid()
	ax.set_xlim(xlim)
	if ylim is not None:
		ax.set_ylim(ylim)
	else:
		ax.set_ylim(min, max)

	from matplotlib.font_manager import FontProperties
	fontP = FontProperties()
	fontP.set_size('small')
	leg = ax.legend(list_file, "best", prop = fontP, fancybox=True)
	leg.get_frame().set_facecolor("wheat")
	leg.get_frame().set_alpha(0.7)

	Sup.savefig(os.path.splitext(os.path.basename(list_file[0]))[0] + ".pdf", format="pdf")
	Sup.show()

	return r, m

	#leg = ax.legend((os.path.splitext(os.path.basename(fich))[0], ), 'best', fancybox=True, shadow=False) #'lower left', bbox_to_anchor=(0., 0.02, 1., 0.102), ncol=3, mode="expand", fancybox=True)
	#bbox_inches='tight'

if __name__ == "__main__":
#	truc = launch("amas-king.dat")
	Mass, Dens, Pot, Simu, Distrib, Ener = ld.launch("amas-king.dat", rsoft=0.00, nbbin=100)
	ld.plot(Dens, Pot, Simu, Distrib, m=m, save=True)

