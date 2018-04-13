
cdef extern from "BasePair.h" namespace "PTools":
    cdef cppclass CppBasePair "PTools::BasePair":
        CppBasePair(string)
        CppBasePair(CppRigidbody&)
        CppBasePair(CppBasePair&)
        CppRigidbody GetRigidBody()
        unsigned int Size()


cdef class BasePair:
    cdef CppBasePair* thisptr

    def __cinit__(self,arg=None):
        cdef string fn

        if arg is not None:
            if isinstance(arg, str):
                fn = <string?> arg
                self.thisptr = new CppBasePair(fn)
            elif isinstance(arg, Rigidbody):
                rb = <Rigidbody> arg
                self.thisptr = new CppBasePair(deref(rb.thisptr))
            else:
                raise RuntimeError("unknown arg type")

    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr
            self.thisptr = <CppBasePair*> 0

    def __len__(self):
        return self.size()

    def size(self):
        return self.thisptr.Size()

    def get_rigid_body(self):
        # Get a pointer to the RigidBody.
        cdef CppRigidbody * new_rb = new CppRigidbody(self.thisptr.GetRigidBody())

        # Create a new Python Rigidbody and makes it point to the cpp copy.
        cdef Rigidbody rb = Rigidbody()
        del rb.thisptr
        rb.thisptr = new_rb
        return rb
