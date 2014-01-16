#! /usr/bin/env python
# -*- coding:Utf8 -*-

class Plot:
	def __init__(self, don, axes):
		"""Constructeur :
		don  : donnée à tracer.
		axes : classe matplotlib.axes.AxesSubplot pour tracer.
		"""
		self.data   = don
		self.ax     = axes

		self.loglog = False

	def LogLogSwitch(self):
		"""Switch le graphique en LogLog ou Normal.
		"""
		self.loglog = not self.loglog

	def Plot(self, col=None, lab=None):
		"""Trace les données.
		"""
		if self.loglog:
			plot = self.loglog
		else:
			plot = self.plot

		if col is None:
			if lab is None:
				plot(self.don[:,0], self.don[:,1])
			else:
				plot(self.don[:,0], self.don[:,1], lab)
		else:
			for i, tup in enumerate(col):
				if lab is None:
					plot(self.don[tup[0], tup[1]])
				else:
					plot(self.don[tup[0], tup[1]], lab[i])

		self.ax.legend(self.leg, 'lower left', shadow=True)

	def Title(self, title):
		"""Ajuste le titre du graphique.
		"""
		self.ax.set_title(title)
		#self.title = title

	def Label(self, x="", y=""):
		"""Ajuste les labels des axes :
		x = "" : label de l'axe x.
		y = "" : label de l'axe y.
		"""
		self.x = x
		self.y = y
		self.ax.set_xlabel(x)
		self.ax.set_ylabel(y)

	def Legende(self, leg):
		"""Ajuste la légende du graphe.
		"""
		if type(leg) == type(tuple()):
			raise TypeError("Vous devez donner un tuple !!!")
		self.leg = leg
