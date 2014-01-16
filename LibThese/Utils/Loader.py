#! /usr/bin/env python
# -*- coding:Utf8 -*-

from ..Carte  import PhaseSpace   as ps
from ..Carte  import DensityCarte as dc

def loadPSMap(
		last = [ "0.1/res/ci_100", "0.2/res/ci_100", "0.3/res/ci_100", "0.4/res/ci_100", "0.5/res/ci_100" ], \
		vir  = [0.1, 0.2, 0.3, 0.4, 0.5], \
		mid  = None, \
		ori  = None, \
	):
	if mid is None:
		mid  = [ x.replace("100", "050") for x in last ]
	if ori is None:
		ori  = [ x.replace("100", "000") for x in last ]

	PSMap = dict()
	for v, o, m, l in zip(vir, ori, mid, last):
		PSMap[v] = [ ps.Map(o), ps.Map(m), ps.Map(l) ]

	return PSMap

def loadDCMap(
		last = [ "0.1/res/ci_100", "0.2/res/ci_100", "0.3/res/ci_100", "0.4/res/ci_100", "0.5/res/ci_100" ], \
		vir  = [0.1, 0.2, 0.3, 0.4, 0.5], \
		mid  = None,\
		ori  = None, \
	):
	if mid is None:
		mid  = [ x.replace("100", "050") for x in last ]
	if ori is None:
		ori  = [ x.replace("100", "000") for x in last ]

	DCMap = dict()
	for v, o, m, l in zip(vir, ori, mid, last):
		DCMap[v] = [ dc.Map(o), dc.Map(m), dc.Map(l) ]

	return DCMap


