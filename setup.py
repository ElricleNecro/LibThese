#! /usr/bin/env python
# -*- coding:Utf8 -*-

#--------------------------------------------------------------------------------------------------------------
# All necessary import:
#--------------------------------------------------------------------------------------------------------------
import os, sys, stat

try:
	import King
except ImportError:
	print("It seems that the python Binding for the king librairies is not installed on your system.\nYou should install it as it is a necessary dependancy!")
	sys.exit(-1)

try:
	import commands
except:
	import subprocess as commands

from distutils.core import setup

#--------------------------------------------------------------------------------------------------------------
# For adding support of pkg-config:
#--------------------------------------------------------------------------------------------------------------
def scandir(dir, files=[]):
	for file in os.listdir(dir):
		path = os.path.join(dir, file)
		if os.path.isfile(path) and path.endswith(".pyx"):
			files.append(path.replace(os.path.sep, ".")[:-4])
		elif os.path.isdir(path):
			scandir(path, files)
	return files

#--------------------------------------------------------------------------------------------------------------
# Packages names:
#--------------------------------------------------------------------------------------------------------------
from setuptools import find_packages
packages = find_packages() # [ 'LibThese' ]

#--------------------------------------------------------------------------------------------------------------
# Call the setup function:
#--------------------------------------------------------------------------------------------------------------
setup(
	name        = 'LibThese',
	version     = '2.0a',
	description = 'Python Module for analysis gadget simulation.',
	author      = 'Guillaume Plum',
	packages    = packages,
)

#vim:spelllang=
