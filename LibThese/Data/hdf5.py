# -*- coding:Utf8 -*-

import h5py
import numpy as np


class DensiteTable(dict):

    def __init__(self):
        self["r"] = 0
        self["densite"] = 1
        self["temperature3"] = 2
        self["anisotropy"] = 3
        self["temperature2"] = 4
        self["temperature"] = 5

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
            "Temperature_3",
            "Anisotropy",
            "r10",
            "r50",
            "r90",
            "x", "y", "z",
            "vx", "vy", "vz",
            "Temperature_2",
            "Temperature"
        ]
        self._corres = {
            key: val for val, key in enumerate(tmp)
        }

    def __call__(self, name):
        return self._corres[name]


class Data(object):

    def __init__(
        self,
        file,
        status="r",
        corres=dict(
            timeparam=TimeTable(),
            densite=DensiteTable())
    ):
        self._file = h5py.File(file, status)
        self._correspondance = corres

    def get(self, node, sub, *parameter):
        if len(parameter) == 0:
            return self._file[node][sub][:]
        return self._file[node][sub].value[
            :, [self._correspondance[sub](i) for i in parameter]]

    def get_densite(self, node, *parameter):
        return self.get(node, "densite", *parameter)

    def get_time(self, node, *parameter):
        return self.get(node, "timeparam", *parameter)[0, :]

    def get_all_time(self, *parameter):
        res = np.zeros(shape=(len(self._file), len(parameter)))
        for i, a in enumerate(self._file):
            res[i, :] = self.get_time(a, *parameter)

        return res

    def get_fof(self, node):
        return self._file[node]["ids"][:]

    def __del__(self):
        self._file.close()
