#! /usr/bin/env python
# -*- coding:Utf8 -*-

import h5py

class H5Reader(object):
	def __init__(self, file, status="r"):
		self.___file = h5py.File(file, status)
