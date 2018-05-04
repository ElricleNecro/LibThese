#! /usr/bin/env python3
# -*- coding:Utf8 -*-

#--------------------------------------------------------------------------------------------------------------
# All necessary import:
#--------------------------------------------------------------------------------------------------------------
import os, sys, glob

try:
	import InitialCond
except ImportError:
	print("You need the InitialCond package for some import part of the module.")
	sys.exit(-1)

try:
	import numpy
except ImportError:
	print("Numpy is a needed dependancy.")
	sys.exit(-1)

try:
	import matplotlib
except ImportError:
	print("You really need matplotlib")
	sys.exit(-1)

#from setuptools import find_packages
import setuptools as st
from distutils.core import setup
from distutils.command.install_data import install_data

packages = st.find_packages()

#--------------------------------------------------------------------------------------------------------------
# Call the setup function:
#--------------------------------------------------------------------------------------------------------------
setup(
	name        = 'LibThese',
	version     = '2.0',
	description = 'Python Module for analysis gadget simulation.',
	author      = 'Guillaume Plum',
	packages    = packages,
	cmdclass    = {'install_data': install_data},
	data_files  = [
		('share/LibThese/animation-plugins', ["share/LibThese/animation-plugins/__init__.py"]), #glob.glob("share/LibThese/animation-plugins/*.py")),
		('share/LibThese/', ["share/LibThese/config.yml", "share/LibThese/filter.yml"]), #glob.glob("share/LibThese/animation-plugins/*.py")),
	],
	scripts = [
		'scripts/animationv2.py',
		'scripts/models_plot.py',
		'scripts/roi.py',
		'scripts/verif_python.py',
	],
)

#vim:spelllang=
