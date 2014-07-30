#!/usr/bin/env python
# encoding: utf-8

import os
import argparse as ap
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from LibThese import Models as m


def king_temp_cmd(args):
    fig = plt.figure(figsize=args.figsize)
    ax = fig.add_subplot(111)

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=args.XT_ANGLE)
    plt.setp(ax.yaxis.get_majorticklabels(), rotation=args.YT_ANGLE)
    ax.xaxis.set_tick_params(labelsize=args.T_FONT)
    ax.yaxis.set_tick_params(labelsize=args.T_FONT)

    ax.set_xscale("log")
    ax.set_yscale("log")

    # ax.set_title(r"Fonction $\zeta$", fontsize=args.L_FONT)
    ax.set_xlabel("$x$", fontsize=args.L_FONT)

    if args.normalized:
        ax.set_ylabel(r"$\zeta(x) / \zeta(0)$", fontsize=args.L_FONT)
    else:
        ax.set_ylabel(r"$\zeta(x)$", fontsize=args.L_FONT)

    fig2 = plt.figure(figsize=args.figsize)
    ax2 = fig2.add_subplot(111)

    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=args.XT_ANGLE)
    plt.setp(ax2.yaxis.get_majorticklabels(), rotation=args.YT_ANGLE)
    ax2.xaxis.set_tick_params(labelsize=args.T_FONT)
    ax2.yaxis.set_tick_params(labelsize=args.T_FONT)

    ax2.set_xscale("log")
    ax2.set_yscale("log")

    # ax2.set_title("Température pour le modèle de King", fontsize=args.L_FONT)
    ax2.set_xlabel("$x$", fontsize=args.L_FONT)

    if args.normalized:
        ax2.set_ylabel(r"$T(x) / T(0)$", fontsize=args.L_FONT)
    else:
        ax2.set_ylabel(r"$T(x)$", fontsize=args.L_FONT)

    for x in args.X:
        print("Doing ", x, "...", end=" ")
        king = m.ADimKing(x)
        king.Solve()

        zeta = (1. / king.rho(king.X[:, 0])) * king.X[:, 0] ** 2.5

        if args.normalized:
            ax.plot(
                king.x, zeta / zeta[0], "-",
                label=r"$W_0 = %g$" % x
            )

            ax2.plot(
                king.x, (
                    1 - 8./(15.*np.sqrt(np.pi)) * zeta
                ) / (
                    1 - 8./(15.*np.sqrt(np.pi)) * zeta[0]
                ), "-",
                label=r"$W_0 = %g$" % x
            )
        else:
            ax.plot(
                king.x, zeta, "-",
                label=r"$W_0 = %g$" % x
            )

            ax2.plot(
                king.x, 3. * args.dispersion * (
                    1 - 8./(15.*np.sqrt(np.pi)) * zeta
                ), "-",
                label=r"$W_0 = %g$" % x
            )

        print("Ok!")

    if args.normalized:
        ax.set_ylim(ymin=0.8)
        ax2.set_ylim(ymax=2.)

    if args.x_maxn is not None:
        ax.xaxis.set_major_locator(MaxNLocator(args.x_maxn))
        ax2.xaxis.set_major_locator(MaxNLocator(args.x_maxn))
    if args.y_maxn is not None:
        ax.yaxis.set_major_locator(MaxNLocator(args.y_maxn))
        ax2.yaxis.set_major_locator(MaxNLocator(args.y_maxn))

    if args.legend:
        ax.legend(loc="best")
        ax2.legend(loc="best")

    fig2.savefig(
        os.path.join(
            args.IMG_DIR,
            args.fname + "_temp",
        ) + ".pdf",
        transparent=True,
        bbox_inches='tight',
    )
    fig2.savefig(
        os.path.join(
            args.IMG_DIR,
            args.fname + "_temp",
        ) + ".png",
        transparent=True,
        bbox_inches='tight',
    )
    fig.savefig(
        os.path.join(
            args.IMG_DIR,
            args.fname,
        ) + ".pdf",
        transparent=True,
        bbox_inches='tight',
    )
    fig.savefig(
        os.path.join(
            args.IMG_DIR,
            args.fname,
        ) + ".png",
        transparent=True,
        bbox_inches='tight',
    )


