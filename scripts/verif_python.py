#!/usr/bin/env python
# encoding: utf-8

import sys
import logging
import numpy as np
import argparse as ap

from glob import glob
from os import path as p
from LibThese import Data as d
from InitialCond import Gadget as g


class Analyse(object):
    def __init__(self, hdf, gadget, RSelect=10., substract=True):
        # We are getting the information about the density center:
        hdf5 = d.Data(hdf)

        p_cg = hdf5.get(p.basename(gadget), "timeparam", "x", "y", "z")
        v_cg = hdf5.get(p.basename(gadget), "timeparam", "vx", "vy", "vz")

        self._time = hdf5.get(p.basename(gadget), "timeparam", "time")[0, 0]

        fof = hdf5.get(p.basename(gadget), "ids")[:, 0]

        # We read the Gadget file:
        _name = gadget
        gadget = g.Gadget(gadget)
        gadget._read_format1(1)
        # gadget.Part.SortById()

        logging.debug("Removing %g from %s" % (gadget.BoxSize / 2., _name))

        pos = gadget.Part.NumpyPositions.copy()  - np.array([gadget.BoxSize/2.]*3)
        vel = gadget.Part.NumpyVelocities.copy()
        ide = gadget.Part.NumpyIdentities

        tmp_r = np.sum(pos**2, axis=1)
        id_p_sort1 = np.argsort(tmp_r)
        id_p_sort1 = id_p_sort1[ tmp_r[id_p_sort1] <= RSelect ** 2. ]

        pos = pos[id_p_sort1]
        vel = vel[id_p_sort1]
        ide = ide[id_p_sort1]

        id_p_sort1 = np.argsort(ide)
        id_p_sort1 = id_p_sort1[fof]

        pos = pos[id_p_sort1]
        vel = vel[id_p_sort1]
        ide = ide[id_p_sort1]

        if substract:
            # We are correcting our center of position and velocities:
            self._p = pos - p_cg
            self._v = vel - v_cg
            # self._p = gadget.Part.NumpyPositions.copy()[fof, :]  - np.array([gadget.BoxSize/2.]*3) - p_cg
            # self._v = gadget.Part.NumpyVelocities.copy()[fof, :] - v_cg
        else:
            self._p = pos
            self._v = vel
            # self._p = gadget.Part.NumpyPositions.copy()[fof, :] - np.array([gadget.BoxSize/2.]*3)
            # self._v = gadget.Part.NumpyVelocities.copy()[fof, :]

        gadget.Part.Release()
        del gadget, hdf5

    def get_r2(self):
        return np.sum(self.pos[:]**2, axis=1)

    def get_v2(self):
        return np.sum(self.vel[:]**2, axis=1)

    def get_vr(self):
        return np.sum(self.pos * self.vel, axis=1) / np.sqrt( self.get_r2() )

    @property
    def time(self):
        return self._time

    @property
    def pos(self):
        return self._p
    @pos.setter
    def pos(self, val):
        self._p = val

    @property
    def vel(self):
        return self._v
    @vel.setter
    def vel(self, val):
        self._v = val


class Object(object):
    def __init__(self, file, center, time=None, ids=None, substract=True):
        p_cg = center[:3]
        v_cg = center[3:]

        # We read the Gadget file:
        gadget = g.Gadget(file)
        gadget._read_format1(1)

        if time is not None:
            self._time = time
        else:
            self._time = gadget.time

        if substract:
            # We are correcting our center of position and velocities:
            self._p = gadget.Part.NumpyPositions.copy()[ids, :]  - p_cg
            self._v = gadget.Part.NumpyVelocities.copy()[ids, :] - v_cg
        else:
            self._p = gadget.Part.NumpyPositions.copy()[ids, :]
            self._v = gadget.Part.NumpyVelocities.copy()[ids, :]

        gadget.Part.Release()
        del gadget

    def get_r2(self):
        return np.sum(self.pos[:]**2, axis=1)

    def get_v2(self):
        return np.sum(self.vel[:]**2, axis=1)

    def get_vr(self):
        return np.sum(self.pos * self.vel, axis=1) / np.sqrt( self.get_r2() )

    @property
    def time(self):
        return self._time

    @property
    def pos(self):
        return self._p
    @pos.setter
    def pos(self, val):
        self._p = val

    @property
    def vel(self):
        return self._v
    @vel.setter
    def vel(self, val):
        self._v = val


def CreateArgument():
    parser = ap.ArgumentParser(
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
            "Gadget",
            nargs='+',
            help="Gadget files to analyze.",
    )

    parser.add_argument(
            "--hdf5",
            help="HDF5 files to use to get needed information.",
            default=glob("Data/*.hdf5")[-1],
    )

    parser.add_argument(
            "-o",
            "--out",
            type=ap.FileType("w"),
            default=sys.stdout,
    )

    parser.add_argument(
            "--RSelect",
            default=10.,
            type=float,
            help="Maximal radius to consider."
    )

    parser.add_argument(
            "--not-remove-dc",
            action="store_false",
            help="Substract density center information."
    )

    parser.add_argument(
            "--log",
            type=str,
            default="INFO",
            help="Log level."
    )

    parser.add_argument(
            "--save-txt",
            action="store_true",
            help="Saving in files all working particles."
    )

    args = parser.parse_args()
    args.log = getattr(logging, args.log.upper())

    return args

def GatherData(hdf5_file, *files):
    hdf5 = d.Data(hdf5_file)
    data = dict()

    for f in files:
        name = p.basename(f)

        data[name] = (
            hdf5.get(name, "timeparam", "x", "y", "z", "vx", "vy", "vz")[0],
            hdf5.get(name, "timeparam", "time")[0, 0],
            hdf5.get(name, "ids")[:, 0],
            f,
        )

    return data

def CalculateAnisotropy(center, time, ids, data, substract=True):
    calc = Object(data, center, time, ids, substract)

    v_r2 = calc.get_vr() ** 2
    v_t2 = calc.get_v2() - v_r2

    res = (calc.time, 1 - v_t2.sum() / (2.*v_r2.sum()))

    del calc
    return res


if __name__ == '__main__':
    args = CreateArgument()
    logging.basicConfig(level=logging.DEBUG)

    centers = GatherData(args.hdf5, *args.Gadget)

    for f in args.Gadget:
        calc = Analyse(args.hdf5, f, RSelect=args.RSelect) #, substract=args.not_remove_dc)
        v_r2 = calc.get_vr() ** 2
        v_t2 = calc.get_v2() - v_r2

        logging.info("Doing " + f)
        logging.debug("{0}".format(calc.pos.shape))
        if args.save_txt:
            np.savetxt("/tmp/" + p.basename(f) + "2.pos", calc.pos)
            np.savetxt("/tmp/" + p.basename(f) + "2.vel", calc.vel)

        print(
                calc.time,
                1 - v_t2.mean() / (2.*v_r2.mean()),
                # *CalculateAnisotropy(*centers[p.basename(f)], substract=args.not_remove_dc),
                file=args.out
        )
        del calc

