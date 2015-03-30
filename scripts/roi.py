#!/usr/bin/env python
# encoding: utf-8

"""
"""


import argparse as ap
import os, sys

import matplotlib
import numpy as np

matplotlib.rcParams['figure.figsize'] = (3., 1.8)
matplotlib.rcParams['axes.grid'] = True

from matplotlib.ticker import MaxNLocator
# from matplotlib import cm
from matplotlib import pyplot as plt

from scipy.interpolate import interp1d, Rbf, InterpolatedUnivariateSpline

# from LibThese import Carte as c
from LibThese import Data as h

from os.path import basename, splitext

from yaml import load


PREFIX = os.path.dirname(sys.argv[0])
# PREFIX = os.path.dirname(__file__)
CONFIG_DIR = os.path.abspath(
    os.path.join(
        PREFIX,
        "../share/LibThese"
    )
)
interp_method = {
    interp1d.__name__ : interp1d,
    Rbf.__name__ : Rbf,
    InterpolatedUnivariateSpline.__name__ : InterpolatedUnivariateSpline,
}


class Filter(object):
    """Class made to deal with data filtering, file by file.
    Take all filter in the form "filename"=[value to filter].
    """
    def __init__(self, **kwargs):
        """
        """
        self._filter = kwargs

    def __getitem__(self, key):
        return self._filter[key]

    def __setitem__(self, key, value):
        if not isinstance(value, list):
            raise TypeError("Take only list or np.array")
        self._filter[key] = value

    def dataFilter(self, array, fname, copy=False):
        if copy:
            res = array.copy()
        else:
            res = array

        values = self[
                fname
        ]
        col = res.shape[1]
        for x1, x2 in values:
            c = np.ma.masked_inside(res[:, 0], x1, x2)
            tmp_mask = np.hstack(
                (
                    c.mask.reshape(c.shape[0], 1),
                    np.array(
                        [False]*(c.shape[0]*(col-1))
                        ).reshape(c.shape[0], col-1)
                    )
            )
            res = np.ma.MaskedArray(res, mask=tmp_mask)

        return np.ma.compress_rows(res)


def move_average(data, window_size=10):
    """.. function:: move_average(data[, window_size=10])
            Smooth the given data array using a moving average.

    :param data: data to smooth.
    :type data: np.array
    :param window_size: number of point to consider.
    :type window_size: integer
    :rtype: np.array
    :returns: smoothed data.
    """
    extended_data = np.hstack([[data[0]] * (window_size - 1), data])
    weightings = np.repeat(1.0, window_size) / window_size
    return np.convolve(
        extended_data,
        weightings
    )[
        window_size - 1: -(window_size - 1)
    ]

def movingaverage(values, window_size=5):
    """.. function:: movingaverage(values[, window_size=5])
            Smooth the given data array using a moving average.

    :param values: data to smooth.
    :type values: np.array
    :param window_size: number of point to consider.
    :type window_size: integer
    :rtype: np.array
    :returns: smoothed data.
    """
    weigths = np.repeat(1.0, window_size)/window_size
    smas = np.convolve(values, weigths, 'valid')
    return smas

def movingaverage_2(values, window_size=5):
    """.. function:: movingaverage_2(values[, window_size=5])
            Smooth the given data array using a moving average.

    :param values: data to smooth.
    :type values: np.array
    :param window_size: number of point to consider.
    :type window_size: integer
    :rtype: np.array
    :returns: smoothed data.
    """
    win = np.ones(int(window_size))/float(window_size)
    return np.convolve(values, win, 'same')

def createinterpolation(config, data, *args, **kwargs):
    """Interpolate data.
    """
    #tmp = np.ma.compress_rows(data)
    tmp = data
    func = list()
    config["interpolation"]["kwargs"].update(kwargs)
    for i in range(1, tmp.shape[1]):
        func.append(
            interp_method[
                config["interpolation"]["method"]
            ](
                tmp[:, 0],
                tmp[:, i],
                *args,
                **config["interpolation"]["kwargs"]
            )
        )

    return tuple(func)

def cleanedTime(td, tr, name, config, filter):
    T_carac_filter = (
        filter.dataFilter(
            td,
            name,
            copy=True,
            ),
        filter.dataFilter(
            tr,
            name,
            copy=True,
            )
    )


    T_d_n = np.zeros_like(T_carac_filter[0])
    T_r_n = np.zeros_like(T_carac_filter[1])
    T_d_n[0, 1] = td[0, 0] / td[0, 1]
    T_r_n[0, 1] = tr[0, 0] / tr[0, 1]

    print(name, T_carac_filter[0][:, 0].min(), T_carac_filter[0][:, 0].max())

    for i in range(1, T_d_n.shape[0]):
        T_d_n[i, 0] = T_carac_filter[0][i, 0]
        T_d_n[i, 1] = T_d_n[i-1, 1] + (
            T_carac_filter[0][i, 0] - T_carac_filter[0][i-1, 0]
        ) / T_carac_filter[0][i-1, 1]

        T_r_n[i, 0] = T_carac_filter[1][i, 0]
        T_r_n[i, 1] = T_r_n[i-1, 1] + (
            T_carac_filter[1][i, 0] - T_carac_filter[1][i-1, 0]
        ) / T_carac_filter[1][i-1, 1]

    print(T_d_n[:, 0].min(), T_d_n[:, 0].max())

    return (
        createinterpolation(
            config,
            T_d_n,
        )[0],
        createinterpolation(
            config,
            T_r_n,
        )[0]
    )

