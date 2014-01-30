#! /usr/bin/env python3
# -*- coding:Utf8 -*-

import os
import argparse                   as ap
import logging			  as log

from LibThese      import Carte   as c
from LibThese.Plot import Animate as an
from LibThese.Plot import hdf5    as h

class FromHDF5(object):
	def __init__(self, filename):
		try:
			self.File = filename
		except OSError as e:
			log.fatal("Unable to open file '" + filename + "'")
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

class MapPlot(FromHDF5):
	def __init__(self, filename, J):
		self._cb = None
		self._J = J
		super(self, MapPlot).__init__(filename)

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

def get_args():
	parser = ap.ArgumentParser()
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
		"-j",
		"--angular-momentum",
		dest="J",
		type=float,
		help="Angular Momentum to use.",
		default=None,
	)

	return parser.parse_args()

if __name__ == '__main__':
	args = get_args()

	args.Files.sort()

	func = MapPlot(args.ref, args.J)
	anim = an.Animate(
			save          = True,
			frame         = args.Files,
			xlabel        = r"$r$",
			ylabel        = r"$\vec{r}.\vec{v}/r$",
			title         = r"Movie Theater!",
			xlim          = (1e-2, 20.),
			ylim          = (-2, 2),
			xscale        = "log",
			tmp_directory = args.tmp_dir,
	)
	anim.update = func
	anim.Plot(
		progressbar=True,
	)

