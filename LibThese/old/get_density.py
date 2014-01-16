#! /usr/bin/env python3
# -*- coding:Utf8 -*-

from numpy import sqrt, histogram, pi, log, linspace

def get_density(data, NbBin=100, Mass=1.0):
	"""Calcul la densité sur un jeu de donnée en position."""

	r = sqrt(data[:,0]**2.0 + data[:,1]**2.0 + data[:,2]**2.0)
	print(len(r))
	print(r)

	hist, r_edges = histogram(r, bins=NbBin, range=(0.0, r.max()) )
	print(r_edges)

	hist = hist * Mass

	for i, _ in enumerate(hist):
#		if i > 0:
		hist[i] /= (4.0*pi*(r_edges[i+1] - r_edges[i])**3.0)
#		else:
#			hist[i] /= (4.0*pi*(r_edges[i])**3.0)

	return hist, r_edges

def _ok(i, r):
	if i > 0:
		return r[i]
	elif i == 0:
		return 0.0
	else:
		raise IndexError("WTF!!!! Qu'est ce que c'est que ce micmac !!! " + str(i))

def get_logdensity(data, NbBin=100, Mass=1.0):
	"""Calcul la densité avec pas logarithmique constant sur un jeu de positions."""

	r  = sqrt(data[:,0]**2.0 + data[:,1]**2.0 + data[:,2]**2.0)
	lr = log(r)

	hist, edges = histogram(r, bins=10.0**(linspace(lr.min(), lr.max(), NbBin)))
	hist *= Mass

	print(r.min(), r.max(), '\n', 10**lr.min(), 10**lr.max())
	print(hist, len(edges), len(hist))

	for i, _ in enumerate(hist):
		hist[i] /= 4.0/3.0 * pi * edges[i+1]**3.0 - 4.0/3.0 * pi * _ok(i, edges)**3.0

	return hist, edges

