# -*- coding:Utf8 -*-

import matplotlib.colorbar as cb
import matplotlib.pyplot   as plt
import matplotlib.cm	   as cm
import itertools	   as it
import numpy		   as np

from mpl_toolkits.axes_grid1 import make_axes_locatable
from InitialCond.Gadget      import Gadget
from ..Utils.Histo	     import Histogram

__all__ = [
	"Map",
	"DensityCarte",
]

class Map(Gadget):
	def __init__(self, *args, **kwargs):
		"""
		"""
		if "nbbin" in kwargs:
			self.nbbin = kwargs["nbbin"]
			del kwargs["nbbin"]
		else:
			self.nbbin = 100

		if "use_vit" in kwargs:
			self.use_vit = kwargs["use_vit"]
			del kwargs["use_vit"]
		else:
			self.use_vit = False

		if "format" in kwargs:
			format = kwargs["format"]
			del kwargs["format"]
		else:
			format = 1

		if "nbfile" in kwargs:
			nbfile = kwargs["nbfile"]
			del kwargs["nbfile"]
		else:
			nbfile = 1

		letter      = [ "x", "y", "z" ]
		self._tlist = dict()
		self._data  = dict()
		for a in it.combinations(range(3), 2):
			self._tlist[letter[a[0]] + letter[a[1]]] = a

		super(Map, self).__init__(*args, **kwargs)
		if format == 1:
			self._read_format1(nbfile)
		elif format == 2:
			self._read_format2(nbfile)
		elif format == 3:
			self._read_format3(nbfile)
		else:
			raise ValueError("File format not recognized!")

		self.CreateMap()

	def CreateMap(self):
		if self.use_vit:
			tmp = self.Part.NumpyVelocities
		else:
			tmp = self.Part.NumpyPositions
		for k, t in self._tlist.items():
			h, x, y = np.histogram2d(
						tmp[:,t[0]],
						tmp[:,t[1]],
						bins=self.nbbin
			)

			self._data[k] = (h.T, x, y)

	def Get(self, name):
		if not name in self._tlist.keys():
			raise ValueError(name + "not in allowed value: " + [i for i in self._tlist.keys()])
		return self._data[name]

	@staticmethod
	def Plot(cls, name, fig=None, ax=None):
		h, x, y = cls.Get(name)
		h, x, y = h.copy(), x.copy(), y.copy()
		tmp = np.ma.log10(np.ma.masked_where( h <= 0., h))
		h[ tmp.nonzero() ] = tmp[ tmp.nonzero() ]

		if fig is None and ax is None:
			fig = plt.figure()
			ax  = fig.add_subplot(111)
		elif fig is None and ax is not None:
			fig = ax.figure
		elif ax is None:
			ax = fig.add_subplot(111)

		ax.set_xlabel("$" + name[0] + "$")
		ax.set_ylabel("$" + name[1] + "$")
		ax.set_xlim(x.min(), x.max())
		ax.set_ylim(y.min(), y.max())

		cb = ax.pcolormesh(x, y, h, cmap=cm.gray)

		return fig, ax, cb

class DensityCarte(Histogram):
	"""Classe s'occupant de gérer les histogrammes pour tracer les cartes de densité du systèmes.
	"""
#	def __init__(self, num=None):
#		if num is None:
#			self.fig, self.axs = plt.subplots(1, len(tlist), squeeze=True)
#		else:
#			self.fig, self.axs = plt.subplots(1, len(tlist), num=num, squeeze=True)

	def Set_AllDim(self, fact):
		"""Multiplie chaque dimension par fact.
		"""
		for i in range(0, 3):
			super().Set_dim(i, fact)

	def Plot(self, num=None, cmap=cm.jet, verbose=0, log=False):
		"""Trace les histogrammes.
		"""
		self.tlist = []
		for a in it.combinations(range(3), 2):
			self.tlist += [a]
		if verbose >= 1: print(self.tlist)

		if num is None:
			self.fig, self.axs = plt.subplots(1, len(self.tlist), squeeze=True)
		else:
			self.fig, self.axs = plt.subplots(1, len(self.tlist), num=num, squeeze=True)

		for i, v in enumerate(self.tlist):
			X, Y, Z = super().Create_Histo(ind=v)
			#X, Y, Z = super().Create_FuncHisto(lambda f: f[-1], ind=v)
			Z = np.ma.array(Z)
			Z = np.ma.masked_where(Z <= 0, Z)
			if log:
				Z = np.log10(Z)
			Axis = np.array( [np.min(X), np.max(X), np.min(Y), np.max(Y)] )
			self.axs[i].axis(Axis)

			cbf = self.axs[i].pcolor(X, Y, Z, cmap=cmap)
			divider = make_axes_locatable(self.axs[i])
			cax = divider.append_axes("right", size="5%", pad=0.05)

#			cax, key = cb.make_axes(self.axs[i])
			self.fig.colorbar(cbf, cax=cax)

			ratio = (Axis[1] - Axis[0]) / (Axis[3] - Axis[2])
			self.axs[i].set_aspect(ratio, adjustable='box')

	def Get_Plot(self):
		return self.fig

	def Get_Axes(self):
		return self.axs

