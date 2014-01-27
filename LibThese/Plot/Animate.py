#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
"""

import numpy    as np
import tempfile as tmp

from matplotlib import pyplot as plt

class WeirdosError(Exception):
	def __init__(self, error="?"):
		self._error = error
	def __str__(self):
		return repr("Weirdos error " + str(error))

class Animate(object):
	"""Cette classe sert de template pour créer des animations. Elles s'occupe
	de créer la figure et les axes comme demandé lors de la construction de la
	figure.
	"""
	def __init__(self, fig=None, ax=None, frame=None, tmp_directory=None, builder=None, figkwargs=None, save=True, **kwargs):
		"""Constructeur :
		fig = None :: Figure à utiliser pour les graphiques.
		ax = None :: Axes liées à la figure sur lesquels tracer.
		builder = None :: Fonction charger de construire les axes pour la classe.
		"""
		if fig is None and ax is None and builder is not None:
			fig, ax = builder()
		elif fig is None and ax is None:
			if figkwargs is not None:
				fig = plt.figure(**figkwargs)
			else:
				fig = plt.figure()
			ax  = fig.add_subplot(111, **kwargs)
		elif fig is None and ax is not None:
			fig = ax.figure
		elif ax is None:
			ax = fig.add_subplot(111, **kwargs)
		else:
			raise WeirdosError

		if frame is not None: # and isinstance(frame, (tuple, list, np.array)):
			self._frame = frame
		elif frame is not None:
			self._frame = range(frame)
		else:
			self._frame = None

		self._fig = fig
		self._ax  = ax
		self._ax_opt = kwargs

		self._save = save

		if self._save and tmp_directory is not None:
			self._tmp = tmp_directory
		elif self._save:
			self._tmp = tmp.TemporaryDirectory()
		else:
			self._tmp = None

	def __del__(self):
		if self._tmp is not None:
			self._tmp.cleanup()
		#super(Animate, self).__del__()

	@property
	def Save(self):
		return self._save
	@Save.setter
	def Save(self, val):
		self._save = val
		if self._save:
			self._tmp = tmp.TemporaryDirectory()
		elif self._tmp is not None:
			self._tmp.cleanup()
	@Save.deleter
	def Save(self):
		self._save = False
		if self._tmp is not None:
			self._tmp.cleanup()
			del self._tmp
			self._tmp = None

	@property
	def Fig(self):
		return self._fig
	@Fig.setter
	def Fig(self, val):
		self._fig = val
	@Fig.deleter
	def Fig(self):
		self._fig.clf()

	@property
	def Axes(self):
		return self._ax
	@Axes.setter
	def Axes(self, val):
		self._ax = val
	@Axes.deleter
	def Axes(self):
		self._ax.cla()

	def Set_AxesProperty(self, **kwargs):
		self._ax_opt = kwargs
		self._ax.update(**kwargs)
	def Get_AxesProperty(self):
		return self._ax_opt
	AxesProperty = property(fget=Get_AxesProperty, doc="Dictionnaire des propriétés de l'axe.")

	@staticmethod
	def _save_fig(fig, name, outdir, format):
		"""Enregistre une figure au format indiqué dans le repertoire outdir.
		fig :: figure à enregistrer.
		name :: nom à utiliser.
		outdir :: répertoire où enregistrer les images.
		format :: format de l'image (doit-être supporté par matplotlib).
		"""
		from os.path import basename, join
		fig.savefig(join(outdir, basename(name) + "." + format), format=format, transparent=False)

	@staticmethod
	def update(frame, ax, *opt, **kwopt):
		"""Fonction s'occupant de mettre à jour la figure.
		frame :: élément de l'itérateur frame= du constructeur.
		ax :: Axe sur lequel tracer.
		*opt, **opt :: options supplémentaire passé à Plot.
		"""
		raise NotImplementedError

	def Plot(self, *args, print=False, progressbar=True, **kwargs):
		if progressbar:
			from pacmanprogressbar import Pacman
			# On prépare la barre de progression :
			p = Pacman(start=0, end=len(self._frame)+1)

		for i, a in enumerate(self._frame):
			# On efface le graphique précédent :
			self._ax.cla()
			self._ax.set(**self._ax_opt)

			self.update(a, self._ax, *args, **kwargs)

			if print:
				self._ax.figure.canvas.draw()

			if self._save:
				self._save_fig(self.Fig, "%03d"%i, self._tmp.name, "png")

			if progressbar:
				# Mise à jour de la barre de progression :
				p.progress(i)
