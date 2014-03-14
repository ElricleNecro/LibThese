# -*- coding:Utf8 -*-

import matplotlib.colorbar as cb
import matplotlib.pyplot   as plt
import matplotlib.cm	   as cm
import itertools	   as it
import numpy		   as np

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.axes	     import Subplot
from ..Utils		     import Histo as hs
from ..Utils.Divers	     import VConcate
from ..Gadget.Filter	     import Filter

__all__ = [
	"PhaseSpaceData",
	"PSPlot",
]

		#""".. py:class:: PhaseSpaceData(file, [AngularBins=None, format=1, nb_file=1, nb_bin=100, r_min=None, r_max=None, v_min=None, v_max=None, j_min=None, j_max=None])
		#This class read a Gadget file and calculate the radius, the radial velocity and the angular momentum of each particules.
		#"""
class PhaseSpaceData(Filter):
	"""This class read a Gadget file and calculate the radius, the radial velocity and
	the angular momentum of each particles.

	:param str file: Gadget file to load.

	:param AngularBins: Bins of angular momentum to use.
	:type AngularBins: iterable or None

	:param int format: Gadget file format (1-3).

	:param int nb_file: Number of file composing the snapshot.

	:param int nb_bin: Number of bin to use.

	:param r_min: Minimum value of the radius.
	:type r_min: float or None

	:param r_max: Maximum value of the radius.
	:type r_max: float or None

	:param v_min: Minimum value of the velocity.
	:type v_min: float or None

	:param v_max: Maximum value of the velocity.
	:type v_max: float or None

	:param j_min: Minimum value of the angular momentum.
	:type j_min: float or None

	:param j_max: Maximum value of the angular momentum.
	:type j_max: float or None

	:raises ValueError: if the format is not recognised.
	"""
	def __init__(	self,
			file,
			AngularBins=None,
			format=1,
			nb_file=1,
			nb_bin=100,
			r_min=None,
			r_max=None,
			v_min=None,
			v_max=None,
			j_min=None,
			j_max=None,
			move_pos=None,
			move_vel=None,
			j_bin=None,
			r_bin=None,
			v_bin=None,
	):
		super(Filter, self).__init__(file)
		if format == 1:
			super(Filter, self)._read_format1(nb_file)
		elif format == 2:
			super(Filter, self)._read_format2(nb_file)
		elif format == 3:
			super(Filter, self)._read_format3(nb_file)
		else:
			raise ValueError("Unrecognised file format:", format)

		if move_pos is not None:
			self.Part.Translate(move_pos)
		if move_vel is not None:
			self.Part.AddVelocity(move_vel)

		if AngularBins is not None:
			try:
				_ = (e for e in AngularBins)
			except TypeError:
				AngularBins = [ AngularBins ]
			self._angular_bins  = AngularBins
		else:
			self._angular_bins  = None

		self.nb_bin = nb_bin
		if r_bin is None:
			self._r_bin = self.nb_bin
		else:
			self._r_bin = r_bin
		if v_bin is None:
			self._v_bin = self.nb_bin
		else:
			self._v_bin = v_bin
		if j_bin is None:
			self._j_bin = self.nb_bin
		else:
			self._j_bin = j_bin

		self._do_bins(
			r_min,
			r_max,
			v_min,
			v_max,
			j_min,
			j_max
		)
		self.Create()

	def _do_bins(self,
			r_min,
			r_max,
			v_min,
			v_max,
			j_min,
			j_max
	):
		############
		# Calculs des quantités physiques voulues pour l'espace des phase :
		###################################################################
		self._r     = self.get_r(self.Part.NumpyPositions)
		self._v     = self.get_rv(self.Part.NumpyPositions, self.Part.NumpyVelocities) / self._r
		self._j     = self.get_j(self.Part.NumpyPositions, self.Part.NumpyVelocities)

		if r_min is None:
			r_min = self.r.min()
		if r_max is None:
			r_max = self.r.max()

		if v_min is None:
			v_min = self.v.min()
		if v_max is None:
			v_max = self.v.max()

		if j_min is None:
			j_min = self.j.min()
		if j_max is None:
			j_max = self.j.max()

		##################
		# Calculs des intervalles pour le comptage :
		############################################
		self._bins_r = 10**np.linspace(
						np.log10(r_min),
						np.log10(r_max),
						self._r_bin+1
				)
		self._bins_v = np.linspace(
						v_min,
						v_max,
						self._v_bin+1
				)
		self._bins_j = np.linspace(
						j_min,
						j_max,
						self._j_bin+1
				)

	def Create(self):
		################
		# Calculs de la position de chaque valeurs de r, v_r et j dans les intervalles :
		################################################################################
		self._pos_j = np.digitize(self._j, self._bins_j)
		self._pos_r = np.digitize(self._r, self._bins_r)
		self._pos_v = np.digitize(self._v, self._bins_v)

		##################
		# Classement des tableaux de position :
		#######################################
		self._corres_ind = np.lexsort( (self._pos_r, self._pos_v, self._pos_j) )

		##################
		# Récupèration de l'indice auquel chaque bin se termine :
		#########################################################
		self._bin_end_in_corres = np.nonzero( self._pos_j[self._corres_ind[:-1]] - self._pos_j[self._corres_ind[1:]] )[0]

		tmp                     = self._pos_j[ self._corres_ind[ self._bin_end_in_corres ] ]
		self._dict_corres_value = dict()
		prec                    = -1

		for i, pj in enumerate(tmp):
			self._dict_corres_value[ pj ] = ( prec ,self._bin_end_in_corres[i])
			prec                          = self._bin_end_in_corres[i]
		self._dict_corres_value[ self._pos_j[self._corres_ind[-1]] ] = (prec, self.nb_bin)

	def GetSliceJ(self, ang):
		"""
		:param float ang: Angular momentum.
		:returns: radius
		:rtype: np.array
		:returns: radial velocity
		:rtype: np.array
		:returns: angular momentum
		:rtype: np.array
		:returns: bin size
		:rtype: float
		"""
		pos_in_bin_j = np.digitize( [ang], self.j_bin)[0]
		if not pos_in_bin_j in self._dict_corres_value:
			raise ValueError("Bad value, nothing in it's bin: j (=" + str(ang) + ") in [" + str(self.j.min()) + ", " + str(self.j.max()) + "]")
		indice = self._dict_corres_value[ pos_in_bin_j ]

		##########################################################################################################################
		# Solution dégueulasse. Trouver mieux.
		##########################################################################################################################
		try:
			dj = self.j_bin[pos_in_bin_j+1] - self.j_bin[pos_in_bin_j]
		except IndexError:
			print("Solution dégueulasse !")
			dj = self.j_bin[1] - self.j_bin[0]

		return		self._r[ self._corres_ind[ (indice[0]+1):(indice[1]+1) ] ], \
				self._v[ self._corres_ind[ (indice[0]+1):(indice[1]+1) ] ], \
				self._j[ self._corres_ind[ (indice[0]+1):(indice[1]+1) ] ], \
				dj
				#self._j[ self._corres_ind[ (indice[0]+1):(indice[1]+1) ] + 1 ] - self._j[ self._corres_ind[ (indice[0]+1):(indice[1]+1) ] ]

	@property
	def r(self):
		return self._r
	@property
	def v(self):
		return self._v
	@property
	def j(self):
		return self._j

	@property
	def r_bin(self):
		return self._bins_r
	@r_bin.setter
	def r_bin(self, val):
		self._bins_r = np.asarray(val)

	@property
	def v_r_bin(self):
		return self._bins_v
	@v_r_bin.setter
	def v_r_bin(self, val):
		self._bins_v = np.asarray(val)

	@property
	def j_bin(self):
		return self._bins_j
	@j_bin.setter
	def j_bin(self, val):
		self._bins_j = np.asarray(val)


	@staticmethod
	def get_r(pos):
		return np.sqrt( np.sum( pos[:]**2, axis=1 ) )
	@staticmethod
	def get_rv(pos, vit):
		return np.sum(pos * vit, axis=1)
	@staticmethod
	def get_j(pos, vit):
		return  np.sqrt(
				np.sum(
					np.cross(
						pos,
						vit
					)**2,
					axis=1
				)
			)


