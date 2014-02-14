#! /usr/bin/env python3
# -*- coding:Utf8 -*-

import os
import sys
import logging as log
import importlib

import matplotlib as ml
ml.use('agg')

import LibThese.Plot.Animation as lpa
from LibThese.Plot import Animate as an

PREFIX      = os.path.dirname(__file__)
PLUGINS_DIR = os.path.abspath(
			os.path.join(
				PREFIX,
				"../share/LibThese"
			)
		)

sys.path.insert(0, PLUGINS_DIR)

try:
	importlib.import_module("animation-plugins")
except ImportError as e:
	log.fatal("Import failed. sys.path is: {0}".format(sys.path))
	raise e

if __name__ == '__main__':
	args = lpa.get_args()

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