def king_density_cmd(args):
    fig = plt.figure(figsize=args.figsize)
    ax = fig.add_subplot(111)

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=args.XT_ANGLE)
    plt.setp(ax.yaxis.get_majorticklabels(), rotation=args.YT_ANGLE)
    ax.xaxis.set_tick_params(labelsize=args.T_FONT)
    ax.yaxis.set_tick_params(labelsize=args.T_FONT)

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_title("Densité pour le modèle de King", fontsize=args.L_FONT)
    ax.set_xlabel("$x$", fontsize=args.L_FONT)

    if not args.normalized:
        ax.set_ylabel(r"$\rho^s(x)$", fontsize=args.L_FONT)
    else:
        ax.set_ylabel(r"$\rho^s(x) / \rho^s(0)$", fontsize=args.L_FONT)

    for x in args.X:
        print("Doing ", x, "...", end=" ")
        king = m.ADimKing(x)
        king.Solve()

        if not args.normalized:
            ax.plot(
                king.x, king.rho(king.X[:, 0]), "-",
                label=r"$W_0 = %g$" % x
            )
        else:
            ax.plot(
                king.x, king.rho(king.X[:, 0]) / king.rho(king.X[0, 0]), "-",
                label=r"$W_0 = %g$" % x
            )

        print("Ok!")

    if args.x_maxn is not None:
        ax.xaxis.set_major_locator(MaxNLocator(args.x_maxn))
    if args.y_maxn is not None:
        ax.yaxis.set_major_locator(MaxNLocator(args.y_maxn))

    ax.set_ylim(1e-6, king.rho(king.X[0, 0]) if not args.normalized else 2)
    # ax.set_xlim(0, 3)

    if args.legend:
        ax.legend(loc="best")

    fig.savefig(
        os.path.join(
            args.IMG_DIR,
            args.fname,
        ) + ".pdf",
        transparent=True,
        bbox_inches='tight',
    )
    fig.savefig(
        os.path.join(
            args.IMG_DIR,
            args.fname,
        ) + ".png",
        transparent=True,
        bbox_inches='tight',
    )


def sib_cmd(args):
    for x in args.X:
        print("Doing ", x, "...", end=" ")
        sib = m.SIB(x)
        sib.Solve()

        u = np.linspace(0.5, 3, 20)
        l = (1.5 - sib.X[-1, 0])/sib.X[-1, 1]

        fig = plt.figure(figsize=args.figsize)
        ax = fig.add_subplot(111)

        plt.setp(ax.xaxis.get_majorticklabels(), rotation=args.XT_ANGLE)
        plt.setp(ax.yaxis.get_majorticklabels(), rotation=args.YT_ANGLE)
        ax.xaxis.set_tick_params(labelsize=args.T_FONT)
        ax.yaxis.set_tick_params(labelsize=args.T_FONT)

        ax.plot(sib.X[:, 0], sib.X[:, 1], "-", label="SIB")
        ax.plot(u, 3.0/(2.0*l) - u/l, "-", label="Droite de Padmanabhan")
        ax.plot(
            [1], [2], "r+",
            ms=args.ms,
            markeredgewidth=args.markeredgewidth,
            label="SIS"
        )

        ax.set_ylim(0, 3)
        ax.set_xlim(0, 3)

        ax.set_xlabel("$u$", fontsize=args.L_FONT)
        ax.set_ylabel("$v$", fontsize=args.L_FONT)
        ax.set_title("$X=%g$" % x, fontsize=args.L_FONT)

        if args.x_maxn is not None:
            ax.xaxis.set_major_locator(MaxNLocator(args.x_maxn))
        if args.y_maxn is not None:
            ax.yaxis.set_major_locator(MaxNLocator(args.y_maxn))

        if args.legend:
            ax.legend(loc="best")

        fig.savefig(
            os.path.join(
                args.IMG_DIR,
                "milne_X%g" % x
            ) + ".pdf",
            transparent=True,
            bbox_inches='tight',
        )
        fig.savefig(
            os.path.join(
                args.IMG_DIR,
                "milne_X%g" % x
            ) + ".png",
            transparent=True,
            bbox_inches='tight',
        )
        print("Ok!")


