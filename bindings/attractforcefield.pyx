from cython.operator cimport dereference as deref
from libcpp.string cimport string

cdef extern from "<vector>" namespace "std":
    cdef cppclass vector[T]:
        cppclass iterator:
            T operator*()
            iterator operator++()
            bint operator==(iterator)
            bint operator!=(iterator)
        vector()
        void push_back(T&)
        T& operator[](int)
        T& at(int)
        int size()
        iterator begin()
        iterator end()


        
cdef extern from "forcefield.h" namespace "PTools":
    cdef cppclass CppForceField "PTools::ForceField":
        pass

cdef extern from "attractforcefield.h" namespace "PTools":
    
    cdef cppclass CppBaseAttractForceField "PTools::BaseAttractForceField" (CppForceField):
        unsigned int ProblemSize()
        double Function(vector[double]&)
        void AddLigand(CppAttractRigidbody &)
        double getVdw()
        double getCoulomb()
        double nonbon8(CppAttractRigidbody& , CppAttractRigidbody& , CppAttractPairList & , int) 
        
        
    
    cdef cppclass CppAttractForceField2 "PTools::AttractForceField2" (CppBaseAttractForceField)  :
       CppAttractForceField2(string&, double)
       
       
cdef class BaseAttractForceField:
    cdef CppBaseAttractForceField * thisptr
       
       
    

cdef class AttractForceField2(BaseAttractForceField):
    cdef object rigidlist
    #cdef CppAttractForceField2* thisptr
    
    def __cinit__(self, filename, cutoff):
        cdef char* c_filename
        cdef string * cppname

        c_filename = <char*> filename
        cppname = new string(c_filename)
        self.rigidlist = []
        self.thisptr = new CppAttractForceField2(deref(cppname), cutoff)
        del cppname

    def __dealloc__(self):
        del self.thisptr

    def add_ligand(self, AttractRigidbody rig):
        self.rigidlist.append(rig)
        self.thisptr.AddLigand(deref(<CppAttractRigidbody*>rig.thisptr))

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


cdef extern from "attractforcefield.h" namespace "PTools":
    cdef cppclass CppAttractForceField1 "PTools::AttractForceField1"(CppBaseAttractForceField):
       CppAttractForceField1(string&, double)
       void AddLigand(CppAttractRigidbody&)
       double Function(vector[double]&)
       double getVdw()
       double getCoulomb()
       


cdef class AttractForceField1(BaseAttractForceField):
   
    #cdef CppAttractForceField1* thisptr


    def __cinit__(self, filename, cutoff):
        cdef char* c_filename
        cdef string * cppname

        c_filename = <char*> filename
        cppname = new string(c_filename)
        self.thisptr = new CppAttractForceField1(deref(cppname), cutoff)
        del cppname

    def __dealloc__(self):
        del self.thisptr

    def add_ligand(self, AttractRigidbody rig):
        self.thisptr.AddLigand(deref(<CppAttractRigidbody*>rig.thisptr))

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

