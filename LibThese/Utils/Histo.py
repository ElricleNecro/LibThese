import numpy		   as np
import logging		   as log

from   ..dir.rw		  import File
from   ..Gadget.load_gadget import ReadGadget

class Histogram:
	"""Classe créant et gérant une carte de densité de point, crée à partir d'un numpy.array.

	Les paramètres utiles à modifier sont :
		Carte.colorbar :: fonction correspondant à plt.figure().colorbar() qui permet de placer un axe de couleur.
	"""
	def __init__(self, filename, nbbin=300, ind=(0, 1), FieldRange=None, dtype=None, logger=None, log_level=None):
		"""Quelques paramètres utiles à la création de la classe :
			filename		:: Nom du fichier à lire, ou tableau à lire.
			nbbin			:: 300
			ind = (0, 1)		:: Indices à utiliser pour créer les axes de l'histogramme.
			FieldRange = None	:: Inutile actuellement.
		"""
		# Lecture du fichier :
		#super().__init__(filename, beval=True)

		if isinstance(logger, log.Logger):
			self.log = logger
		elif isinstance(logger, str):
			self.log = log.Logger(logger)
		else:
			self.log = log.Logger("MapLogger")

		if log_level is not None:
			self.log.setLevel(log_level)

		if isinstance(filename, str):
			tmp = ReadGadget(filename)
			if tmp.border_block() == 256:
				self.log.info("Lecture d'un fichier gadget")
				don = tmp.get_positions()
				#np  = np.sum(tmp.read_header()["Nall"])
				don.shape = (len(don)/3, 3)
				if dtype is not None:
					tmp.read_header()
					wanted = tmp.header["Npart"][dtype]
					self.log.info("type is : ", dtype, " for : ", wanted, " Particules.")
					before = sum(tmp.header["Npart"][0:dtype])
					don    = don[before:(before+wanted)]
			else:
				self.log.info("Lecture d'un fichier texte")
				don = np.array(File.Read_File(filename, beval=True))
		elif isinstance(filename, np.ndarray):
			#if filename.shape[1] != 2:
				#raise ValueError(filename.shape[1])
			don = filename
		elif isinstance(filename, list):
			if len(filename) != 2:
				raise ValueError(len(filename))
			don = filename

		self.don   = np.array( don )
		self.nbbin = nbbin
		self.ind   = ind

		self.dx    = None
		self.dy    = None
		self.X     = None
		self.Y     = None
		self.hist  = None

	def Set_dim(self, i, fact):
		"""Ajuste les dimensions de l'axe i en le multipliant par fact :
			don[:,i] *= fact
		"""
		self.don[:,i] *= fact

	def Create_Histo(self, ind=None):
		"""Créé l'histogramme 2D d'un tableau sur toutes les combinaisons possibles d'un tableau.
		"""
		if ind is None: ind = self.ind
		self.hist, self.X, self.Y = np.histogram2d(
						self.don[:,ind[0]],
						self.don[:,ind[1]],
						bins=self.nbbin
					)
		return self.X, self.Y, self.hist.T

	def Create_Axis(self, ind=None):
		"""Créé les axes servant à la fonction Create_FuncHisto.
		Faîtes attentions à ce que les indices donnés en paramètre optionnel soit cohérent avec ceux utilisé par la fonction Create_FuncHisto.
		"""
		pass

	def Create_FuncHisto(self, func, ind=None): #(0, 1)):
		"""Créé l'histogramme des valeurs de la fonction z = f(x, y).
		"""
		if ind is None:
			ind = self.ind

		self.X, self.Y, self.hist, cmpt = np.zeros(self.nbbin, dtype=np.float64), \
							np.zeros(self.nbbin, dtype=np.float64), \
							np.zeros((self.nbbin, self.nbbin), dtype=np.float64), \
							np.zeros((self.nbbin, self.nbbin), dtype=np.float64)
		self.X[0], self.Y[0]            = self.don[:,ind[0]].min(), self.don[:,ind[1]].min()
		dx, dy                          = ( self.don[:,ind[0]].max() - self.don[:,ind[0]].min() ) / self.nbbin, \
							( self.don[:,ind[1]].max() - self.don[:,ind[1]].min() ) / self.nbbin

		print(dx, dy, self.nbbin)

		for i in range(1, len(self.X)):
			self.X[i] = self.X[i-1] + dx
			self.Y[i] = self.Y[i-1] + dy

		for var in self.don:
			i, j             = int((var[ind[0]] - self.X[0])/dx), int((var[ind[1]] - self.Y[0])/dy)
			if i >= self.nbbin:
				i = self.nbbin - 1
			if j >= self.nbbin:
				j = self.nbbin - 1
			self.hist[i, j] += func(var)
			cmpt[i, j]      += 1

		for i in range(self.nbbin):
			for j in range(self.nbbin):
				if cmpt[i,j] != 0:
					self.hist[i, j] /= cmpt[i, j]

#		self.hist = self.hist.T
#		for i, tmp in enumerate(self.hist):
#			for j, tmp2 in enumerate(tmp):
#				if tmp2 <= 0:
#					del self.hist[i,j]
#
		return self.X, self.Y, self.hist.T

