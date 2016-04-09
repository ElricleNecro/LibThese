cimport Tree as t

cimport LibThese.Gadget.Types as Types
import  LibThese.Gadget.Types as Types

cpdef SetG(double G):
	t.Tree_SetG(G)

cpdef double GetG():
	return t.Tree_GetG()

cpdef CreateOctTree(Types.Particules part, int NbMin, Types.Particules center, double taille):
	return OctTree(part, NbMin, center, taille)

cdef class OctTree:
	def __cinit__(self, Types.Particules posvits, int NbMin, Types.Particules center, double taille):
		self.set_data(posvits.ptr_data, posvits.N, NbMin, center.ptr_data[0], taille)

	cdef set_data(self, Types.Particule_d posvits, int Nb, int NbMin, Types._particule_data_d center, double taille):
		self.NbMin = NbMin
		self.N = Nb
		self.root = t.Create_Tree(posvits, Nb, NbMin, center, taille)
		if self.root is NULL:
			raise MemoryError

	def __dealloc__(self):
		if self.root is not NULL:
			t.Tree_Free(self.root)
			self.root = NULL

	cpdef double CalcPotential(self, double accept, double soft):
		cdef unsigned int i
		cdef double pot = 0.

		for i in range(self.root.N):
			pot += self.root.first[i].m * t.Tree_CalcPot(self.root, &self.root.first[i], accept, soft)

		return pot/2.0

	def Get_Viriel(self, accept=0.5, soft=0.0):
		return self._get_viriel(accept, soft)

	cpdef double _get_viriel(self, double accept = 0.5, double soft = 0.0):
		cdef double pot = 0.
		cdef double v   = 0.
		cdef unsigned int i

		for i in range(self.root.N):
			pot += self.root[0].first[i].m * t.Tree_CalcPot(self.root, &self.root[0].first[i], accept, soft)
			v   += 0.5 * self.root[0].first[i].m * ( self.root[0].first[i].Vit[0]*self.root[0].first[i].Vit[0] + self.root[0].first[i].Vit[1]*self.root[0].first[i].Vit[1] + self.root[0].first[i].Vit[2]*self.root[0].first[i].Vit[2] )

		pot /= 2.0

		return 2. * v / pot

