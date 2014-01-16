#! /usr/bin/env python
# -*- coding:Utf8 -*-

import abc
import LibPerso.typecheck as tc
from matplotlib import pyplot as plt

class Plot(object,metaclass=abc.ABCMeta):
	"""Classe de gestion d'un graphique.
	"""
	_nb_instance = 0
	def __init__(self, ax=None, **kwargs):
		"""ax : mpl.Axes.axes class for plotting,
		*kwargs* : options pour la fonction de plot.
		"""
		self.ax                      = ax
		self.DictPlot                = kwargs
		self.__class__._nb_instance += 1

#	def __init__(fig=None, color=None, marker=None, ls=None, ms=None):
#		self._color  = color
#		self._marker = marker
#		self._ls     = ls
#		self._ms     = ms
#		self.__class__._nb_instance += 1

	@property
	@tc.typecheck
	def ms(self) -> int:
		return self._ms
	@ms.setter
	@tc.typecheck
	def ms(self, val: int):
		self._ms = val

	@abc.abstractproperty
	def x(self):
		raise NotImplementedError("You MUST implement setter AND getter for x!")
	@x.setter
	def x(self, val):
		raise NotImplementedError("You MUST implement setter AND getter for x!")

	@abc.abstractproperty
	def y(self):
		raise NotImplementedError("You MUST implement setter AND getter for y!")
	@y.setter
	def y(self, val):
		raise NotImplementedError("You MUST implement setter AND getter for y!")

	def Plot(self, ax=None, **kwargs):
		tmp = None
		if ax is None or self.ax is None:
			tmp = plt.figure(self.__class__._nb_instance)
			ax  = tmp.add_subplot(111)
		else:
			ax = self.ax

		odict = self.DictPlot
		odict.update(kwargs)

#		if self._color is not None and "color" not in kwargs:
#			kwargs["color"] = self._color
#
#		if self._marker is not None and "marker" not in kwargs:
#			kwargs["marker"] = self._marker
#
#		if self._ls is not None and "linestyle" not in kwargs:
#			kwargs["linestyle"] = self._ls
#
#		if self._ms is not None and "markersize" not in kwargs:
#			kwargs["markersize"] = self._ms

		ax.plot(self._x, self._y, **odict)
		#color=self._color, marker=self._marker, linestyle=self._ls, markersize=self._ms)
		return tmp, ax

	def __del__(self):
		self.__class__._nb_instance -= 1
		#super(object, self).__del__()

