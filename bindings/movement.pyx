# distutils: language = c++

# Notes for the developers.
# =========================
# 
# __init__() function
# --------------------
#
# In the Python Movement classe and children, the __init__ function is
# declared and does nothing.
# This is to force the check of the number of arguments for the constructor,
# as Cython' standard behavior is to ignore extra arguments (for the
# constructor only).
#


from libcpp.string cimport string


cdef extern from "Movement.h" namespace "PTools":
    cdef cppclass CppMovement "PTools::Movement":
        CppMovement() except+
        CppMovement(Array2D[double] &)
        Array2D[double] m
        void apply(CppRigidbody&)
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

    def __init__(self):
        pass

    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr
    
    def apply(self, Rigidbody rigid):
        self.thisptr.apply(deref(rigid.thisptr))

    def Print(self):
        self.thisptr.Print()

    def toString(self):
        return self.thisptr.toString()


cdef class Shift(Movement):
    def __cinit__(self, double alpha):
        self.thisptr = <CppMovement *>new CppShift(alpha)

    def __init__(self, double alpha):
        pass


cdef class Slide(Movement):
    def __cinit__(self, double alpha):
        self.thisptr = <CppMovement *>new CppSlide(alpha)

    def __init__(self, double alpha):
        pass


cdef class Rise(Movement):
    def __cinit__(self, double alpha):
        self.thisptr = <CppMovement *>new CppRise(alpha)

    def __init__(self, double alpha):
        pass


cdef class Twist(Movement):
    def __cinit__(self, double alpha):
        self.thisptr = <CppMovement *>new CppTwist(alpha)

    def __init__(self, double alpha):
        pass


cdef class Roll(Movement):
    def __cinit__(self, double alpha):
        self.thisptr = <CppMovement *>new CppRoll(alpha)

    def __init__(self, double alpha):
        pass


cdef class Tilt(Movement):
    def __cinit__(self, double alpha):
        self.thisptr = <CppMovement *>new CppTilt(alpha)

    def __init__(self, double alpha):
        pass


cdef class ADNA(Movement):
    def __cinit__(self):
        self.thisptr = <CppMovement *>new CppADNA()

    def __init__(self):
        pass

cdef class BDNA(Movement):
    def __cinit__(self):
        self.thisptr = <CppMovement *>new CppBDNA()

    def __init__(self):
        pass
