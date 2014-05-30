#!/usr/bin/env python
# encoding: utf-8

import os
import argparse as ap
import numpy as np

from matplotlib import pyplot as plt
from LibThese import Models as m


def king_cmd(args):
    fig = plt.figure(figsize=args.figsize)
    ax = fig.add_subplot(111)

    plt.setp(ax.xaxis.get_majorticklabels(), rotation=args.XT_ANGLE)
    plt.setp(ax.yaxis.get_majorticklabels(), rotation=args.YT_ANGLE)
    ax.xaxis.set_tick_params(labelsize=args.T_FONT)
    ax.yaxis.set_tick_params(labelsize=args.T_FONT)

    ax.set_title("Densité pour le modèle de King", fontsize=args.L_FONT)
    ax.set_xlabel("$x$", fontsize=args.L_FONT)

    if not args.normalized:
        ax.set_ylabel(r"$\rho^s(x)$", fontsize=args.L_FONT)
    else:
        ax.set_ylabel(r"$\rho^s(x) / \rho_0$", fontsize=args.L_FONT)

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
    common.add_argument(
        "--legend",
        help="Print a legend.",
        action='store_true',
    )

    return common


def sib_args(sub, common):
    parser = sub.add_parser(
        'sib',
        help="Plot the milne diagramme of the SIB.",
        parents=common,
    )
    parser.set_defaults(func=sib_cmd)
    parser.add_argument(
        "X",
        help="Radius of the sib.",
        type=float,
        nargs='+',
    )


def king_args(sub, common):
    parser = sub.add_parser(
        'king',
        help="Plot the density profile of the king Model.",
        parents=common,
    )
    parser.set_defaults(func=king_cmd)
    parser.add_argument(
        "W0",
        help="Main parameter.",
        type=float,
        nargs='+',
        dest="X",
    )
    parser.add_argument(
        "--normalized",
        help="Plot the density normalized to 1.",
        dest="normalized",
        action="store_true",
    )
    parser.add_argument(
        "--file-name",
        help="Name (without extension) to save the plot under.",
        dest="fname",
        default="king_profile",
    )


if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers()
    common = common_args()

    sib_args(
        sub,
        [common],
    )

    king_args(
        sub,
        [common],
    )

    args = parser.parse_args()
    args.func(args)
