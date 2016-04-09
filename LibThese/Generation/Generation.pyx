cimport cython
cimport cython.parallel as cp

cimport libc.math as m

from libc.stdlib cimport malloc, free

cimport Generation as gb

import  King
cimport King

import numpy as np
cimport numpy as np

import  LibThese.Gadget.Types as Types
cimport LibThese.Gadget.Types as Types

import  LibThese.Tree.Tree as Tree
cimport LibThese.Tree.Tree as Tree

cdef class GKing(King.KingModel):
	cdef double r_grand
	cdef Types.Particules part

	cpdef long Generate(self, long seed, int id=0, int Type=2):
		cdef unsigned int i

		if self.N == 0:
			raise ValueError("You should call setM or SolveAll before calling this method.")

		part = <Types._particule_data_d *>malloc( self.N * sizeof(Types._particule_data_d))

		gb.King_Generate(self._obj, self.N, &self.r_grand, part, &seed)

		self.part = Types.FromPointer(part, self.N)

		for i in range(self.N):
			self.part.ptr_data[i].m = self._obj.amas.m
			self.part.ptr_data[i].Id = id + i
			self.part.ptr_data[i].Type = Type

		return seed

	cdef Types.Particules _get_part(self):
		return self.part

	property Part:
		def __get__(self):
			if self.part.ptr_data is not NULL:
				return self._get_part()

cdef class pObject:
	"""Classe de base permettant de générer n'importe quel type de profile.
	Elle fournit un constructeur récupérant des informations utiles comme le type gadget
	des particules associées, leurs Id, leurs masses (unique), et le nombre de particules.

	Elle s'occupe d'allouer le tableau de particules dans le membre Part de la classe.

	En bonus, elle fournit 2 méthodes permettant de calculer le rapport du Viriel de
	l'objet généré et un méthode permettant, en jouant sur les vitesses, de ramener ce
	rapport à une valeur choisie.

	Optionnellement, il exite une méthode écrivant les particules dans un fichier texte, mais
	cette méthode peut disparaître à tout moment.
	"""
	cdef Types.Particules part
	cdef readonly int N
	cdef readonly double m

	@cython.boundscheck(False)
	#def __cinit__(self, int N, double m=1.0, int id=0, int Type=1):
	def __init__(self, int N, double m=1.0, int id=1, int Type=1):
		"""Constructeur :
			N -> Nombre de particule,
			m = 1.0 -> masse d'une particule,
			id = 0 -> identité à partir de laquelle compter les Id des particules,
			Type = 1 -> type gadget ([0, 5]) à donner aux particules.
		"""
		cdef unsigned int i
		self.N    = N
		self.m    = m
		if self.N <= 0:
			raise ValueError("N cannot be negative or null.")
		part = <Types._particule_data_d *>malloc( self.N * sizeof(Types._particule_data_d))
		if part is NULL:
			raise MemoryError()
		self.part = Types.FromPointer(part, self.N)

		for i in range(self.N):
			self.part.ptr_data[i].Id   = id + i
			self.part.ptr_data[i].m    = m
			self.part.ptr_data[i].Type = Type

	#def __dealloc__(self):
		#if self.part is not NULL:
			#free(self.part)
			#self.part = NULL

	cdef Types.Particules _get_part(self):
		return self.part

	cdef _set_part(self, Types.Particules part):
		self.part = part

	property Part:
		def __get__(self):
			if self.part.ptr_data is not NULL:
				return self._get_part()
		def __set__(self, part):
			self._set_part(part)

	@cython.boundscheck(False)
	cpdef GetViriel(self, int NbMin=15, double accept=0.5, double soft=0.0, G=None):
		cdef double taille = 0., r = 0.
		cdef unsigned int i, j

		for i in range(self.N):
			r = 0.
			for j in range(3):
				r += self.part.ptr_data[i].Pos[j]*self.part.ptr_data[i].Pos[j]
			if r > taille:
				taille = r

		taille = 4.0*m.sqrt(taille)

		if G is not None:
			Tree.SetG(G)

		tree = Tree.OctTree(self.part, NbMin, Types.FromPyData([[0., 0., 0., 0., 0., 0.]]), taille)

		return tree._get_viriel(accept, soft)

	@cython.boundscheck(False)
	cpdef SetViriel(self, double Vir, int NbMin=15, double accept=0.5, double soft=0.0, G=None):
		cdef double OldVir = self.GetViriel(NbMin, accept, soft, G)
		cdef double fact = 0. #Vir /
		cdef unsigned int i, j

		if OldVir == 0.:
			self.SaveText("/tmp/debug.ci_py.log")
			raise ValueError("Get Null Viriel! Data write in /tmp/debug.ci_py.log.")
		fact = Vir / OldVir

		for i in range(self.N):
			for j in range(3):
				self.part.ptr_data[i].Vit[j] *= m.sqrt(fact)

	@cython.boundscheck(False)
	cpdef SaveText(self, filename):
		cdef unsigned int i
		with open(filename, "w") as f:
			for i in range(self.N):
				f.writelines("%g %g %g %g %g %g %g %d\n"%(self.part.ptr_data[i].Pos[0], self.part.ptr_data[i].Pos[1], self.part.ptr_data[i].Pos[2], self.part.ptr_data[i].Vit[0], self.part.ptr_data[i].Vit[1], self.part.ptr_data[i].Vit[2], self.part.ptr_data[i].m, self.part.ptr_data[i].Id))

	@cython.boundscheck(False)
	cpdef gauss(self, double sig, long seed, pos=False, int Id_from=0):
		cdef double **res
		cdef unsigned int i, j

		res = gb.gauss(sig, self.N, &seed)

		if pos:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Pos[j] = res[i][j]
		else:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Vit[j] = res[i][j]

		free(res[0])
		free(res)

		return seed

	@cython.boundscheck(False)
	cpdef gauss_limited(self, double sig, double broke, long seed, pos=False):
		cdef double **res
		cdef unsigned int i, j

		res = gb.gauss_limit(sig, broke, self.N, &seed)

		if pos:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Pos[j] = res[i][j]
		else:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Vit[j] = res[i][j]

		free(res[0])
		free(res)

		return seed

	cpdef Fujiwara1983(self, double r_max, double v_max, double sig_v, long seed):
		cdef double r_grand

		gb.Fuji_Generate(self.N, r_max, v_max, sig_v, 4.*self.N*self.m/(4.0*np.pi*r_max**3.), self.part.ptr_data, &r_grand, &seed)

		return seed, r_grand