class PSPlot(PhaseSpaceData):
	def __init__(self, file, **kwargs):
		if "AxsLog" not in kwargs:
			kwargs["AxsLog"] = False
		if "nbbin" not in kwargs:
			kwargs["nbbin"]  = 100
		if "Log" not in kwargs:
			self._log_data = False
		else:
			self._log_data = True
			del kwargs["Log"]

		if kwargs["AxsLog"]:
			if isinstance(kwargs["nbbin"], int):
				nb_point = kwargs["nbbin"]
			self.nbbin = (
					10.**np.linspace(
							np.log10( kwargs["r_min"] ),
							np.log10( kwargs["r_max"] ),
							nb_point
					),
					np.linspace(
						kwargs["v_min"],
						kwargs["v_max"],
						nb_point
					)
				)
			#self.axs.set_xscale("log")
			self.AxsLog = True
		elif not isinstance(kwargs["nbbin"], int):
			self.nbbin = kwargs["nbbin"]
		else:
			self.nbbin = 100

		del kwargs["AxsLog"]
		del kwargs["nbbin"]

		super(PSPlot, self).__init__(file, **kwargs)

	def CreateHistogram(self, r, vr, j, dj, j_norm=False):
		self.hist, self.X, self.Y = np.histogram2d(
						r,
						vr,
						#bins=self.nbbin
						bins=(
							self._bins_r,
							self._bins_v,
							#10**np.linspace(np.log10(r.min()), np.log10(r.max()), self.nbbin),
							#np.linspace(vr.min(), vr.max(), self.nbbin),
						)
					)
		self.hist = self.hist.T

		if j_norm and j is not None:
			l_dj = 2.0 * np.pi * j * dj

		for i in range( len( self.hist ) ):
			self.hist[i, :] = self.hist[i, :] / (self.Y[i+1] - self.Y[i])
			self.hist[:, i] = self.hist[:, i] / (4./3.*np.pi * (self.X[i+1]**3 - self.X[i]**3))
			if j_norm and j is not None:
				self.hist[:, i] = self.hist[:, i] / ( l_dj ) * self.X[i]**2

	def GetSliceJ(self, binJ=None):
		if binJ is None:
			r, vr, _, dj = super(PSPlot, self).r, super(PSPlot, self).v, super(PSPlot, self).j, 1
			#j[:] = 1
			j_norm = False
		else:
			r, vr, _, dj = super(PSPlot, self).GetSliceJ(binJ)
			j_norm = True

		self.CreateHistogram(r, vr, binJ, dj, j_norm)

	def Plot(self, fig=None, ax=None, log=False, colorbar=False, vmin=None, vmax=None):
		if log:
			to_plot = np.zeros_like(self.hist)
			tmp     = np.ma.log10(
					np.ma.masked_where(
						self.hist <= 0,
						self.hist
					)
			)
			to_plot[ tmp.nonzero() ] = tmp[ tmp.nonzero() ]
		else:
			to_plot = self.hist

		if ax is None:
			if fig is None:
				fig = plt.figure()
			ax = fig.add_subplot(
					111,
					ylim   = (self.Y.min(), self.Y.max()),
					xlim   = (self.X.min(), self.X.max()),
					#ylim   = (self.v.min(), self.v.max()),
					#xlim   = (self.r.min(), self.r.max()),
					#ylim   = (-2, 2),
					#xlim   = (1e-2, 20),
					xscale = "log",
			)
		if ax is not None and fig is None:
			fig = ax.figure

		cb = ax.pcolormesh(self.X, self.Y, to_plot, vmin=vmin, vmax=vmax)
		if colorbar:
			fig.colorbar(cb)

		return fig, ax, cb



