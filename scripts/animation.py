#! /usr/bin/env python3
# -*- coding:Utf8 -*-

import os
import h5py
import argparse                   as ap
import logging			  as log

from LibThese      import Carte   as c
from LibThese.Plot import Animate as an

class MapPlot(object):
	def __init__(self, filename, J):
		self._J = J
		try:
			self._file = h5py.File(filename, "r")
		except OSError as e:
			log.fatal("Unable to open file '" + filename + "'")
			raise e

	@property
	def J(self):
		return self._J
	@J.setter
	def J(self, val):
		self._J = val

	@property
	def File(self):
		return self._file
	@File.setter
	def File(self, val):
		if isinstance(val, str):
			self._file = h5py.File(val, "r")
		else:
			self._file = val
	@File.deleter
	def File(self):
		self._file.close()
		del self._file

	def __call__(self, frame, ax, *o, **kwo):
		p, v = None, None
		try:
			p   = self.File[ os.path.basename(frame) ]["timeparam"][0, 11:14]
			v   = self.File[ os.path.basename(frame) ]["timeparam"][0, 14:17]
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

		map.Plot(
			fig=ax.figure,
			ax=ax,
			log=True,
		)

	def __del__(self):
		self._file.close()

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
		help="File in which we get all needed information."
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
			save=True,
			frame=args.Files,
			xlabel=r"$r$",
			ylabel=r"$\vec{r}.\vec{v}/r$",
			title=r"Movie Theater!",
			xlim=(1e-2, 20.),
			ylim=(-2, 2),
			xscale="log"
	)
	anim.update = func
	anim.Plot(
		progressbar=True,
	)

