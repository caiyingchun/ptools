from cython.operator cimport dereference as deref
from libcpp.string cimport string


cdef extern from "surface.h" namespace "PTools":
    cdef cppclass CppSurface "PTools::Surface":
        CppSurface(int, int , string ) 
        CppRigidbody surfpoint(CppRigidbody & , double)
        void surfpointParams(int, double)
        CppRigidbody outergrid(CppRigidbody &, CppRigidbody & , double)
        CppRigidbody remove_closest(CppRigidbody & , double)
        void readsolvparam(string)


cdef class Surface:

    cdef CppSurface * thisptr

    def __cinit__(self, int nphi, int ncosth, bytes b ):
        cdef char* c_filename = b
        cdef string * cpp_filename = new string(c_filename)
        self.thisptr = new CppSurface(nphi, ncosth, deref(cpp_filename) )
        del cpp_filename

    def __dealloc__(self):
        if self.thisptr:
           del self.thisptr

    def surfpoint(self, Rigidbody rigid, double srad):
        cdef CppRigidbody r = self.thisptr.surfpoint(deref(rigid.thisptr), srad)
        ret = Rigidbody()
        del ret.thisptr
        ret.thisptr = new CppRigidbody(r)
        return ret

    def surfpointParams(self, int max, double shift):
        self.thisptr.surfpointParams(max, shift)

    def outergrid(self, Rigidbody rigid1, Rigidbody rigid2, double srad):
        cdef CppRigidbody r = self.thisptr.outergrid(deref(rigid1.thisptr), deref(rigid2.thisptr), srad)
        ret = Rigidbody()
        del ret.thisptr
        ret.thisptr = new CppRigidbody(r)
        return ret

    def remove_closest(self, Rigidbody rigid1, double srad):
        cdef CppRigidbody r = self.thisptr.remove_closest(deref(rigid1.thisptr), srad)
        ret = Rigidbody()
        del ret.thisptr
        ret.thisptr = new CppRigidbody(r)
        return ret

    def readsolvparam(self, bytes file):
       cdef char* c_filename = file
       cdef string * cpp_filename = new string(c_filename)
       self.thisptr.readsolvparam(deref(cpp_filename) )
       del cpp_filename
