cdef extern from "Stacking.h" namespace "PTools":
    cdef cppclass CppStacking "PTools::Stacking":
        CppStacking()

cdef class Stacking:
    cdef CppStacking * thisptr

    def __cinit__(self):
        self.thisptr = new CppStacking()

    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr

