#! /usr/bin/env python3
# -*- coding:Utf8 -*-

import matplotlib as ml
ml.use('agg')

import os
import argparse                   as ap
import logging			  as log
import numpy			  as np

from LibThese      import Carte   as c
from LibThese.Plot import Animate as an
from LibThese.Plot import hdf5    as h

class FromHDF5(object):
	def __init__(self, args):
		try:
			self.File = args.ref
		except OSError as e:
			log.fatal("Unable to open file '" + args.ref + "'.")
			raise e

	@property
	def File(self):
		return self._file
	@File.setter
	def File(self, val):
		if isinstance(val, str):
			self._file = h.Data(val)
		else:
			self._file = val
	@File.deleter
	def File(self):
		del self._file

	def __call__(self, frame, ax, *o, **kwo):
		data = File.get(frame, *o)
		for i in range(1, data.shape[1]):
			ax.plot(data[:, 0], data[:, i])

		return frame

class PSPlot(FromHDF5):
	def __init__(self, args):
		self._cb = None
		self._J = args.J
		self._j_bin = args.j_bin
		super(PSPlot, self).__init__(args)

	@property
	def J(self):
		return self._J
	@J.setter
	def J(self, val):
		self._J = val

	def __call__(self, frame, ax, *o, **kwo):
		p, v = None, None
		try:
			p = -self.File.get_time(os.path.basename(frame), "x", "y", "z")
			v = -self.File.get_time(os.path.basename(frame), "vx", "vy", "vz")
		except KeyError as e:
			log.fatal("Unable to find Key: '" + frame + "'")
			self.File.close()
			raise e

		map = c.PSPlot(
				frame,
				AxsLog   = True,
				nbbin    = 300,
				Log      = True,
				v_min    = -2,
				v_max    = 2,
				r_min    = 1e-2,
				r_max    = 20,
				move_pos = p,
				move_vel = v,
				j_bin    = self._j_bin,
		)

		map.GetSliceJ(self.J)

		_, _, cb = map.Plot(
				fig=ax.figure,
				ax=ax,
				log=False,
				#log=True,
		)
		if self._cb is not None:
			self._cb.update_normal(cb)
		else:
			self._cb = ax.figure.colorbar(cb)

		ax.text(
			0.8,
			0.95,
			"Time: %g\nJ = %g"%(
				self._file.get_time(os.path.basename(frame), "time"),
				self.J,
			),
			transform=ax.transAxes,
			verticalalignment='center',
			horizontalalignment='left',
		)

		return frame

class LogDensity(FromHDF5):
	def __init__(self, args):
		super(LogDensity, self).__init__(args)
		self._x  = np.linspace(args.xlim[0], args.xlim[1], 20)
		self._y2 = self._x**(-2)
		self._y4 = self._x**(-4)

	def __call__(self, frame, ax, *o, **kwo):
		dlog = None
		try:
			dlog = self.File.get(os.path.basename(frame), "densite_log")
		except KeyError as e:
			log.fatal("Unable to find Key: '" + frame + "'")
			self.File.close()
			raise e

		ax.plot(dlog[:,0], dlog[:,1], "-")
		ax.plot(self._x, self._y2, "-")
		ax.plot(self._x, self._y4, "-")

		ax.text(
			0.8,
			0.95,
			"Time: %g\n"%(
				self.File.get_time(os.path.basename(frame), "time"),
			),
			transform=ax.transAxes,
			verticalalignment='center',
			horizontalalignment='left',
		)

		return frame

class MapPlot(FromHDF5):
	def __init__(self, args):
		self._cb = None
		self._Plan = args.Plan
		self._select = args.RSelect
		self._nb_bin = args.nb_bin
		self._spherical_selection = args.spherical_selection
		self._resize_not_done = True
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
		try:
			p = self.File.get_time(os.path.basename(frame), "x", "y", "z")
		except KeyError as e:
			log.fatal("Unable to find Key: '" + frame + "'")
			self.File.close()
			raise e

		map = c.Map(
				frame,
				nbbin=self._nb_bin,
				RSelect=self._select,
				move_pos=-p,
				to_center=self._spherical_selection,
		)

		ind = map._tlist[self.Plan]
		_, _, cb = map.Plot(
				map,
				self.Plan,
				fig=ax.figure,
				ax=ax,
		)
		ax.plot(p[ ind[0] ], p[ ind[1] ], "r+", linewidth=10, markersize=12, markeredgewidth=13)

		if self._cb is not None:
			self._cb.update_normal(cb)
		else:
			self._cb = ax.figure.colorbar(cb)

		ax.text(
			0.8,
			0.95,
			"Time: %g"%(
				self._file.get_time(os.path.basename(frame), "time"),
			),
			transform=ax.transAxes,
			verticalalignment='center',
			horizontalalignment='left',
			color="white",
		)

		return frame

def set_common_args(parser):
	parser.add_argument(
		"Files",
		nargs='+',
		help="File to plot.",
	)
	parser.add_argument(
		"-r",
		"--ref",
		type=str,
		help="File in which we get all needed information.",
	)
	parser.add_argument(
		"--tmp-dir",
		type=str,
		help="Directory into which the script will create all graphics.",
		default=None,
	)
	parser.add_argument(
		"--xlabel",
		type=str,
		help="Set X axis label.",
	)
	parser.add_argument(
		"--ylabel",
		type=str,
		help="Set Y axis label.",
	)
	parser.add_argument(
		"--xlim",
		type=str,
		help="Set X axis limits.",
		nargs=2,
	)
	parser.add_argument(
		"--ylim",
		type=str,
		help="Set Y axis limits.",
		nargs=2,
	)
	parser.add_argument(
		"--xscale",
		type=str,
		help="Set X axis scale.",
	)
	parser.add_argument(
		"--yscale",
		type=str,
		help="Set Y axis scale.",
	)
	parser.add_argument(
		"--grid",
		action="store_true",
		help="Print a grid on graphics?",
	)

def create_sub_PSMap(sub):
	parser = sub.add_parser('psplot', help="Plot the phase space of multiple files.")
	parser.set_defaults(
		func=PSPlot,
		xscale="log",
		yscale="linear",
		xlim=(1e-2, 20.),
		ylim=(-2, 2),
		xlabel=r"$r$",
		ylabel=r"$\vec{r}.\vec{v}/r$",
		title="Phase Space",
	)
	set_common_args(parser)
	parser.add_argument(
		"-j",
		"--angular-momentum",
		dest="J",
		type=float,
		help="Angular Momentum to use.",
		default=None,
	)
	parser.add_argument(
		"--j-bin",
		type=int,
		help="Number of bins of angular momentum.",
		default=None,
	)

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
	set_common_args(parser)

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

def create_sub_LogDensity(sub):
	parser = sub.add_parser('density-log', help="Plot the density (with bin size constant in log) of multiple files.")
	parser.set_defaults(
		func=LogDensity,
		xscale="log",
		yscale="log",
		xlim=(1e-2, 30.),
		ylim=(1e-5, 30),
		xlabel=r"$r$",
		ylabel=r"$\rho(r)$",
		title="Density",
	)
	set_common_args(parser)

def get_args():
	parser = ap.ArgumentParser()
	sub = parser.add_subparsers(help="What do we want to plot?")
	create_sub_PSMap(sub)
	create_sub_LogDensity(sub)
	create_sub_Map(sub)

	return parser.parse_args()

if __name__ == '__main__':
	args = get_args()

	args.Files.sort()

	func = args.func(args)
	anim = an.Animate(
			save          = True,
			frame         = args.Files,
			xlabel        = args.xlabel,
			ylabel        = args.ylabel,
			title         = args.title,
			xlim          = args.xlim,
			ylim          = args.ylim,
			xscale        = args.xscale,
			yscale        = args.yscale,
			tmp_directory = args.tmp_dir,
			grid          = args.grid,
	)
	anim.update = func
	anim.Plot(
		progressbar=False,
	)

