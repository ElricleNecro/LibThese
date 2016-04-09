import  numpy as np
cimport numpy as np

cimport cython

cimport King as kb

def get_include():
	import os
	import subprocess as commands
	def pkgconfig(*packages, **kw):
		flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
		for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
			kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
		return kw
	return os.path.join( pkgconfig("king")["include_dirs"][0], 'king' )

cdef class KingModel:
	"""Create a King object accordingly to my studies.
	"""
	def __cinit__(self, double w0, double rc, double sv, double G = 6.67e-11):
		""" w0 : depth of the potential.
		rc : core radius.
		sv : velocities dispersion.
		G = 6.67e-11 : constant of gravitation.
		"""
		kb.King_SetG(G)
		self._obj = kb.King_New(w0, rc, sv)
		if self._obj.don is not NULL:
			raise MemoryError()

	@cython.boundscheck(False)
	cdef np.ndarray _get_data(self):

		cdef np.ndarray res = np.zeros([self._obj.lig, self._obj.col], dtype=np.float64)
		cdef i, j

		for i in range(0, self._obj.lig):
			for j in range(0, self._obj.col):
				res[i, j] = self._obj.don[i][j]
		return res

	property data:
		def __get__(self):
			if self._obj.don is not NULL:
				return self._get_data()

	property Mtot:
		def __get__(self):
			return self._obj.amas.Mtot

	property rho0:
		def __get__(self):
			return self._obj.amas.rho0

	property rmax:
		def __get__(self):
			return self._obj.amas.rmax

	property vmax:
		def __get__(self):
			return self._obj.amas.vmax

	property El:
		def __get__(self):
			return self._obj.amas.El

	property m:
		def __get__(self):
			return self._obj.amas.m

	property W0:
		def __get__(self):
			return self._obj.amas.W0

	property sigma2:
		def __get__(self):
			return self._obj.amas.sigma2

	property rc:
		def __get__(self):
			return self._obj.amas.rc

	#property N:
		#def __get__(self):
			#return self.N

	cpdef Solve(self):
		"""Solve the King model equation.
		"""
		kb.King_gud(&self._obj)

	cpdef SolveAll(self, int N):
		"""Resolve the King model equation and set all dimension accordingly to the parameters given at the class construction.
		N : number of particule (use to get the particule mass we need to end the transformation).
		"""
		kb.King_gud      ( &self._obj    )
		kb.King_CalcR    ( &self._obj    )
		kb.King_CalcRho  ( &self._obj    )
		kb.King_CalcMtot ( &self._obj    )
		self.N = N
		kb.King_SetM     ( &self._obj, N )
		kb.King_CalcSig2 ( &self._obj    )
		kb.King_CalcEl   ( &self._obj    )
		kb.King_CalcPot  ( &self._obj    )
		kb.King_CalcDPot ( &self._obj    )
		kb.King_CalcMu   ( &self._obj    )
		kb.King_CalcVMax ( &self._obj    )

	cpdef CalcR(self):
		kb.King_CalcR(&self._obj)

	cpdef CalcRho(self):
		kb.King_CalcRho(&self._obj)

	cpdef CalcMtot(self):
		kb.King_CalcMtot(&self._obj)

	cpdef SetM(self, int N):
		self.N = N
		kb.King_SetM(&self._obj, N)

	cpdef CalcSig2(self):
		kb.King_CalcSig2(&self._obj)

	cpdef CalcEl(self):
		kb.King_CalcEl(&self._obj)

	cpdef CalcPot(self):
		kb.King_CalcPot(&self._obj)

	cpdef CalcDPot(self):
		kb.King_CalcDPot(&self._obj)

	cpdef CalcMu(self):
		kb.King_CalcMu(&self._obj)

	cpdef CalcVMax(self):
		kb.King_CalcVMax(&self._obj)

	def __dealloc__(self):
		if self._obj.don is not NULL:
			kb.King_free(&self._obj)

DTYPE = np.float64
ctypedef np.float64_t DTYPE_T

#from cython.parallel import prange

@cython.boundscheck(False)
@cython.wraparound(False)
def CalcMtotForW0(double w0, np.ndarray[DTYPE_T, ndim=2] rc not None, np.ndarray[DTYPE_T, ndim=2] sigv not None):
	"""Useless, the numpy + scipy version is faster and better (more precise).
	"""
	#assert rc.dtype == DTYPE and sigv == DTYPE
	#assert rc.shape[0] == sigv.shape[0] and rc.shape[1] == sigv.shape[1]

	cdef unsigned int i, j
	cdef int nx = rc.shape[0]
	cdef int ny = rc.shape[1]
	cdef kb.King tmp
	cdef np.ndarray[DTYPE_T, ndim=2] h = np.zeros([nx, ny], dtype=DTYPE)

	for i in range(nx):
		for j in range(ny):
			tmp = kb.King_New(w0, rc[i, j], sigv[i, j])
			kb.King_gud(&tmp)
			kb.King_CalcR(&tmp)
			kb.King_CalcRho(&tmp)
			kb.King_CalcMtot(&tmp)
			h[i, j] = tmp.amas.Mtot
			kb.King_free(&tmp)

	return h

