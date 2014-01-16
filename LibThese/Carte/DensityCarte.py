#! /usr/bin/env python
# -*- coding:Utf8 -*-

import matplotlib.colorbar as cb
import matplotlib.pyplot   as plt
import matplotlib.cm	   as cm
import itertools	   as it
import numpy		   as np

from mpl_toolkits.axes_grid1 import make_axes_locatable
from InitialCond.Gadget      import Gadget
from ..Utils.Histo	     import Histogram

class Map(Gadget):
	def __init__(self, *args, **kwargs):
		"""
		"""
		if "nbbin" in kwargs:
			self.nbbin = kwargs["nbbin"]
			del kwargs["nbbin"]
		else:
			self.nbbin = 100

		if "use_vit" in kwargs["use_vit"]:
			self.use_vit = kwargs["use_vit"]
			del kwargs["use_vit"]
		else:
			self.use_vit = False

		self._tlist = []
		for a in it.combinations(range(3), 2):
			self._tlist += [a]

		super(Map, self).__init__(*args, **kwargs)

		self.CreateMap()

	def CreateMap(self):
		if self.use_vit:
			tmp = self.Part.NumpyVelocities
		for t in self._tlist:
			self._data[t] = np.histogram2d(
						tmp[:,t[0]],
						tmp[:,t[1]],
						bins=self.nbbin
			)


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

