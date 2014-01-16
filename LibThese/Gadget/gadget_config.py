# -*- encoding: utf-8 -*-

from   LibThese.plot                   import Read_File

class GadgetConfig:
	list_type = ["SofteningGas", "SofteningHalo", "SofteningDisk", "SofteningBulge", "SofteningStars", "SofteningBndry"]
	def __init__(self, filename="ci.dat", paramname="ci_param.dat", unit_pos=3.086e16, unit_vit=1.0):
		"""Créé une instance de la classe et initialise les champs aux valeurs données avec les paramètres.

		filename  = "ci.dat"       : Nom du fichier de condition initiale.
		paramname = "ci_param.dat" : Nom du fichier de paramètre donné par le programme de génération des conditions initiales.
		unit_pos  = 3.086e16       : Facteur de conversion de l'unité de position du fichier de condition initiale vers les mètres.
		unit_vit  = 1.0            : Facteur de conversion de l'unité de vitesse du fichier de condition initiale vers les mètres.
		"""
		self.param = Read_File(paramname)
		self.File = dict()
		self.File["BoxSize"] = self.param[6][0]
		#self.
		pass

	def write(self, name="fich"):
		with open(name, "w") as fich:
			pass
			#fich.write()

	def set(self):
		pass
