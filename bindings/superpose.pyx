cdef extern from "superpose.h" namespace "PTools":
    cdef cppSuperpose_t cppsuperpose "PTools::superpose" ( CppRigidbody& ,CppRigidbody& , int )
    

cdef extern from "screw.h" namespace "PTools":
    cdef cppclass CppScrew "PTools::Screw":
        pass
        
        CppCoord3D unitVector
        CppCoord3D point
        double normtranslation
        double angle


cdef class Screw:
    cdef CppScrew * thisptr
    
    def __cinit__(self):
        self.thisptr = new CppScrew()
        
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr

    property unitVector:
        def __get__(self):
            cdef CppCoord3D ref = (<CppScrew*>self.thisptr).unitVector
            return Coord3D(ref.x, ref.y, ref.z)

        def __set__(self, Coord3D u):
            (<CppScrew*>self.thisptr).unitVector = deref(u.thisptr)

    property point:
        def __get__(self):
            cdef CppCoord3D ref = (<CppScrew*>self.thisptr).point
            return Coord3D(ref.x, ref.y, ref.z)

        def __set__(self, Coord3D u):
            (<CppScrew*>self.thisptr).point = deref(u.thisptr)


    property normtranslation:
        def __get__(self):
            return self.thisptr.normtranslation

        def __set__(self, double value):
            self.thisptr.normtranslation = value

    property angle:
        def __get__(self):
            return self.thisptr.angle

        def __set__(self, double value):
            self.thisptr.angle = value

    
def superpose(Rigidbody ref, Rigidbody mob, int verbosity=0):
    cdef cppSuperpose_t sup = cppsuperpose(deref(ref.thisptr), deref(mob.thisptr), verbosity)
    
    mat = Matrix()
    mat.assign_cpp_pointer(&sup.matrix)

    pysup = Superpose_t(sup.rmsd, mat)

    return pysup


cdef int MatTrans2screw():
    return 12

