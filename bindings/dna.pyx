from cython.operator cimport dereference as deref
from libcpp.string cimport string

cdef extern from "DNA.h" namespace "PTools":
    cdef cppclass CppDNA "PTools::DNA":
        CppDNA()
        CppDNA(CppDNA&)
        CppDNA(string&, string&, CppMovement&)
        CppDNA(string&, string&)  #with default value for third parameter
        CppDNA SubDNA(int, int)
        CppBasePair operator[](int)
        unsigned int Size()
        void Add(CppBasePair, const CppMovement &)
        void Add(CppBasePair)
        void Add(CppDNA, const CppMovement &)
        void Add(CppDNA)
        void ChangeType(int, string, string)
        void ApplyLocal(const CppMovement&, int)
        void ChangeRepresentation(string);


cdef class DNA:
    cdef CppDNA* thisptr

    def __cinit__(self, arg1=None, arg2=None, arg3=None):
        cdef Movement mov
        if arg1 is None:
            self.thisptr = new CppDNA()
        elif arg2 is not None:
            if arg3 is not None:
                mov = <Movement?> arg3
                self.thisptr = new CppDNA(<string>arg1,<string> arg2, deref(mov.thisptr))
            else:
                self.thisptr = new CppDNA(<string> arg1, <string> arg2)
        elif isinstance(arg1, DNA):
            dna = <DNA?> arg1
            self.thisptr = new CppDNA(deref(dna.thisptr))
        else:
            raise RuntimeError("invalid parameters during DNA creation")

    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr
            self.thisptr = <CppDNA*> 0

    def __len__(self):
        return self.Size()

    def __getitem__(self, unsigned int i):
        if i>=self.thisptr.Size():
            raise IndexError
        bp = BasePair()
        if bp.thisptr:
            del bp.thisptr

        bp.thisptr = new CppBasePair(deref(self.thisptr)[i])
        return bp

    def Size(self):
        return self.thisptr.Size()

    def SubDNA(self, int start, int end):
        ret = DNA()
        if ret.thisptr:
            del ret.thisptr
        cdef CppDNA cdna = self.thisptr.SubDNA(start, end)
        ret.thisptr = new CppDNA(cdna)
        return ret

    def Add(self, bp_or_dna, mov=None):
        if isinstance(bp_or_dna, DNA):
            self._add_dna(bp_or_dna, mov)
        else:
            self._add_bp(bp_or_dna, mov)

    def _add_bp(self, BasePair bp, Movement mov=None):
        if mov == None:
            self.thisptr.Add(deref(bp.thisptr))
        else:
            self.thisptr.Add(deref(bp.thisptr), deref(mov.thisptr))

    def _add_dna(self, DNA dna, Movement mov=None):
        if mov == None:
            self.thisptr.Add(deref(dna.thisptr))
        else:
            self.thisptr.Add(deref(dna.thisptr), deref(mov.thisptr))
    
    def ChangeType(self, int pos, bytes basetype, bytes filename):
        cdef const char * c_basetype = basetype
        cdef const char * c_filename = filename
        self.thisptr.ChangeType(pos, str(c_basetype), str(c_filename))

    def ApplyLocal(self, Movement mov, int posMov):
        self.thisptr.ApplyLocal(deref(mov.thisptr), posMov)

    def ChangeRepresentation(self, bytes rep):
        self.thisptr.ChangeRepresentation(rep)
