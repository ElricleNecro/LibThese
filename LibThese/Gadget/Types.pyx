from libc.stdlib cimport malloc, free
#from Types cimport _particule_data, Particule

cimport cython
cimport Types

cimport numpy as np
import numpy as np

cdef class Array2DWrapper:
    """Get from : http://gael-varoquaux.info/blog/?p=157
    """
    cdef void* data_ptr
    cdef int size[2]

    cdef set_data(self, int size[2], void* data_ptr):
        """ Set the data of the array
        This cannot be done in the constructor as it must recieve C-level
        arguments.

        Parameters:
        -----------
        size: int
        Length of the array.
        data_ptr: void*
        Pointer to the data
        """
        self.data_ptr = data_ptr
        self.size[0] = size[0]
        self.size[1] = size[1]

cdef class Array1DWrapper:
    """Get from : http://gael-varoquaux.info/blog/?p=157
    """
    cdef void* data_ptr
    cdef int size

    cdef set_data(self, int size, void* data_ptr):
        """ Set the data of the array
        This cannot be done in the constructor as it must recieve C-level
        arguments.

        Parameters:
        -----------
        size: int
        Length of the array.
        data_ptr: void*
        Pointer to the data
        """
        self.data_ptr = data_ptr
        self.size = size

    #def __array__(self):
        #""" Here we use the __array__ method, that is called when numpy
        #tries to get an array from the object."""
        #cdef np.npy_intp shape[2]
        #shape[0] = <np.npy_intp> self.size
        ## Create a 1D array, of length 'size'
        #ndarray = np.PyArray_SimpleNewFromData(2, shape,

        #return ndarray

#-----------------------------------------------------------------------------------------------------------
# Classes et fonctions travaillant autour du type _particule_data :
#-----------------------------------------------------------------------------------------------------------
cdef Particule_Data _PD_FromValue(Types._particule_data_d val):
    cdef Particule_Data res
    # Allocation de la particule :
    cdef Types.Particule_d ptr = <Types._particule_data_d *>malloc(sizeof(Types._particule_data_d))

    # copie de la valeur :
    ptr[0] = val

    # On crée la classe permettant d'accéder aux champs de la structure :
    res = Particule_Data()
    # On la fait pointer au bon endroit :
    res.ptr_data = ptr
    # La structure n'a pas été initialisé à partir d'un pointeur :
    res.from_ptr = False

    return res

cdef Particule_Data _PD_FromPointer( Types.Particule_d ptr):
    cdef Particule_Data res

    # On crée la classe Wrapper autour de la structure _particule_data :
    res = Particule_Data()
    # On la fait pointer au bon endroit :
    res.ptr_data = ptr
    # cette structure vient d'un pointeur :
    res.from_ptr = True

    return res

