#! /usr/bin/env python
# -*- coding:Utf8 -*-

import sqlite3
import numpy as np

#from LibPerso import typecheck as tc
import LibPerso.typecheck as tc
from LibThese.Utils import Plot as pt

tables = {
	"id_simu": ["nom", "id"],
	"energie": ["id", "r", "ec", "epot", "etot"],
	"masse":   ["id", "r", "m"],
	"densite": ["id", "bin_rg", "rho", "t", "aniso"],
	"densite_log": ["id", "bin_rg", "l_densite"],
	"distribution": ["id", "e", "distribution"]
}

class DataDB(pt.Plot):
	"""Classe récupérant les données x, y à partir d'une base de donnée !
	"""
	def __init__(self, *data, **kwargs):
		"""Constructeur :
				-> *data*   : nom de la base de donnée à passer ou 2 numpy.array pour les données x et y à tracer.
				-> *kwargs* : paramètre du plot et valeur pour la lecture dans la base de donnée.
						- SELECT : obligatoire : tuple des champs à récuperer dans la base SQLite3,
						- FROM   : obligatoire, de quel table prendre les données,
						- WHERE  : conditions à appliquer pour filtrer les données,
						- ORDER  : comment ordonner les données.
		"""
		if len(data) == 1:
			nextd = self._get_from_db(data[0], **kwargs)
		elif len(data) == 2:
			self._x, self._y = data[0], data[1]
			if len(self._x) != len(self._y):
				raise ValueError(str(len(self._x)) + " != " + str(len(self._y)))
		else:
			raise ValueError(len(data))
		super(DataDB, self).__init__(**nextd)

	def __iter__(self):
		return zip(self._x, self._y)

	@tc.typecheck
	def _get_from_db(self, name, **kwargs):
		if isinstance(name, str):
			conn = sqlite3.connect(name)
			cur  = conn.cursor()
		elif isinstance(name, sqlite3.Cursor):
			cur  = name
		else:
			raise TypeError(type(name))
		if len(kwargs["SELECT"]) != 2:
			raise ValueError("This class works with 2 dimensionals array : " + \
						len(kwargs["SELECT"]))

		req = ""
		#req   = "SELECT " + kwargs["SELECT"][0] + ", " + kwargs["SELECT"][1] + " "
		#del kwargs["SELECT"]
		for k in [ "SELECT", "FROM", "WHERE", "ORDER" ]:
			req += k + " " + str(kwargs[k]).replace('\'', '').replace('(', '').replace(')', '') + " "
			del kwargs[k]

		print(req)
		cur.execute(req)
		tmp = np.array(cur.fetchall())
		self._x = tmp[:,0]
		self._y = tmp[:,1]

		return kwargs

	@property
	def x(self):
		return self._x
	@x.setter
	@tc.typecheck
	def x(self, val : tc.either(np.array, list)):
		self._x = val

	@property
	def y(self):
		return self._y
	@y.setter
	@tc.typecheck
	def y(self, val : tc.either(np.array, list)):
		self._y = val

if __name__ == '__main__':
	import argparse as ap
	args = ap.ArgumentParser()