class NHisto:
	"""Classe gérant de multiple histogramme.
	"""
	def __init__(self, filename, nbbin=300, ind=None, indmax=None, FieldRange=None):
		self.AllHist = []
		self.nbbin   = nbbin
		if indmax is None:
			self.indmax = self.don.shape[1]
		else:
			self.indmax = indmax

		if ind is None:
			self.allind = []
			for i in it.combinations(range(self.indmax), 2):
				self.allind.append( i )
		else:
			self.allind = ind

	def Create_MFuncHisto(self, func):
		"""Créé un histogramme pour toutes les combinaisons possible.
		"""
		self.AllHist = []
		pass
		for ind in self.allind:
			super().Create_FuncHisto(func, ind=ind)

#class Carte2:
#	"""Classe créant et gérant une carte de densité de point, crée à partir d'un numpy.array.
#
#	Les paramètres utiles à modifier sont :
#		Carte.colorbar :: fonction correspondant à plt.figure().colorbar() qui permet de placer un axe de couleur.
#	"""
#	def __init__(self, data, colorbar=None, ax=None, tlist=[(0, 1), ], clm=cm.jet, nbbin=300, post=lambda x: x):
#		self.colorbar = colorbar
#		self.ax       = ax
#		self.tlist    = tlist
#		self.cmap     = clm
#		self.nbbin    = nbbin
#		if data is None:
#			self.data = None
#		elif type(data) == type(str):
#			from .dir.rw import Read_File
#			self.data = np.array(Read_File(data))
#		elif type(data) == type(list):
#			self.data = np.array(data)
#		elif type(data) == type(np.array):
#			self.data = data
#		else:
#			raise TypeError("les données n'ont pas le bon type.")
#
#		self.data = post(self.data)
#
#		lenx, leny = self.data.shape
#
#
#	def PlotCarte(self, tlist=[(0, 1), (0, 2), (1, 2)], num="Carte de l'objet", clm=cm.jet, nbbin=300, Axis=None, contrast=-20):
#		fig, axs = plt.subplots(1, len(tlist), num=num, squeeze=True)
#
#		for i, tup in enumerate(tlist):
#			axs[i].cla()
#			tmp = PlotHisto(pos, axCar1=axs[i], indice=i, ind=tup, clm=clm, nbbin=nbbin, Axis=Axis, contrast=contrast)
#			color = fig.colorbar(tmp, ax=axs[i])
#
#		return fig, axs, color
#
#	def _create_histo(self):
#		pass
#		self.hist = []
#		for i, tup in enumerate(self.tlist):
#			FieldRange = [ [Axis[i][0], Axis[i][1]], [Axis[i][2], Axis[i][3]] ]
#			self.hist.append( np.histogram2d(self.data[:,ind[0]], self.data[:,ind[1]], bins=nbbin, range=FieldRange) )
#
#	def PlotHisto(axCar1=None, indice=0, ind=(0, 1), clm=cm.jet, nbbin=300, Axis=None, contrast=-20):
#		"""Trace un histogramme des données suivant les indices données, en utilisant la figure et l'axe donnée (ax = plt.figure().add_subplot(111)) lors de la création de la classe.
#
#		Si aucune figure ou aucun axe n'a été donné, il est possible de les donner en utilisant le paramètre axCar1 pour indiquer à la routine où elle doit tracer
#		"""
#		if self.data   is None:
#			raise ValueError("Les données n'ont pas été initialisées.")
#		if axCar1 is None:
#			axCar1 = self.ax
#
#		if Axis is None:
#			Axis = np.array( [np.min(self.data[:,ind[0]]), np.max(self.data[:,ind[0]]), np.min(self.data[:,ind[1]]), np.max(self.data[:,ind[1]]) ] )
#
#		FieldRange = [ [Axis[0], Axis[1]], [Axis[2], Axis[3]] ]
#
#		if axCar1 is None:
#			Carte1 = plt.figure("Carte " + str(ind))
#			axCar1 = Carte1.add_subplot(111)
#
#		hist, X, Y = np.histogram2d(self.data[:,ind[0]], self.data[:,ind[1]], bins=nbbin, range=FieldRange)
#
#		axCar1.axis(Axis)
#
#		Tr = hist.T
#		Tr[ Tr == 0 ] = contrast
#		#Tr = np.log10(np.where(hist.T <= 0, 10**(-0.01), hist.T))
#		tmp = axCar1.pcolor(X, Y, Tr, cmap=clm)
#		ratio = (Axis[1] - Axis[0]) / (Axis[3] - Axis[2]) #(  np.max(data[:,ind[0]]) - np.min(data[:,ind[0]]) ) / (np.max(data[:,ind[1]]) - np.min(data[:,ind[1]]) )
#		axCar1.set_aspect(ratio, adjustable='box') #'equal')
#
#		return tmp



#class Carte(rw.File)
#	def __init__(self):
#	def box(self, ...):
#	def plot(self,tup):
#	def all_plot(self, ...):
#	def add_pts(self, ...):
#
#def Create_box_axis(taille, cen):
#	return np.array(
#		-taille/2 + cen[0],
#		 taille/2 + cen[0],
#		-taille/2 + cen[1],
#		 taille/2 + cen[1],
#		-taille/2 + cen[2],
#		 taille/2 + cen[2]
#		)