# Classe permettant de jouer en python avec les structures _particule_data :
cdef class Particule_Data:
    cdef _particule_data_d* ptr_data
    cdef bint from_ptr

    def __dealloc__(self):
        # si cette structure n'a pas été initialisé à partir d'un pointeur, on libère la mémoire :
        if not self.from_ptr:
            free(self.ptr_data)

    property Pos:
        def __get__(self):
            return [ self.ptr_data[0].Pos[0], self.ptr_data[0].Acc[1], self.ptr_data[0].Acc[2] ]
        def __set__(self, val):
            self.ptr_data[0].Pos[0], self.ptr_data[0].Acc[1], self.ptr_data[0].Acc[2] = val[0], val[1], val[2]

    property Vit:
        def __get__(self):
            return [ self.ptr_data[0].Vit[0], self.ptr_data[0].Acc[1], self.ptr_data[0].Acc[2] ]
        def __set__(self, val):
            self.ptr_data[0].Vit[0], self.ptr_data[0].Acc[1], self.ptr_data[0].Acc[2] = val[0], val[1], val[2]

    property Acc:
        def __get__(self):
            return [ self.ptr_data[0].Acc[0], self.ptr_data[0].Acc[1], self.ptr_data[0].Acc[2] ]
        def __set__(self, val):
            self.ptr_data[0].Acc[0], self.ptr_data[0].Acc[1], self.ptr_data[0].Acc[2] = val[0], val[1], val[2]

    property Id:
        def __get__(self):
            return self.ptr_data[0].Id
        def __set__(self, val):
            self.ptr_data[0].Id = val

    property Mass:
        def __get__(self):
            return self.ptr_data[0].m
        def __set__(self, val):
            self.ptr_data[0].m = val

    property Type:
        def  __get__(self):
            return self.ptr_data[0].Type
        def __set__(self, val):
            self.ptr_data[0].Type = val

    property ts:
        def  __get__(self):
            return self.ptr_data[0].ts
        def __set__(self, val):
            self.ptr_data[0].ts = val

    property Pot:
        def  __get__(self):
            return self.ptr_data[0].Pot
        def __set__(self, val):
            self.ptr_data[0].Pot = val

    property dAdt:
        def  __get__(self):
            return self.ptr_data[0].dAdt
        def __set__(self, val):
            self.ptr_data[0].dAdt = val

    property Rho:
        def  __get__(self):
            return self.ptr_data[0].Rho
        def __set__(self, val):
            self.ptr_data[0].Rho = val

    property U:
        def  __get__(self):
            return self.ptr_data[0].U
        def __set__(self, val):
            self.ptr_data[0].U = val

    property Ne:
        def  __get__(self):
            return self.ptr_data[0].Ne
        def __set__(self, val):
            self.ptr_data[0].Ne = val

    # Quelques méthodes statique permettant d'initialiser la classe :
    #FromPointer = staticmethod(_PD_FromPointer)
    #FromValue   = staticmethod(_PD_FromValue)

#-----------------------------------------------------------------------------------------------------------
# Classes et fonctions travaillant autour du type Particules :
#-----------------------------------------------------------------------------------------------------------
@cython.wraparound(False)
@cython.boundscheck(False)
cdef Particules FromPointer(Types.Particule_d p, int N):
    tmp = Particules()

    tmp.set_data(p, N)

    return tmp

@cython.wraparound(False)
@cython.boundscheck(False)
cdef Particules Single(Types._particule_data_d p):
    cdef Types.Particule_d tmp = NULL
    res = Particules()

    tmp = <Types._particule_data_d *>malloc( sizeof(Types._particule_data_d))
    if tmp is NULL:
        raise MemoryError()

    tmp[0] = p

    res.set_data(tmp, 1)

    return res

@cython.wraparound(False)
@cython.boundscheck(False)
cpdef FromPyData(lst, colType=None, colm=None, colId=None):
    cdef Types.Particule_d tmp = NULL

    tmp = <Types._particule_data_d *>malloc(len(lst)* sizeof(Types._particule_data_d))
    if tmp is NULL:
        raise MemoryError()

    for i, a in enumerate(lst):
        for j, b in enumerate(a):
            if j < 3:
                tmp[i].Pos[j] = float(b)
            elif j < 6:
                tmp[i].Vit[j-3] = float(b)
            elif colType is not None and j == colType:
                tmp[i].Type = int(b)
            elif colm is not None and j == colm:
                tmp[i].m = float(b)
            if colId is not None and colId == j:
                tmp[i].Id = int(b)
            else:
                tmp[i].Id = i

    res = Particules()
    res.set_data(tmp, len(lst))

    return res

# Prototype d'itérateur pour la classe Particules :
cdef class Particules_iterator:
    def __next__(self):
        if self.i >= self.N:
            raise StopIteration
        self.i += 1
        return Particule_Data.FromPointer()

