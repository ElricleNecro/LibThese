# -*- coding:Utf8 -*-
import os
import argparse as ap
import logging as log

from LibThese.Plot import hdf5 as h

_registered_module = list()


class FromHDF5(object):

    def __init__(self, args):
        try:
            self.File = args.ref
        except OSError as e:
            log.fatal("Unable to open file '" + args.ref + "'.")
            raise e

    @property
    def File(self):
        return self._file

    @File.setter
    def File(self, val):
        if isinstance(val, str):
            self._file = h.Data(val)
        else:
            self._file = val

    @File.deleter
    def File(self):
        del self._file

    def __call__(self, frame, ax, *o, **kwo):
        data = self.File.get(frame, *o)
        for i in range(1, data.shape[1]):
            ax.plot(data[:, 0], data[:, i])

        return frame


def set_common_args(parser):
    parser.add_argument(
        "Files",
        nargs='+',
        help="File to plot.",
    )
    parser.add_argument(
        "-r",
        "--ref",
        type=str,
        help="File in which we get all needed information.",
    )
    parser.add_argument(
        "--tmp-dir",
        type=str,
        help="Directory into which the script will create all graphics.",
        default="/tmp/",
    )
    parser.add_argument(
        "--xlabel",
        type=str,
        help="Set X axis label.",
    )
    parser.add_argument(
        "--ylabel",
        type=str,
        help="Set Y axis label.",
    )
    parser.add_argument(
        "--xlim",
        type=float,
        help="Set X axis limits.",
        nargs=2,
    )
    parser.add_argument(
        "--ylim",
        type=float,
        help="Set Y axis limits.",
        nargs=2,
    )
    parser.add_argument(
        "--xscale",
        type=str,
        help="Set X axis scale.",
    )
    parser.add_argument(
        "--yscale",
        type=str,
        help="Set Y axis scale.",
    )
    parser.add_argument(
        "--grid",
        action="store_true",
        help="Print a grid on graphics?",
    )
    parser.add_argument(
        "-p",
        "--parallel",
        help="Launch multiple instance at once.",
        action='store_true',
    )
    parser.add_argument(
        "--nb-proc",
        help="Number of thread to launch.",
        type=int,
        default=4,
    )

# class ArgumentParser(object):
    # def __init__(self):
        # pass

    # def get_args(self):
        #parser = ap.ArgumentParser()
        #sub = parser.add_subparsers(help="What do we want to plot?")
        # for a in _registered_module:
            # a(sub)


def get_args():
    parser = ap.ArgumentParser()
    sub = parser.add_subparsers(help="What do we want to plot?")
    common_args = ap.ArgumentParser(
        add_help=False,
    )
    set_common_args(
        common_args
    )
    for a in _registered_module:
        a(sub, [ common_args ])

    return parser.parse_args()


def register_module(args_function):
    _registered_module.append(args_function)
