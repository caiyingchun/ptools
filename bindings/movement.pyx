# distutils: language = c++


cdef extern from "Movement.h" namespace "PTools":
    cdef cppclass CppMovement "PTools::Movement":
        CppMovement() except+
        CppMovement(Array2D[double] &)
        Array2D[double] m
        void Apply(CppRigidbody&)


    cdef cppclass CppShift "PTools::Movement":
        CppShift()

    cdef cppclass CppSlide "PTools::Movement":
        CppSlide()

    cdef cppclass CppRise "PTools::Movement":
        CppRise()

    cdef cppclass CppTwist "PTools::Movement":
        CppTwist()

    cdef cppclass CppRoll "PTools::Movement":
        CppRoll()

    cdef cppclass CppTilt "PTools::Movement":
        CppTilt()

    cdef cppclass CppADNA "PTools::Movement":
        CppADNA()

    cdef cppclass CppBDNA "PTools::Movement":
        CppBDNA()



cdef class Movement:
    cdef CppMovement *thisptr
    def __cinit__(self):
        self.thisptr = new CppMovement()
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr
    def Apply(self, Rigidbody rigid):
        self.thisptr.Apply(deref(rigid.thisptr))


cdef class Shift:
    cdef CppShift *thisptr
    
    def __cinit__(self):
        self.thisptr = new CppShift()
    
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr


cdef class Slide:
    cdef CppSlide *thisptr
    
    def __cinit__(self):
        self.thisptr = new CppSlide()
    
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr


cdef class Rise:
    cdef CppRise *thisptr
    
    def __cinit__(self):
        self.thisptr = new CppRise()
    
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr


cdef class Twist:
    cdef CppTwist *thisptr
    
    def __cinit__(self):
        self.thisptr = new CppTwist()
    
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr


cdef class Roll:
    cdef CppRoll *thisptr
    
    def __cinit__(self):
        self.thisptr = new CppRoll()
    
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr


cdef class Tilt:
    cdef CppTilt *thisptr
    
    def __cinit__(self):
        self.thisptr = new CppTilt()
    
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr

cdef class ADNA:
    cdef CppADNA *thisptr
    
    def __cinit__(self):
        self.thisptr = new CppADNA()
    
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr


cdef class BDNA:
    cdef CppBDNA *thisptr
    
    def __cinit__(self):
        self.thisptr = new CppBDNA()
    
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr

