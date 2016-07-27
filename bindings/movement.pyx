# distutils: language = c++

from libcpp.string cimport string


cdef extern from "Movement.h" namespace "PTools":
    cdef cppclass CppMovement "PTools::Movement":
        CppMovement() except+
        CppMovement(Array2D[double] &)
        Array2D[double] m
        void Apply(CppRigidbody&)
        void Print() const
        string toString() const;

    cdef cppclass CppShift "PTools::Shift"(CppMovement):
        CppShift(double alpha)

    cdef cppclass CppSlide "PTools::Slide"(CppMovement):
        CppSlide(double alpha)

    cdef cppclass CppRise "PTools::Rise"(CppMovement):
        CppRise(double alpha)

    cdef cppclass CppTwist "PTools::Twist"(CppMovement):
        CppTwist(double alpha)

    cdef cppclass CppRoll "PTools::Roll"(CppMovement):
        CppRoll(double alpha)

    cdef cppclass CppTilt "PTools::Tilt"(CppMovement):
        CppTilt(double alpha)

    cdef cppclass CppADNA "PTools::ADNA"(CppMovement):
        CppADNA()

    cdef cppclass CppBDNA "PTools::BDNA"(CppMovement):
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

    def Print(self):
        self.thisptr.Print()

    def toString(self):
        return self.thisptr.toString()



cdef class Shift(Movement):
    def __cinit__(self, alpha):
        self.thisptr = <CppMovement *>new CppShift(alpha)


cdef class Slide(Movement):
    def __cinit__(self, alpha):
        self.thisptr = <CppMovement *>new CppSlide(alpha)


cdef class Rise(Movement):
    def __cinit__(self, alpha):
        self.thisptr = <CppMovement *>new CppRise(alpha)


cdef class Twist(Movement):
    def __cinit__(self, alpha):
        self.thisptr = <CppMovement *>new CppTwist(alpha)


cdef class Roll(Movement):
    def __cinit__(self, alpha):
        self.thisptr = <CppMovement *>new CppRoll(alpha)


cdef class Tilt(Movement):
    def __cinit__(self, alpha):
        self.thisptr = <CppMovement *>new CppTilt(alpha)


cdef class ADNA(Movement):
    def __cinit__(self):
        self.thisptr = <CppMovement *>new CppADNA()


cdef class BDNA(Movement):
    def __cinit__(self):
        self.thisptr = <CppMovement *>new CppBDNA()
