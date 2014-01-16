#! /usr/bin/env python
# -*- coding:Utf8 -*-

import h5py
import numpy as np

class DensiteTable(dict):
	def __init__(self):
		self["r"]           = 0
		self["densite"]     = 1
		self["temperature"] = 2
		self["aisotropy"]   = 3

	def __call__(self, name):
		return self[name]

class TimeTable(object):
	def __init__(self):
		tmp = [
			"time",
			"s_ratio",
			"g_ratio",
			"Viriel",
			"Kinetic",
			"Potential",
			"Temperature",
			"Anisotropy",
			"r10",
			"r50",
			"r90",
			"x", "y", "z",
			"vx", "vy", "vz",
		]
		self._corres = {
			key: val for val, key in enumerate(tmp)
		}

	def __call__(self, name):
		return self._corres[name]

class Data(object):
	def __init__(self, file, status="r", param_table=TimeTable(), densite=DensiteTable()):
		self._file = h5py.File(file, status)
		self._correspondance = dict(
				timeparam=param_table,
				densite=densite,
		)

	def get_time(self, node, *parameter):
		return self._file[a]["timeparam"][0,:]

	def get_all_time(self, *parameter):
		res = np.array( [[]] )
		for a in self._file:
			tmp = self.get_time(a, *parameter)
			tmp = tmp[ [self._correspondance["timeparam"](i) for i in parameter] ]
			res = np.resize(res, (res.shape[0] + 1, tmp.shape[0]))
			res[ res.shape[0]-1, : ] = tmp[:]

		return res

	def get_fof(self, node):
		return self._file[node]["ids"][:]
