#! /usr/bin/env python
# -*- coding:Utf8 -*-

################
#	Import :
###########################################


import numpy         as np
#import pandas.io.sql as psql

##############################
#	Exception Definition :
###########################################


class ConstError(Exception):
	def __init__(self, name):
		self.name = str(name)
	def __str__(self):
		return repr("Unable to modify: " + self.name)

class TableError(Exception):
	def __init__(self, name):
		self.name = str(name)
	def __str__(self):
		return repr("No table " + self.name + " found")

##########################
#	Class Definition :
###########################################


class Const(object):
	"""Classe permettant de créer et d'utiliser des variables constantes !
	"""
	def __init__(self, data):
		self.__dict__.update(data)

	def __setattr__(self, nom, val):
		if nom in self.__dict__:
			raise ConstError(nom)
		self.__dict__[nom] = val

	#def __getattr__(self, nom):
		#if nom in self.__dict__[nom]:
			#return self.__dict__[nom]
		#else:
			#return None

	def __call__(self, nom=None):
		if nom is not None:
			return self.__dict__[nom]
		else:
			return self.__dict__.copy()

	def __repr__(self):
		return "<Const: " + str(self.__dict__) + ">"

	def __str__(self):
		return str(self.__dict__)

SQLite3Orga = Const({
	'Movement'     : ['id', 'type', 'x', 'y', 'z', 'vx', 'vy', 'vz'],
	'densite'      : ['id', 'type', 'bin_rg', 'rho', 't', 'aniso'],
	'densite_log'  : ['id', 'type', 'bin_rg', 'l_densite'],
	'distribution' : ['id', 'type', 'e', 'distribution'],
	'energie'      : ['id', 'type', 'r', 'ec', 'epot', 'etot'],
	'id_simu'      : ['nom', 'id', 'time'],
	'potentiel'    : ['id', 'type', 'r', 'pot'],
	'masse'        : ['id', 'type', 'r', 'm'],
	'timeparam'    : ['id', 'type', 'time', 'p_ratio', 'g_ratio', 'viriel', 'tmoy', 'aniso', 'r10', 'r50', 'r90', 'x', 'y', 'z', 'vx', 'vy', 'vz']
	}
)

class PandasDB(object):
	"""Class for getting information from database generated by VerificationTree Code.
	"""

	def __init__(self, db, table_dict = SQLite3Orga):
		if isinstance(db, str):
			import sqlite3
			self._db = sqlite3.connect(db)
		elif isinstance(db, sqlite3.Connection):
			self._db = db
		else:
			raise TypeError

		self.cur = db.cursor()

		self.tables = table_dict

	def Get_TimeParam(self, col : list = None):
		# Verifying than timeparam exist in the database :
		if "timeparam" not in self.tables:
			raise TableError("timeparam")

		# Preparing the wanted col if not set :
		if col is None:
			col = self.tables["timeparam"]

		# Request building :

#############################
#	Function Definition :
###########################################


def VConcate(a, b):
	"""Ajoute les colonnes de b à a.

	Paramètres obligatoires :
	a :: np.array à concaténer.
	b :: np.array à concaténer avec a.

	Valeur de retour :
	np.array contenant les tableaux concaténé.
	"""
	return np.vstack( (a.T, b.T) ).T

def toRad(a):
	return a * np.pi / 180.

def toDeg(a):
	return a * 180. / np.pi

def GetTimeParam():
	import InitialCond.Gadget as gad
	from LibThese.Carte import DensityCarte
	import h5py

	f = h5py.File("data/Test_4.hdf5", "r")

	res = np.array( [] )

	for a in f.keys():
		tmp = f[a]["timeparam"][:]
		res = np.resize(res, (res.shape[0] + 1, tmp.shape[1]))
		res[ res.shape[0]-1, : ] = tmp[0, :]

	return res


def Softening(NbPart : int, R : float, percent : float = 0.05):
	"""Calcul la distance interparticulaire moyenne pour une sphère composé de :NbPart: particules et de rayon :R:, et en retourne une fraction :percent = 0.05:.
	NbPart : Nombre de particules du système.
	R : Rayon de l'objet.
	percent : fraction de la distance inter-particulaire moyenne à retourner.
	"""
	return R / (NbPart)**(1./3.) * percent

#def LoadDBUsingPandas(filename : str, request : str = "SELECT * FROM densite_log WHERE type=5;", idx : str = "id"):
	#"""Load Data from sqlite3 database using request 'request' and return Pandas.DataFrame object.
	#filename                                            : database name,
	#request = "SELECT * FROM densite_log WHERE type=5;" : request to execute,
	#idx     = "id"                                      : column to use as index (None for the default).
	#"""
	#import sqlite3

	#if isinstance(filename, str):
		#wib_conn = sqlite3.connect(filename)
	#else:
		#wib_conn = filename

	#if idx is not None:
		#return psql.read_frame(request, wib_conn).set_index(idx)
	#return psql.read_frame(request, wib_conn)

def OldLoadGadget(filename : str, dtype : int = None):
	from ..dir.rw		  import File
	from ..Gadget.load_gadget import ReadGadget

	tmp = ReadGadget(filename)
	if tmp.border_block() == 256:
		print("Lecture d'un fichier gadget")
		#tmp.get_positions()
		don = tmp.get_velocities()
		#np  = np.sum(tmp.read_header()["Nall"])
		don.shape = (len(don)/3, 3)
		if dtype is not None:
			tmp.read_header()
			wanted = tmp.header["Npart"][dtype]
			print("type is : ", dtype, " for : ", wanted, " Particules.")
			before = sum(tmp.header["Npart"][0:dtype])
			don    = don[before:(before+wanted)]
	else:
		print("Lecture d'un fichier texte")
		don = np.array(File.Read_File(filename, beval=True))

	return don