#void Fuji_Generate(const int Nb_part_t1, const double r_max, const double v_max, const double sig_v, const double rho_0, Particule_d king, double *r_grand, long *seed)


cdef class SmoothedSphere(pObject):
	@cython.boundscheck(False)
	cpdef homo(self, double r_m, double smoothing, long seed, pos=True, int Id_from=0):
		"""Generate a homogeneous sphere smoothed with an error function.
		r_m : Size of the sphere,
		smoothing: smoothing radius,
		seed: seed value to use.
		"""
		cdef double **res
		cdef unsigned int i, j

		res = gb.sphere_smooth(r_m, smoothing, self.N, &seed)

		if pos:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Pos[j] = res[i][j]
		else:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Vit[j] = res[i][j]

		free(res[0])
		free(res)

		return seed

	@cython.boundscheck(False)
	cpdef homo_parallel(self, double r_m, double smoothing, long seed, bint pos=True, int nbthread=2):
		cdef double **res
		cdef unsigned int i, j
		#cdef int *local_N, id
		#cdef long local_seed, *tab_seed

		#tab_seed = <long*>malloc(sizeof(long) * nbthread)

		#for i in range(nbthread):
			#tab_seed[i] = gb.ran2(&seed)

		#with nogil:
			#id = cp.threadid()
			#local_seed = tab_seed[id]
			#local_N = <int*>malloc(sizeof(int) * 1)

			#local_N = self.N // nbthread
			#if self.N % nbthread != 0 and id < self.N % nbthread:
				#local_N += 1
		res = gb.sphere_smooth_parallel(r_m, smoothing, self.N, nbthread, &seed)

		if pos:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Pos[j] = res[i][j]
		else:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Vit[j] = res[i][j]
		#with nogil, cp.parallel(num_threads=nbthread):
			#id = cp.threadid()
			#local_seed = tab_seed[id]
			#local_N = <int*>malloc(sizeof(int) * 1)

			#local_N = self.N // nbthread
			#if self.N % nbthread != 0 and id < self.N % nbthread:
				#local_N += 1
			#res = gb.sphere_smooth(r_m, smoothing, local_N, &seed)

		free(res[0])
		free(res)

		return seed

cdef class Sphere(pObject):
	@cython.boundscheck(False)
	cpdef homo(self, double r_m, long seed, pos=True, int Id_from=0):
		cdef double **res
		cdef unsigned int i, j

		res = gb.sphere_homo(r_m, self.N, &seed)

		if pos:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Pos[j] = res[i][j]
		else:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Vit[j] = res[i][j]

		free(res[0])
		free(res)

		return seed

cdef class Cube(pObject):
	@cython.boundscheck(False)
	cpdef homo(self, double r_m, long seed, pos=True, int Id_from=0):
		"""
		"""
		cdef double **res
		cdef unsigned int i, j

		res = gb.carree_homo(r_m, self.N, &seed)

		if pos:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Pos[j] = res[i][j]
		else:
			for i in range(self.N):
				for j in range(3):
					self.part.ptr_data[i].Vit[j] = res[i][j]

		free(res[0])
		free(res)

		return seed


#, pos=False, Type=0, Id=True, m=0.

	#ret = Array2DWrapper()
	#size[0] = Nb
	#size[1] = 3
	#ret.set_data(size, res)

	#return ret

	#part = <gb._particule_data_d *>malloc( self.N * sizeof(gb._particule_data_d))