def calculateTime(config, data):
    T_d = np.array(
        [0.]*(2*len(data._file)),
        dtype=np.float64
    )
    T_d.shape = (T_d.shape[0]//2, 2)

    T_rel = np.zeros_like(T_d)

    radius = data.get_all_time(
        "time",
        "r10",
        "r50",
        "r90"
    )

    for i, t in enumerate(data._file):
        m = data.get(t, "masse")
        time = data.get_time(t, "time")
        N = data.get(t, "ids").shape[0]
        rho, = createinterpolation(
            config,
            data.get(
                t,
                "densite_log"
            ),
        )
        m1 = m[m.shape[0]//2, 1]
        T_d[i, 0] = time
        T_rel[i, 0] = time
        T_d[i, 1] = np.pi * np.sqrt(radius[i, 2]**3. / (2.*m1))
        T_rel[i, 1] = N * m1 / (4*np.pi**2. * radius[i, 2]**3. * rho(radius[i, 2]) * np.log(radius[i, 2] / 0.001)) * T_d[i, 1]

    return T_d, T_rel

def plot_densite(rho, name, ylim=(1e-4, 10), xlim=(1e-2, 1e1)):
    f = plt.figure(figsize=(4, 2.8))
    a = f.add_subplot(
        111,
        xscale="log",
        yscale="log",
        ylim=ylim,
        xlim=xlim,
        xlabel=r"$r$",
        ylabel=r"$\rho(r)$"
    )
    for r in rho:
        a.plot(r[:, 0], r[:, 1], "-")

    f.savefig(
        "ROI_densite_" + splitext(name)[0] + ".png",
        transparent=True,
        bbox_inches="tight",
        format="png"
    )
    f.savefig(
        "ROI_densite_" +
        splitext(name)[0] +
        ".pdf",
        transparent=True,
        bbox_inches="tight",
        format="pdf"
    )

def plot_roi(config, t, T_carac_JP, r1, r2, r3, a_1, a_2, ani, f_b, name):
    f = plt.figure(figsize=(4, 2.8))
    a = f.add_subplot(111)
    a.plot(
        T_carac_JP[0](t), r1(t), "-",
        T_carac_JP[0](t), r2(t), "-",
        T_carac_JP[0](t), r3(t), "-",
    )
    a.set_xlabel(r"$t'$")
    a.set_ylabel(r"$R_{10}$, $R_{50}$, $R_{90}$")
    f.savefig(
        "ROI_radius_" + splitext(name)[0] + ".png",
        transparent=True,
        bbox_inches="tight",
        format="png"
    )
    f.savefig(
        "ROI_radius_" +
        splitext(name)[0] +
        ".pdf",
        transparent=True,
        bbox_inches="tight",
        format="pdf"
    )
    f, a = plt.subplots(
        2,
        1,
        sharex=True,
        squeeze=True,
        figsize=(4, 3.8)
    )
    f.subplots_adjust(hspace=0.0, wspace=0.0)
    # axial = s.get_all_time("time", "s_ratio", "g_ratio", "Anisotropy")
    # axial = DataFilter(axial, filter_list[s.name])
    # a_1, a_2, ani = CreateInterpolation(axial, interpolation, kind=kind)
    # f_b, _, f_b2 = CreateInterpolation(
        # data_aniso[
            # s.name], interpolation, kind=kind)

    a[0].plot(
        T_carac_JP[0](t), a_1(t), "b-",
        T_carac_JP[0](t), a_2(t), "r-",
    )
    a[0].yaxis.set_major_locator(MaxNLocator(config["y_maxn"], prune="lower"))
    a[0].set_ylabel(r"$a_1$, $a_2$")
    if "ax_ylim" in config["roi_plot"]:
        a[0].set_ylim(config["roi_plot"]["ax_ylim"])
    if "ax_xlim" in config["roi_plot"]:
        a[0].set_xlim(config["roi_plot"]["ax_xlim"])

    a[1].plot(T_carac_JP[0](t), f_b(t), "-")
    a[1].yaxis.set_major_locator(MaxNLocator(config["y_maxn"], prune="upper"))
    a[1].set_ylabel(r"$\beta$")
    a[1].set_xlabel(r"$t'$")
    if "b_ylim" in config["roi_plot"]:
        a[0].set_ylim(config["roi_plot"]["b_ylim"])
    if "b_xlim" in config["roi_plot"]:
        a[0].set_xlim(config["roi_plot"]["b_xlim"])

    f.savefig(
        "ROI_" + splitext(name)[0] + ".png",
        transparent=True,
        bbox_inches="tight",
        format="png"
    )
    f.savefig(
        "ROI_" + splitext(name)[0] + ".pdf",
        transparent=True,
        bbox_inches="tight",
        format="pdf"
    )

def plot_interval(config, t, T_carac_JP, r1, r2, r3, a_1, a_2, ani, f_b, name):
    # t_min, t_max = 20, 50
    t_min, t_max = config["tmin"], config["tmax"]
    # interval = slice(t_min, t_max+1)

    f, a = plt.subplots(
        2, 1,
        sharex=True,
        squeeze=True,
        subplot_kw=dict(
            xlim=(
                T_carac_JP[0]([t_min])[0],
                T_carac_JP[0]([t_max])[0]
            )
        ),
        figsize=(3, 2.8)
    )
    f.subplots_adjust(hspace=0.0, wspace=0.0)

    # axial = s.get_all_time("time", "s_ratio", "g_ratio", "Anisotropy")
    # axial = DataFilter(axial, filter_list[s.name])
    # a_1, a_2, ani = CreateInterpolation(axial, interpolation, kind=kind)
    # f_b, _, f_b2 = CreateInterpolation(
        # data_aniso[
            # s.name], interpolation, kind=kind)
    t = np.linspace(t_min, t_max, 50)

    a[0].plot(
        T_carac_JP[0](t), a_1(t), "b-",
        T_carac_JP[0](t), a_2(t), "r-",
    )
    #a[0].plot(t, t)
    a[0].set_ylim(0., 1.5)
    a[0].yaxis.set_major_locator(MaxNLocator(config["y_maxn"]))
    a[0].set_ylabel(r"$a_1$, $a_2$")
    # a[1].plot(
    #	T_carac_JP[s.name][0](t), ani(t), "-",
    #)
    a[1].plot(T_carac_JP[0](t), f_b(t), "-")
    # a[1].set_ylim(ymax=0.0)
    a[1].yaxis.set_major_locator(MaxNLocator(config["y_maxn"]))
    a[1].set_ylabel(r"$\beta$")
    a[1].set_xlabel(r"$t'$")

    f.savefig(
        "ROI_zoom_" +
        splitext(name)[0] +
        ".png",
        transparent=True,
        bbox_inches="tight",
        format="png")
    f.savefig(
        "ROI_zoom_" +
        splitext(name)[0] +
        ".pdf",
        transparent=True,
        bbox_inches="tight",
        format="pdf")

def parse_args():
    """Creating arguments.
    """
    parser = ap.ArgumentParser(
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "hdf5",
        type=str,
        help="HDF5 file to analyze.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=ap.FileType("r"),
        default=os.path.join(
            CONFIG_DIR,
            "config.yml"
        ),
        help="Configuration file."
    )
    parser.add_argument(
        "-f",
        "--filter",
        type=ap.FileType("r"),
        default=os.path.join(
            CONFIG_DIR,
            "filter.yml"
        ),
        help="Data to filter."
    )
    parser.add_argument(
        "-a",
        "--aniso",
        type=str,
        default="Data/aniso.dat",
        help="Corrected anisotropie."
    )

    return parser.parse_args()

def main():
    """Main program
    """
    args = parse_args()

    config = load(args.config)

    data = h.Data(args.hdf5)

    rho = list()
    for snap in config["snapshots"]:
        rho.append(
            data.get(snap, "densite_log")
        )

    filtre = Filter(**load(args.filter))
    Td, Tr = calculateTime(config, data)
    Td, Tr = cleanedTime(
        Td,
        Tr,
        basename(args.hdf5),
        config,
        filtre
    )

    try:
        data_aniso = createinterpolation(
            config,
            filtre.dataFilter(
                np.loadtxt(args.aniso),
                basename(args.hdf5),
            )
        )[0]
    except FileNotFoundError:
        raise FileNotFoundError("As Anisotropy inside hdf5 is deprecated, you need the external file given by verif_python.py.")

    rad = data.get_all_time(
        "time",
        "s_ratio",
        "g_ratio",
        "Anisotropy",
        "r10",
        "r50",
        "r90"
    )
    rad = filtre.dataFilter(rad, basename(args.hdf5))
    a_1, a_2, ani, r1, r2, r3 = createinterpolation(config, rad)
    t = np.linspace(rad[0, 0], rad[-1, 0], 200)

    plot_densite(
        rho,
        basename(args.hdf5),
        **config["density_plot"]
    )

    plot_roi(
        config,
        t,
        (Td, Tr),
        r1, r2, r3,
        a_1, a_2,
        ani,
        data_aniso,
        basename(args.hdf5),
    )

    plot_interval(
        config,
        t,
        (Td, Tr),
        r1, r2, r3,
        a_1, a_2,
        ani,
        data_aniso,
        basename(args.hdf5),
    )


if __name__ == '__main__':
    main()
