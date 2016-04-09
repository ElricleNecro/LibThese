#from InitialCond.Types cimport _particule_data_d, Particule_d
cimport LibThese.Gadget.Types as Types

cdef extern from "tree.h":
	cdef struct _tnoeud:
		int    N
		int    level
		double x, y, z
		double cote
		Types.Particule_d first
		Types._particule_data_d cm
		double CM
		_tnoeud* parent
		_tnoeud* frere
		_tnoeud* fils

	ctypedef _tnoeud* TNoeud

	void Tree_SetG(double nG) nogil
	double Tree_GetG() nogil
	TNoeud Create_Tree(Types.Particule_d posvits, const int NbParticule_d, const int NbMin, const Types._particule_data_d center, const double taille) nogil
	double Tree_CalcPot(TNoeud root, const Types.Particule_d part, const double accept, const double soft) nogil
	void Tree_Free(TNoeud root) nogil

cpdef SetG(double G)
cpdef double GetG()
cpdef CreateOctTree(Types.Particules part, int NbMin, Types.Particules center, double taille)

cdef class OctTree:
	cdef TNoeud root
	cdef int NbMin, N

	cdef set_data(self, Types.Particule_d posvits, int Nb, int NbMin, Types._particule_data_d center, double taille)
	cpdef double CalcPotential(self, double accept, double soft)
	cpdef double _get_viriel(self, double accept=?, double soft=?)

