# -*- coding:Utf8 -*-
import os
import numpy as np
import logging as log

from LibThese      import Carte   as c
from .Base import FromHDF5, register_module

class MapPlot(FromHDF5):
	def __init__(self, args):
		self._cb = None
		self._Plan = args.Plan
		self._select = args.RSelect
		self._nb_bin = args.nb_bin
		self._spherical_selection = args.spherical_selection
		self._resize_not_done = True
		self._plot_dc = args.plot_dc
		self._xlim = args.xlim
		self._ylim = args.ylim
		super(MapPlot, self).__init__(args)

	@property
	def Plan(self):
		return self._Plan
	@Plan.setter
	def Plan(self, val):
		self._Plan = val

	@property
	def Radius(self):
		return self._select
	@Radius.setter
	def Radius(self, val):
		self._select = val

	def __call__(self, frame, ax, *o, **kwo):
		if self._resize_not_done:
			ax.figure.set_size_inches( np.array([1920, 1080]) / ax.figure.get_dpi() )
			self._resize_not_done = False

		p = None
		if self.File is not None:
			try:
				p = self.File.get_time(os.path.basename(frame), "x", "y", "z")
			except KeyError as e:
				log.fatal("Unable to find Key: '" + frame + "'")
				self.File.close()
				raise e

		map = c.Map(
				frame,
				nbbin=(
					np.linspace(self._xlim[0], self._xlim[1], self._nb_bin),
					np.linspace(self._ylim[0], self._ylim[1], self._nb_bin),
				),
				#nbbin=self._nb_bin,
				RSelect=self._select,
				#move_pos=-p,
				to_center=self._spherical_selection,
		)

		ind = map._tlist[self.Plan]
		_, _, cb = map.Plot(
				map,
				self.Plan,
				fig=ax.figure,
				ax=ax,
		)
		if p is not None and self._plot_dc:
			ax.plot(p[ ind[0] ], p[ ind[1] ], "r+", linewidth=10, markersize=12, markeredgewidth=13)

		if self._cb is not None:
			self._cb.update_normal(cb)
		else:
			self._cb = ax.figure.colorbar(cb)

		ax.text(
			0.8,
			0.95,
			"Time: %g"%(
				self._file.get_time(os.path.basename(frame), "time") if self.File is not None else map.time,
			),
			transform=ax.transAxes,
			verticalalignment='center',
			horizontalalignment='left',
			color="white",
		)

		return frame

def create_sub_Map(sub):
	parser = sub.add_parser('projection', help="Plot a gadget file on a plan.")
	parser.set_defaults(
		func=MapPlot,
		xscale="linear",
		yscale="linear",
		xlim=(-20., 20.),
		ylim=(-20, 20),
		xlabel=r"$r$",
		ylabel=r"$\vec{r}.\vec{v}/r$",
		title="Projection",
	)

	parser.add_argument(
		"--plan",
		dest="Plan",
		type=str,
		help="Plan to use.",
		choices=[ a for a in c.Map.GetPermutation(["x", "y", "z"]).keys() ],
		default="xy",
	)
	parser.add_argument(
		"--nb-bin",
		type=int,
		help="Number of bins of angular momentum.",
		default=300,
	)
	parser.add_argument(
		"--selection-radius",
		type=float,
		help="Radius into which it will select particles. All particles outside this radius will not be considered.",
		default=None,
		dest="RSelect",
	)
	parser.add_argument(
		"--spherical-selection",
		action='store_true',
		help="Are we using the 'Spherical selection' version of the verification code?",
	)
	parser.add_argument(
		"--plot-density-center",
		help="Plot Density center on top of the map.",
		dest="plot_dc",
		action='store_true',
	)

	return parser

register_module(create_sub_Map)
