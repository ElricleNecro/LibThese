#! /usr/bin/env python
# -*- coding:Utf8 -*-

import numpy as np

from . import load_gadget as lg
from ..Utils import Divers as ud

from InitialCond.Gadget import Gadget

class Filter(Gadget):
	def FromR(cls, rmax=5.):
		res = np.array( [] )
		for p, v, i in zip(cls.Part.NumpyPositions, cls.Part.NumpyVelocities, cls.Part.NumpyIdentities):
			if np.sum(p**2.) >= rmax**2.:
				res = np.resize(res, (res.shape[0] + 1, p.shape[0] + v.shape[0] + 1))
				res[res.shape[0]-1,:] = p.tolist() + v.tolist() + [i]

		return res

	def FromI(cls, ind=1000):
		for p, v, i in zip(cls.Part.NumpyPositions, cls.Part.NumpyVelocities, cls.Part.NumpyIdentities):
			if i >= ind:
				res = np.resize(res, (res.shape[0] + 1, p.shape[0] + v.shape[0] + 1))
				res[res.shape[0]-1,:] = p.tolist() + v.tolist() + [i]

		return res

	def FromAngularMomentum(cls, inter):
		print(inter)
		Angular = np.sqrt(
				np.sum(
					np.cross(
						cls.Part.NumpyPositions,
						cls.Part.NumpyVelocities
					)**2,
					axis=1
				)
			)
		bobo = (Angular >= inter[0]) & (Angular <= inter[1])
		resp = cls.Part.NumpyPositions[ bobo ]
		resv = cls.Part.NumpyVelocities[ bobo ]

		return resp, resv, Angular[ bobo ]

def filterfromr(*args, rmax=5.):
	"""Return an array [positions, velocities, identities] construct from the passing array.
	You can pass :
		(x) 3 array : positions, velocities, identities,
		(x) a 2D array : [positions, velocities, identities].
	then the limit radius (default : 5 pc).
	"""
	if len(args) == 1:
		var_iter = zip(args[0][:,0:3], args[0][:,3:6], args[0][:,6])
	elif len(args) == 3:
		var_iter = zip(args[0], args[1], args[2])
	else:
		raise ValueError("You must pass one or 3 arguments, see help function")

	ind = 1
	for p, v, i in var_iter:
		if np.sum(p*p) >= rmax**2:
			tmp = np.append(p, np.append(v, i))
			try:
				res = np.append(res, [tmp], axis=0)
				#print(ind, "Added to res")
				#ind+=1
			except NameError:
				res = np.array([tmp])
				#print(ind, "Create res")
				#ind+=1

	return res

def filterfromi(*args, ind=1000):
	"""Return an array [positions, velocities, identities] construct from the passing array.
	You can pass :
		(x) 3 array : positions, velocities, identities,
		(x) a 2D array : [positions, velocities, identities].
	then the limit radius (default : 5 pc).
	"""
	if len(args) == 1:
		var_iter = zip(args[0][:,0:3], args[0][:,3:6], args[0][:,6])
	elif len(args) == 3:
		var_iter = zip(args[0], args[1], args[2])
	else:
		raise ValueError("You must pass one or 3 arguments, see help function")

	for p, v, i in var_iter:
		if i >= ind:
			tmp = np.append(p, np.append(v, i))
			try:
				res = np.append(res, [tmp], axis=0)
				#print(ind, "Added to res")
				#ind+=1
			except NameError:
				res = np.array([tmp])
				#print(ind, "Create res")
				#ind+=1

	return res

def filterfromAngularMomentum(pos, vel, inter):
	"""This function return all positions and velocities of particles having Angular Momentum
	between inter[0] and inter[1].
	"""
	Angular = np.sqrt( np.sum( np.cross(pos, vel)**2, axis=1 ) )
	#np.sqrt( np.sum( tmp_pos[:]**2, axis=1 ) )
	#ind     = np.where()
	resp = pos[ (Angular >= inter[0]) & (Angular <= inter[1]) ]
	resv = vel[ (Angular >= inter[0]) & (Angular <= inter[1]) ]

	return resp, resv, Angular

def compare(gad1 : str, gad2 : str, rmax : float = None, ind : int = None):
	assert rmax != None or ind != None

	# Opening file pointer:
	f1, f2 = lg.ReadGadget(gad1), lg.ReadGadget(gad2)

	# Reading header:
	f1.read_header()
	f2.read_header()

	# Reading useful information (positions, velocities and identities):
	p1, v1, i1 = f1.get_positions(), f1.get_velocities(), f1.get_identities()
	p2, v2, i2 = f2.get_positions(), f2.get_velocities(), f2.get_identities()

	# Changing array shape:
	assert len(p1) == len(p2)
	p1.shape = p2.shape = (len(p1)//3,3)

	assert len(v1) == len(v2)
	v1.shape = v2.shape = (len(v1)//3,3)

	# Filter ending snapshot and getting information:
	if rmax != None:
		res = filterfromr(p2, v2, i2, rmax=rmax)
	elif ind != None:
		res = filterfromi(p2, v2, i2, ind=ind)

	# Getting their position from the begining snapshot:
	buf  = ud.VConcate( ud.VConcate(p1, v1), i1)
	for a in buf:
		if a[6] in res[:,6]:
			try:
				ret = np.append(ret, [a], axis=0)
			except NameError:
				ret = np.array([a])

	return ret, res

