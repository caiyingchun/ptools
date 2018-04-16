from cython.operator cimport dereference as dereference
from libcpp.string cimport string

cdef extern from "lbfgs_interface.h" namespace "PTools":
    cdef cppclass CppScorpionLbfgs "PTools::Lbfgs":
        CppScorpionLbfgs(CppScorpionForceField&)
        void minimize(int)
        vector[double] GetMinimizedVars()
        vector[double] GetMinimizedVarsAtIter(int)
        int GetNumberIter()

cdef class ScorpionLbfgs:
    
    cdef CppScorpionLbfgs * thisptr

    def __cinit__(self, forcefield):
        
        ff = <ScorpionForceField?> forcefield
        cdef CppScorpionForceField * ffptr = ff.thisptr
        self.thisptr = new CppScorpionLbfgs(deref(ffptr))

    def __dealloc__(self):
        del self.thisptr

    def minimize(self, int maxiter):
        self.thisptr.minimize(maxiter)

    def get_minimized_vars(self):
        cdef vector[double] vars = self.thisptr.GetMinimizedVars()
        out = []
        for i in xrange(vars.size()):
            out.append(vars[i])
        return out

    def get_number_iter(self):
        return self.thisptr.GetNumberIter()

    def get_number_of_iterations(self):
        return self.thisptr.GetNumberIter()

    def get_minimized_vars_at_iter(self, int iter):
        cdef vector[double] vars = self.thisptr.GetMinimizedVarsAtIter(iter)
        out = []
        for i in xrange(vars.size()):
            out.append(vars[i])
        return out
