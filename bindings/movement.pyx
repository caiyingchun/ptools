# distutils: language = c++


cdef extern from "Movement.h" namespace "PTools":
    cdef cppclass CppMovement "PTools::Movement":
        CppMovement() except+
        CppMovement(Array2D[double] &)
        Array2D[double] m
        void Apply(CppRigidbody&)


cdef class Movement:
    cdef CppMovement *thisptr
    def __cinit__(self):
        self.thisptr = new CppMovement()
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr
    def Apply(self, Rigidbody rigid):
        self.thisptr.Apply(deref(rigid.thisptr))


cdef class Shift(Movement):
    pass

cdef class Slide(Movement):
    pass

cdef class Rise(Movement):
    pass

cdef class Twist(Movement):
    pass

cdef class Roll(Movement):
    pass

cdef class Tilt(Movement):
    pass

cdef class ADNA(Movement):
    pass

cdef class BDNA(Movement):
    pass
