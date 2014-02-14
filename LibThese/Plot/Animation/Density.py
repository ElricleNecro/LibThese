# -*- coding:Utf8 -*-
import os
import numpoy as np
import logging as log

from .Base import FromHDF5, register_module

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
	return parser

register_module(create_sub_LogDensity)