def common_args():
    common = ap.ArgumentParser(
        add_help=False,
        # formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    common.add_argument(
        "-o",
        "--output-dir",
        help="Output directory for the graphics.",
        default=os.path.join(
            os.getenv("HOME"),
            "Documents/These/Latex/Manuscrit_GPLUM/graphe/"
        ),
        type=str,
        dest="IMG_DIR",
    )
    common.add_argument(
        "--label-font-size",
        help="Axis label font size.",
        default=12,
        type=int,
        dest="L_FONT",
    )
    common.add_argument(
        "--ticks-font-size",
        help="Ticks font size.",
        default=10,
        type=int,
        dest="T_FONT",
    )
    common.add_argument(
        "--xticks-number",
        help="Set the maximum number of xticks for the plot.",
        default=None,
        type=int,
        dest="x_maxn",
    )
    common.add_argument(
        "--yticks-number",
        help="Set the maximum number of yticks for the plot.",
        default=None,
        type=int,
        dest="y_maxn",
    )
    common.add_argument(
        "--angle-xticks",
        help="Turn the ticks from an angle.",
        default=0,
        type=float,
        dest="XT_ANGLE",
    )
    common.add_argument(
        "--angle-yticks",
        help="Turn the ticks from an angle.",
        default=0,
        type=float,
        dest="YT_ANGLE",
    )
    common.add_argument(
        "--figure-size",
        help="Set the figure size (unfortunately, it's in inches).",
        nargs=2,
        default=(3., 1.8),
        dest="figsize",
        type=float,
    )
    common.add_argument(
        "--legend",
        help="Print a legend.",
        action='store_true',
    )

    return common


def sib_args(sub, **def_parser_opt):
    parser = sub.add_parser(
        'sib',
        help="Plot the milne diagramme of the SIB.",
        **def_parser_opt
    )
    parser.set_defaults(func=sib_cmd)
    parser.add_argument(
        "X",
        help="Radius of the sib.",
        type=float,
        nargs='+',
    )
    common.add_argument(
        "--sis-marker-size",
        help="Marker Size for the SIS.",
        type=int,
        default=1,
        dest="ms",
    )
    common.add_argument(
        "--sis-marker-edge-width",
        help="Width of the marker for the size.",
        dest="markeredgewidth",
        type=int,
        default=1,
    )


def king_args(sub, **def_parser_opt):
    tmp = sub.add_parser(
        'king',
        help="Plot the density profile of the king Model.",
    )
    k_parser = tmp.add_subparsers()
    density = k_parser.add_parser(
        'density',
        help="Plot the density profile of the king Model.",
        **def_parser_opt
    )
    density.set_defaults(func=king_density_cmd)
    density.add_argument(
        "X",
        metavar="W0",
        help="Main parameter.",
        type=float,
        nargs='+',
    )
    density.add_argument(
        "--normalized",
        help="Plot the density normalized to 1.",
        dest="normalized",
        action="store_true",
    )
    density.add_argument(
        "--file-name",
        help="Name (without extension) to save the plot under.",
        dest="fname",
        default="king_profile",
    )

    temp = k_parser.add_parser(
        'temperature',
        help="Plot the temperature profile of the king Model.",
        **def_parser_opt
    )
    temp.set_defaults(func=king_temp_cmd)
    temp.add_argument(
        "X",
        metavar="W0",
        help="Main parameter.",
        type=float,
        nargs='+',
    )
    temp.add_argument(
        "-s",
        "--velocity-dispersion",
        help="Velocity dispersion of the object (the units will give the temperature units).",
        type=float,
        dest="dispersion",
        default=10.0,
    )
    temp.add_argument(
        "--normalized",
        help="Plot the temp normalized to 1.",
        dest="normalized",
        action="store_true",
    )
    temp.add_argument(
        "--file-name",
        help="Name (without extension) to save the plot under.",
        dest="fname",
        default="king_temperature_profile",
    )


if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers()
    common = common_args()

    sib_args(
        sub,
        parents=[common],
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )

    king_args(
        sub,
        parents=[common],
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )

    args = parser.parse_args()
    args.func(args)
