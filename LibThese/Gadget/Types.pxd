cdef extern from "IOGadget/types.h":
    cdef struct _particule_data_f:
        float Pos[3]
        float Vit[3]
        float m
        float Pot
        float Acc[3]
        float dAdt
        float ts
        float Rho
        float U
        float Ne
        int Id
        int Type
    ctypedef _particule_data_f* Particule_f

    cdef struct _particule_data_d:
        double Pos[3]
        double Vit[3]
        double m
        double Pot
        double Acc[3]
        double dAdt
        double ts
        double Rho
        double U
        double Ne
        int Id
        int Type
    ctypedef _particule_data_d* Particule_d

cdef extern from "types.h":
    void Echange(Particule_d a, Particule_d b)
    Particule_d Concat(const Particule_d a, const int Na, const Particule_d b, const int Nb)
    void sort_by_id(Particule_d tab, const int N)
    void sort_by_type(Particule_d tab, const int N)

cdef Particules FromPointer(Particule_d p, int N)
cdef Particules Single(_particule_data_d p)
cpdef FromPyData(lst, colType=?, colm=?, colId=?)

cdef class Particules:
    cdef Particule_d ptr_data
    cdef readonly int N
    cdef bint b_potential, b_acceleration, b_rate_entropy, b_timestep
    cdef set_data(self, Particule_d p, int N)
    cpdef _translate(self, double x, double y, double z)
    cpdef _velocity(self, double x, double y, double z)
    cpdef Particules Add(self, Particules b)
    cpdef SortById(self)
    cpdef SortByType(self)
    cpdef Release(self)

