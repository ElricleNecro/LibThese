#! /usr/bin/env python
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

packages = st.find_packages()

#--------------------------------------------------------------------------------------------------------------
# Call the setup function:
#--------------------------------------------------------------------------------------------------------------
setup(
	name        = 'LibThese',
	version     = '2.0a',
	description = 'Python Module for analysis gadget simulation.',
	author      = 'Guillaume Plum',
	packages    = packages,
	data_files  = [
		('bin', ['scripts/animationv2.py']),
		('share/LibThese/animation-plugins', glob.glob("share/LibThese/animation-plugins/*.py")),
	],
)

#vim:spelllang=
