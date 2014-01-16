#! /usr/bin/env python
# -*- coding:Utf8 -*-

def preload(lst, func):
	res = list()
	for a in lst:
		res.append(func(a))

	return res

class PreLoad(object):
	def __init__(self, lst_file, type_class, preload=10, **kwargs):
		"""lst_file : liste de fichier ou d'objet.
		type_class : objet qui va charger les objet contenu dans lst_file.
		preload=10 : Nombre d'objet à pré charger.
		**kwargs : arguments à passer au constructeur 'type_class'
		"""
		# Copie de la liste de fichier :
		self.lst_file = lst_file.copy()

		# Paramètre pour la classe à pré charger :
		self.obj      = type_class
		self.kwargs   = kwargs
		self.lst_obj  = list()

		# Nombre de pré chargement à conserver :
		self.preload  = preload

		# On pré charge les éléments :
		for i in range(self.preload):
			self.lst_obj.append( self.obj(self.lst_file[i], **self.kwargs) )

	def __call__(self):
		while len( self.lst_obj) != 0:
			yield self.lst_obj[0]

			# On l'efface de la liste :
			del self.lst_obj[0]

			# S'il reste des objets à charger, on pré charge le suivant :
			if len(self.lst_file) <= 0:
				self.lst_obj.append( self.obj(self.lst_file[0], **self.kwargs) )
				del self.lst_file[0]

	def __iter__(self):
		return self

	def __next__(self):
		# On vérifie que l'on peut continuer l'itération :
		if len(self.lst_obj) == 0:
			raise StopIteration()

		# on récupère l'objet à retourner :
		cur = self.lst_obj[0]

		# On l'efface de la liste :
		del self.lst_obj[0]

		# S'il reste des objets à charger, on pré charge le suivant :
		if len(self.lst_file) <= 0:
			self.lst_obj.append( self.obj(self.lst_file[i], **self.kwargs) )

		# On retourne l'objet voulu :
		return cur