class Map(hs.Histogram):
	"""Classe s'occupant de gérer les histogrammes pour tracer les cartes de densité du systèmes.
	"""
	def __init__(self, *args, **kwargs):
		""" Nom de fichier, tableau ou fichier gadget. Paramètre très similaire à DensityCarte.
		Paramètre :
			nbbin			:: 300
			ind = (0, 1)		:: Indices à utiliser pour créer les axes de l'histogramme.
			FieldRange = None	:: Inutile actuellement.
			move			:: Translation à appliquer sur les positions.
			set_units = (1., 1.)	:: Tuple (pos, vit) pour transformer les unités.
			y_axis			:: Choix de l'espace des phases à tracer ("rvr" ou "rv").
			logger			:: log.Logger ou nom du logger.
			log_level = 0		:: Niveau de log.
		"""
		if "move" in kwargs:
			move = kwargs["move"]
			del kwargs["move"]
		else:
			move = np.array( [0., 0., 0.] )

		if "y_axis" in kwargs and kwargs["y_axis"] == "rv":
			mein = True
			del kwargs["y_axis"]
		else:
			mein = False

		if "set_units" in kwargs:
			units = kwargs["set_units"]
			del kwargs["set_units"]
		else:
			units = (1., 1.)

		# Initialisation de la classe mère :
		super(Map, self).__init__(*args, **kwargs)

		if isinstance(args[0], str):
			# Si c'est un fichier gadget :
			tmp = hs.ReadGadget(args[0])
			if tmp.border_block() == 256:
				self.head = tmp.read_header()
				# Lecture des positions :
				tmp_pos = tmp.get_positions()
				tmp_pos.shape = (len(tmp_pos)/3, 3)

				# Lecture des vitesses :
				tmp_vit = tmp.get_velocities()
				tmp_vit.shape = (len(tmp_vit)/3, 3)

				# Est-ce que l'on veut un type particulier ?
				if "dtype" in kwargs and kwargs["dtype"] is not None:
					dtype = kwargs["dtype"]
					self.head = tmp.read_header()

					# Récupération du nombre de particule voulues :
					wanted = tmp.header["Npart"][dtype]
					before = sum(tmp.header["Npart"][0:dtype])

					# filtrage des positions-vitesses :
					tmp_pos    = tmp_pos[before:(before+wanted)]
					tmp_vit    = tmp_vit[before:(before+wanted)]
		else:
			tmp_pos = self.don[:, 0:3].copy()
			tmp_vit = self.don[:, 3:6].copy()

		tmp_pos = tmp_pos * units[0]
		tmp_vit = tmp_vit * units[1]

		tmp_pos = tmp_pos - move

		if mein:
			self.log.info("Using v vs r.")
			don1 = np.sqrt( np.sum( tmp_pos[:]**2, axis=1 ) )
			don2 = np.sqrt( np.sum( tmp_vit[:]**2, axis=1 ) )
			self.don = VConcate(don1, don2)
		else:
			self.log.info(r"Using $\vec{v}.\vec{r} / |r|$ vs r")
			self.don = self.rvr(tmp_pos, tmp_vit)

	@staticmethod
	def rvr(tmp_pos, tmp_vit):
		don2 = np.sum(tmp_pos * tmp_vit, axis=1) / np.sqrt( np.sum( tmp_pos[:]**2, axis=1 ) )
		don1 = np.sqrt( np.sum( tmp_pos[:]**2, axis=1 ) )

		return VConcate(don1, don2)

	def Set_AllDim(self, fact):
		"""Multiplie chaque dimension par fact.
		"""
		for i in range(0, 2):
			super().Set_dim(i, fact)

	def _calc(self, pfilter=lambda z: z, log=False, density=False, masked=False, v2=False):
		back_don = np.copy(self.don)
		self.don = pfilter(self.don)
		X, Y, Z = super().Create_Histo()

		self.compt = Z.copy()

		if log:
			masked = True
		if density:
			#print(X); print(Y)
			for i in range(len(Z)):
				Z[i, :] = Z[i, :] / ((Y[i+1] - Y[i]))
				Z[:, i] = Z[:, i] / (4./3. * np.pi * (X[i+1]**3 - X[i]**3))
			print(Z[ Z > 0.07e7 ])
			x, y = np.unravel_index(np.argmax(Z), Z.shape)
			print( (x, y), Z[x, y], X[x], X[x+1], Y[y], Y[y+1])
		if masked:
			Z = np.ma.array(Z)
			Z = np.ma.masked_where(Z <= 0, Z)

			if log:
				Z = np.ma.log10(Z)

		self.don = np.copy(back_don)

		return X, Y, Z


	def Plot(self, num=None, fig=None, cmap=cm.jet, verbose=0, log=False, pfilter=lambda z: z, density=False, masked=False, AxsLog=True, ValMin=-2, dj=1.0):
		"""Trace les histogrammes.
		"""
		if isinstance(num, Subplot):
			self.axs = num
			if fig is None:
				raise ValueError("As you give an axis to plot, you must give a figure where plot the colorbar.")
			self.fig = fig
		else:
			self.fig, self.axs = plt.subplots(1, 1, num=num, squeeze=True)

		if AxsLog:
			if isinstance(self.nbbin, int):
				self.nb_point = self.nbbin
			self.nbbin = (
					10.**np.linspace(
							ValMin,
							np.log10( np.max(self.don[:,0]) ),
							self.nb_point
					),
					np.linspace(
						np.min(self.don[:,1]),
						np.max(self.don[:,1]),
						self.nb_point
					)
				)
			self.axs.set_xscale("log")
		elif not isinstance(self.nbbin, int):
			self.nbbin = self.nb_point

		X, Y, Z = self._calc(pfilter=pfilter, log=log, density=density, masked=masked)
		#print(Z.max(), Z.min())
		#print(Z[np.unravel_index(Z.argmax(), Z.shape)])
		#print(self.compt[np.unravel_index(Z.argmax(), Z.shape)])
		ind = np.unravel_index(Z.argmax(), Z.shape)
		#print((X[ind[0]], X[ind[0]+1]), (Y[ind[1]], Y[ind[1]+1]))


		#Axis = np.array( [np.min(X), np.max(X), np.min(Y), np.max(Y)] )
		#self.axs.axis(Axis)
		#self.log.debug(Axis)
		self.log.debug(Z[0:5])

		#self.axs.set_xscale('log')
		#Z /= dj
		cbf = self.axs.pcolor(X, Y, Z, cmap=cmap)
		divider = make_axes_locatable(self.axs)
		cax = divider.append_axes("right", size="5%", pad=0.05)

		self.fig.colorbar(cbf, cax=cax)

		#ratio = (Axis[1] - Axis[0]) / (Axis[3] - Axis[2])
		#self.log.debug(ratio)
		#self.axs.set_aspect(ratio, adjustable='box')
		return cbf

	def Get_Plot(self):
		return self.fig

	def Get_Axes(self):
		return self.axs