cdef class Particules:
    cdef set_data(self, Particule_d p, int N):
        self.N        = N
        self.ptr_data = p

    def __dealloc__(self):
        if self.ptr_data is not NULL:
            free(self.ptr_data)
            self.ptr_data = NULL

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef Types.Particules Add(self, Types.Particules p):
        res = FromPointer( Types.Concat(self.ptr_data, self.N, p.ptr_data, p.N), self.N + p.N )
        if res.ptr_data is NULL:
            raise MemoryError
        return res

    def Translate(self, to_move):
        if len(to_move) != 3:
            raise ValueError("to_move must be of Length 3.")

        self._translate(to_move[0], to_move[1], to_move[2])

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef _translate(self, double x, double y, double z):
        cdef unsigned int i
        for i in range(self.N):
            self.ptr_data[i].Pos[0] += x
            self.ptr_data[i].Pos[1] += y
            self.ptr_data[i].Pos[2] += z

    def AddVelocity(self, to_move):
        if len(to_move) != 3:
            raise ValueError("to_move must be of Length 3.")

        self._velocity(to_move[0], to_move[1], to_move[2])

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef Release(self):
        free(self.ptr_data)
        self.ptr_data = NULL

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef _velocity(self, double x, double y, double z):
        cdef unsigned int i
        for i in range(self.N):
            self.ptr_data[i].Vit[0] += x
            self.ptr_data[i].Vit[1] += y
            self.ptr_data[i].Vit[2] += z

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef SortById(self):
        sort_by_id(self.ptr_data, self.N)

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cpdef SortByType(self):
        sort_by_type(self.ptr_data, self.N)

    def __getitem__(self, key):
        if isinstance(key, slice) or key < 0 or key >= self.N:
            raise IndexError("Index not supported!")
        return _PD_FromPointer(&self.ptr_data[key])
        #return _PD_FromValue(self.ptr_data[key])

    def __add__(self, p):
        return self.Add(p)

    property Velocities:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i, j
            cdef list res, tmp

            res = list()
            for i in range(self.N):
                tmp = list()
                for j in range(3):
                    tmp.append(self.ptr_data[i].Vit[j])
                res.append(tmp)

            return res

    property NumpyVelocities:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i, j
            #cdef list res, tmp
            cdef np.ndarray res = np.zeros((self.N, 3))

            for i in range(self.N):
                for j in range(3):
                    res[i,j] = self.ptr_data[i].Vit[j]

            return res

    property Positions:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i, j
            cdef list res, tmp

            res = list()
            for i in range(self.N):
                tmp = list()
                for j in range(3):
                    tmp.append(self.ptr_data[i].Pos[j])
                res.append(tmp)

            return res

    property NumpyPositions:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i, j
            #cdef list res, tmp
            cdef np.ndarray res = np.zeros((self.N, 3))

            for i in range(self.N):
                for j in range(3):
                    res[i,j] = self.ptr_data[i].Pos[j]

            return res

    property Identities:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i
            cdef list res

            res = list()
            for i in range(self.N):
                res.append(self.ptr_data[i].Id)

            return res

    property NumpyIdentities:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i
            cdef np.ndarray res = np.zeros(self.N)

            for i in range(self.N):
                res[i] = self.ptr_data[i].Id

            return res

    property TimeStep:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i
            cdef list res

            res = list()
            for i in range(self.N):
                res.append(self.ptr_data[i].ts)

            return res

    property NumpyTimeStep:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i
            cdef np.ndarray res = np.zeros(self.N)

            for i in range(self.N):
                res[i] = self.ptr_data[i].ts

            return res

    property Potentiel:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i
            cdef list res

            res = list()
            for i in range(self.N):
                res.append(self.ptr_data[i].Pot)

            return res

    property NumpyPotentiel:
        @cython.boundscheck(False)
        def __get__(self):
            cdef unsigned int i
            cdef np.ndarray res = np.zeros(self.N)

            for i in range(self.N):
                res[i] = self.ptr_data[i].Pot

            return res

    #property Identities:
        #@cython.boundscheck(False)
        #def __get__(self):
            #cdef unsigned int i, j
            #cdef list res

            #res = list()
            #for i in range(self.N):
                #res.append(self.ptr_data[i].ts)

            #return res

    def __repr__(self):
        ret = "<Particules Object %x"%id(self)
        if self.N > 0 or self.ptr_data is not NULL:
            ret += " from id=%d"%self.ptr_data[0].Id + " to %d>"%self.ptr_data[self.N-1].Id
        else:
            ret += " uninitialized>"
        return ret

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return self.N

