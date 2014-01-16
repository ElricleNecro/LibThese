# -*- encoding: utf-8 -*-

import os
import subprocess	          as sb
import LibPerso.ListDir.directory as dir

from   shlex		               import split
from   .dir.rw			       import File

valexec = "valgrind --tool=memcheck --num-callers=40 --leak-check=full --track-origins=yes --show-reachable=yes ./../../Verif"

def exec_list(motif, G=6.67e-11, Rmax=2.92668e+17, rsoft=0.0790899, nbbin=100, vexec="Verif", periodic=False, filetheo="King_dim.log", fileparam="ci_param.dat", exclude=None, retour=False, video=False, tmax=0.1, UT=9.77894e8, Td=8.02191e6, opang=0.0, Other=""):
	"""
	Cette fonction appelle la fonction load.launch sur tous les fichiers contenant la chaîne motif, les tracent dans un fichier pdf du même nom que le snapshot
	et stock les données dans un dictionnaire.

	Paramètres obligatoires :
	motif :: Motif permettant la recherche de fichier snapshot.

	Paramétre optionnel :
	G        = 6.67e-11        :: Valeur de la constante de la gravitation dans le système d'unité du snapshot.
	Rmax     = 2.92668e+17     :: Rayon au-delà duquel les particules sont ignorés.
	rsoft    = 0.0790899       :: Paramètre de lissage à utiliser lors du calcul du potentiel, en parsec.
	nbbin    = 100             :: Nombre de bin à utiliser pour les quantités nécessitant des histogrammes (fonction de distribution, densité, jacobien, ...).
	vexec    = "Verif"         :: Chemin vers l'exécutable du programme.
	filetheo = "King_dim.log"  :: Fichier contenant les données théoriques au format du programme de conditions initiales. Mettre à None s'il n'y a aucun fichier à lire.
	exclude  = None		   :: Expression régulière/motif correspondant aux fichiers à exclure du traitement.
	retour   = False           :: Retourner les tableaux de données de chaque fichiers ?
	video    = False           :: Enregistrement des cartes au format png dans le but d'en faire une vidéo.

	Valeur de retour :
	si retour vaut True :
		Liste contenant les noms de fichier exécuté.
		Dictionnaire contenant résultat de chaque simulation.
	sinon :
		Rien du tout.
	"""
	if os.path.isfile(motif):
		liste = [motif]
	else:
		liste = dir.SearchFile(motif, exclude=exclude)
		liste.sort()
	print(liste)

	if retour:
		res = dict()

	for i, nm in enumerate(liste):
		info = " temps : %g"%( tmax * (i+1) * UT / (len(liste) * Td) )
		print(info)
		if filetheo is not None:
			Mass, Dens, Pot, Distrib, Etot, Theo = launch(nm, rsoft=rsoft, G=G, opang=opang, Rmax=Rmax, nbbin=nbbin, vexec=vexec, filetheo=filetheo, periodic=periodic, Other=Other)
			plot(Dens, Pot, Distrib, data=Theo, m=Mass[0,1], prefix=nm, aff=False, save=True, fileparam=fileparam, video=video, info=info)
			if retour:
				res[nm] = (Mass, Dens, Pot, Distrib, Etot, Theo)
			del Mass, Dens, Pot, Distrib, Etot, Theo
		else:
			Mass, Dens, Pot, Distrib, Etot = launch(nm, rsoft=rsoft, G=G, Rmax=Rmax, opang=opang, nbbin=nbbin, vexec=vexec, filetheo=filetheo, periodic=periodic, Other=Other)
			plot(Dens, Pot, Distrib, m=Mass[0,1], prefix=nm, aff=False, save=True, fileparam=fileparam, video=video, info=info)
			if retour:
				res[nm] = (Mass, Dens, Pot, Distrib, Etot)
			del Mass, Dens, Pot, Distrib, Etot

	if retour:
		return (liste, res)

