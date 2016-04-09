import numpy as np
cimport numpy as np

cdef extern from "king/mod.h":
	cdef struct phys_king:
		double m
		double El
		double rc
		double sigma2
		double rho0
		double W0
		double rho_ori
		double eps
		double G
		double rmax
		double vmax
		double Mtot
	ctypedef phys_king Phys_King

cdef extern from "king/king.h":
	cdef struct king:
		Phys_King amas
		double **don
		double frac
		int lig
		int col
	ctypedef king King

	double King_get_PhysVal(const King *obj, int i, int j) nogil
	void King_SetG(const double G_new) nogil
	King King_New(const double W0, const double rc, const double sig_v) nogil
	double King_Temp(const King *Amas, int i) nogil
	double King_TempMoy(const King *Amas) nogil
	double King_mu(const King *Amas, const int a, const int b) nogil
	double King_Ec(const King *Amas, const int a, const int b) nogil
	double King_Ep(const King *Amas, const int a, const int b) nogil
	void King_gbs(King *obj, const int NbPart) nogil
	#void King_gbs_cb(King *obj, int *NbPart, gbs_cb f , void *data)
	void King_ugbs(King *obj) nogil
	double King_distrib(const King *obj, double E) nogil
	double King_don_pot(const King *obj, double r) nogil
	#int read_utile(King *Amas, const char const *str)
	void King_gud(King *obj) nogil
	void King_CalcRho(King *obj) nogil
	void King_CalcR(King *obj) nogil
	void King_CalcMtot(King *obj) nogil
	void King_CalcSig2(King *obj) nogil
	void King_CalcEl(King *obj) nogil
	void King_CalcMu(King *obj) nogil
	void King_CalcDPot(King *obj) nogil
	void King_CalcPot(King *obj) nogil
	void King_CalcVMax(King *obj) nogil
	void King_CalcRMax(King *obj) nogil
	void King_SetM(King *obj, const int NbPart) nogil
	void King_free(King *obj) nogil

cdef class KingModel:
	cdef King _obj
	cdef readonly int N

	cdef np.ndarray _get_data(self)
	cpdef Solve(self)
	cpdef SolveAll(self, int N)
	cpdef CalcR(self)
	cpdef CalcRho(self)
	cpdef CalcMtot(self)
	cpdef SetM(self, int N)
	cpdef CalcSig2(self)
	cpdef CalcEl(self)
	cpdef CalcPot(self)
	cpdef CalcDPot(self)
	cpdef CalcMu(self)
	cpdef CalcVMax(self)

