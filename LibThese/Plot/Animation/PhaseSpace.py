# -*- coding:Utf8 -*-
import os

from LibThese      import Carte   as c
from .Base import FromHDF5, register_module

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
		if self.File is not None:
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

		if self.J is None:
			ax.text(
				0.8,
				0.95,
				"Time: %g\nAll J"%(
					self._file.get_time(os.path.basename(frame), "time") if self.File is not None else map.time,
				),
				transform=ax.transAxes,
				verticalalignment='center',
				horizontalalignment='left',
			)
		else:
			ax.text(
				0.8,
				0.95,
				"Time: %g\nJ = %g"%(
					self._file.get_time(os.path.basename(frame), "time") if self.File is not None else map.time,
					self.J,
				),
				transform=ax.transAxes,
				verticalalignment='center',
				horizontalalignment='left',
			)

		return frame

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
	parser.add_argument(
		"-j",
		"--angular-momentum",
		dest="J",
		type=float,
		help="Angular Momentum to use.",
	)
	parser.add_argument(
		"--j-bin",
		type=int,
		help="Number of bins of angular momentum.",
	)
	return parser

register_module(create_sub_PSMap)