class DataAnalysis:
	"""Exécute le programme d'analyse sur les données ainsi crée."""

	def __init__(self, filename, G=6.67e-11, Rmax=2.92668e+17, rsoft=0.0790899, opang=0.0, nbbin=100, types=4, periodic=False, vexec="Verif", SeeErr = True, SeeOut = True, filetheo="King_dim.log", Other=""):
		self.filename = filename
		self.G        = G
		self.Rmax     = Rmax
		self.rsoft    = rsoft
		self.opang    = opang
		self.nbbin    = nbbin
		self.types    = types
		self.periodic = periodic
		self.vexec    = vexec
		self.SeeErr   = SeeErr
		self.SeeOut   = SeeOut
		self.filetheo = filetheo
		self.Other    = Other

	def launch(filename, G=6.67e-11, Rmax=2.92668e+17, rsoft=0.0790899, opang=0.0, nbbin=100, types=4, periodic=False, vexec="Verif", SeeErr = True, SeeOut = True, filetheo="King_dim.log", Other=""):
		"""Lance le code. Retourne les résultats sous forme de np.array.

		ATTENTION : Modification de l'interface du programme. La fonction peut arrêter de fonctionner à tout moment.

		Paramètre obligatoire :
		filename :: nom du fichier snapshot au format gadget-1 ou gadget-2

		Paramètres optionnels :
		G        = 6.67e-11        :: Valeur de la constante de la gravitation dans le système d'unité du snapshot.
		Rmax     = 2.92668e+17     :: Rayon au-delà duquel les particules sont ignorés.
		rsoft    = 0.0790899       :: paramètre de lissage à utiliser lors du calcul du potentiel, en parsec.
		nbbin    = 100             :: nombre de bin à utiliser pour les quantités nécessitant des histogrammes (fonction de distribution, densité, jacobien, ...).
		vexec    = "./../../Verif" :: chemin vers l'exécutable du programme.
		filetheo = "King_dim.log"  :: fichier contenant les données théoriques au format :., non chargé si 'None'.
		SeeErr   = True		   :: Voir la sortie d'erreur.
		SeeOut   = True            :: Voir la sortie standard.

		Valeurs de retour :
		np.array contenant la fonction de masse avec le rayon.
		np.array contenant la densité avec le rayon.
		np.array contenant le potentiel avec le rayon.
		np.array contenant les données théoriques du fichier filetheo.
		np.array contenant la fonction de distribution en énergie et son jacobien (foireux => sous-estimé).
		np.array contenant l'énergie potentiel, cinétique et totale avec le rayon.
		"""

		print("G :: %g\nRmax :: %g\nSoftening :: %g\nNbBin :: %d\n"%(G, Rmax, rsoft, nbbin))

		if SeeErr:
			tmperr = None
		else:
			tmperr = sb.PIPE
		if SeeOut:
			tmpout = None
		else:
			tmpout = sb.PIPE

		if periodic:
			OptPer = "-p"
		else:
			OptPer = ""

		#make = sb.Popen(cmd, stdout=tmpout, stderr=tmperr)
		os.system(vexec + " " + filename + " -n " + str(nbbin) + " -s " + str(rsoft) + " -R " + str(Rmax) + " -o " + str(opang) + " -t " + str(types) + " " + OptPer + " " + Other)
		print(vexec + " " + filename + " -n " + str(nbbin) + " -s " + str(rsoft) + " -R " + str(Rmax) + " -o " + str(opang) + " -t " + str(types) + " " + OptPer + " " + Other)
	#	out, err = make.communicate()
	#
	#	out = out.decode("utf-8").split('\n')
	#	err = err.decode("utf-8").split('\n')

	#	print("Sortie standard :", out, sep='\n')
	#	print("Sortie d'erreur :", err, sep='\n')

		Mass      = File.Read_File("Masse.dat")
		Dens      = File.Read_File("Densite.dat")
		Potentiel = File.Read_File("Potentiel-tc.dat")
		Distrib   = File.Read_File("Distribution.dat")
		Energie   = File.Read_File("Energie.dat")
		if filetheo:
			data      = File.Read_File(filetheo)

		Potentiel.sort(key=lambda t: t[0])

		if filetheo:
			return (	np.array(Mass, dtype=np.float64),
					np.array(Dens, dtype=np.float64),
					np.array(Potentiel, dtype=np.float64),
					np.array(Distrib, dtype=np.float64),
					np.array(Energie, dtype=np.float64),
					np.array(data, dtype=np.float64)
				)
		else:
			return (	np.array(Mass, dtype=np.float64),
					np.array(Dens, dtype=np.float64),
					np.array(Potentiel, dtype=np.float64),
					np.array(Distrib, dtype=np.float64),
					np.array(Energie, dtype=np.float64)
				)

def BruteForce(filename, G=6.67e-11, Rmax=2.92668e+17, rsoft=0.0790899, nbbin=100, vexec="./../../BruteForce"):
	"""Lance le code. Retourne les résultats sous forme de np.array.
	"""

	print("G :: %g\nRmax :: %g\nSoftening :: %g\nNbBin :: %d\n"%(G, Rmax, rsoft, nbbin))
	os.system(vexec + " " + filename + " " + str(G) + " " + str(Rmax) + " " + str(rsoft) + " " + str(nbbin))

	Potentiel = Read_File("Potentiel-bf.dat")

	Potentiel.sort(key=lambda t: t[0])

	return np.array(Potentiel, dtype=np.float64)


