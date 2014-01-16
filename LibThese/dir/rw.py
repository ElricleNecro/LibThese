#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""Le module contient un set de fonction créé pour lire et écrire des données (sous forme de liste),
lisant, ou créant, un fichier sous forme de colonne.
"""

class File:
	@staticmethod
	def Read_File(cur_file, sep=' ', beval=True):
		"""Lit un fichier au format "a b c d ..." et retourne une liste de liste contenant les valeurs,
		classer par lignes et colonnes.

		cur_file  :: fichier à lire.
		sep = ' ' :: séparateur des colonnes dans le fichier.
		retour    :: une liste contenant les données.
		"""

		res = list()
		#####################
		#	Lecture du fichier de donnée à ajuster :
		################################################
		with open(cur_file, "r") as fich:
			for lig in fich:
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
					if beval:
						res.append([eval(i) for i in lig])
					else:
						res.append([i for i in lig])

		while [] in res:
			res.remove([])

		return res

	@staticmethod
	def Write_File(cur_file, data, sep=' '):
		"""Écrit un fichier au format "a b c d ..." (le delimiteur est donné par sep).
		Les donnés sont doivent être une liste.

		cur_file :: fichier à écrire.
		data     :: données à écrire.
		sep = ' ' :: séparateur à utiliser dans le fichier.
		"""

		with open(cur_file, "w") as fich:
			for i in data:
				for j in i:
					fich.write(str(j) + sep)
				fich.write("\n")

	def __init__(self, don=None, sep=' ', beval=False):
		if type(don) is type(str()):
			self.don = File.Read_File(don, sep=sep, beval=beval)
		elif don is not None:
			self.don = don
		else:
			self.don = None

	def Read(self, filename, sep=' ', beval=False):
		self.don = File.Read_File(don, sep=sep, beval=beval)

	def Save(self, filename, sep=' '):
		File.Write_File(self.don, sep=sep)
