from cython.operator cimport dereference as deref
from libcpp.string cimport string


cdef extern from "scorpionforcefield.h" namespace "PTools":
    cdef cppclass CppScorpionForceField "PTools::ScorpionForceField":
       CppScorpionForceField(string&, double)
       void AddLigand(CppAttractRigidbody&)
       double Function(vector[double]&)
       double getVdw()
       double getCoulomb()
       double nonbon8(CppAttractRigidbody& , CppAttractRigidbody& , CppAttractPairList & , int) 


cdef class ScorpionForceField:
   
    cdef CppScorpionForceField* thisptr


    def __cinit__(self, filename, cutoff):
        cdef char* c_filename
        cdef string * cppname

        c_filename = <char*> filename
        cppname = new string(c_filename)
        self.thisptr = new CppScorpionForceField(deref(cppname), cutoff)
        del cppname

    def __dealloc__(self):
        del self.thisptr

    def add_ligand(self, AttractRigidbody rig):
        self.thisptr.AddLigand(deref(<CppAttractRigidbody*> rig.thisptr))

    def function(self, vec):
        cdef vector[double] v
        for el in vec:
           v.push_back(el)

        return self.thisptr.Function(v)
        
    def get_vdw(self):
        return self.thisptr.getVdw()
    
    def get_coulomb(self):
        return self.thisptr.getCoulomb()

    def nonbon8(self, AttractRigidbody rec, AttractRigidbody lig, AttractPairList pl, verbose=False):
        return self.thisptr.nonbon8(deref(<CppAttractRigidbody*>rec.thisptr), deref(<CppAttractRigidbody*>lig.thisptr), deref(pl.thisptr), verbose)
