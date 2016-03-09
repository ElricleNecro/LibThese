cimport InitialCond.Types as Types

cdef extern from "IOGadget/gadget.h":
	cdef struct io_header:
		int		npart[6]
		double		mass[6]
		double		time
		double		redshift
		int		flag_sfr
		int		flag_feedback
		unsigned int	npartTotal[6]
		int		flag_cooling
		int		num_files
		double		BoxSize
		double		Omega0
		double		OmegaLambda
		double		HubbleParam
		int		flag_stellarage
		int		flag_metals
		unsigned int	npartTotalHighWord[6]
		int		flag_entropy_instead_u
		char		fill[60]
	ctypedef io_header Header

cdef extern from "IOGadget/gadget_read.h":
	Types.Particule_f Float_Gadget_Read_format1(const char *fname, Header *header, int files, int b_potential, int b_acceleration, int b_rate_entropy, int b_timestep)
	Types.Particule_f Float_Gadget_Read_format2(const char *fname, Header *header, int files, int b_potential, int b_acceleration, int b_rate_entropy, int b_timestep)

	Types.Particule_d Double_Gadget_Read_format1(const char *fname, Header *header, int files, int b_potential, int b_acceleration, int b_rate_entropy, int b_timestep)
	Types.Particule_d Double_Gadget_Read_format2(const char *fname, Header *header, int files, int b_potential, int b_acceleration, int b_rate_entropy, int b_timestep)

cdef extern from "IOGadget/gadget_write.h":
	int Float_Gadget_Write_format1(const char *name, const Header header, const Types.Particule_f part)
	int Float_Gadget_Write_format2(const char *name, const Header header, const Types.Particule_f part)

	int Double_Gadget_Write_format1(const char *name, const Header header, const Types.Particule_d part)
	int Double_Gadget_Write_format2(const char *name, const Header header, const Types.Particule_d part)

#cdef extern from "gadget.h":
	#Types.Particule Gadget_Read(const char *name, Header *header, int files, int b_potential, int b_acceleration, int b_rate_entropy, int b_timestep)
	#int Gadget_Write(const char *name, const Header header, const Types.Particule part)

cdef class Gadget:
	cdef Types.Particules part
	cdef Header header
	cdef filename
	cdef Write
	cdef Read
	#cpdef int OldWrite(self)
	#cpdef OldRead(self, int num_files, bint bpot=?, bint bacc=?, bint bdadt=?, bint bdt=?)
	cpdef int _write_format1(self)
	cpdef int _write_format2(self)
	cpdef _read_format1(self, int num_files, bint bpot=?, bint bacc=?, bint bdadt=?, bint bdt=?)
	cpdef _read_format2(self, int num_files, bint bpot=?, bint bacc=?, bint bdadt=?, bint bdt=?)

