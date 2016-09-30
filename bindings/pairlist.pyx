from cython.operator cimport dereference as deref
from libcpp.string cimport string


cdef extern from "pairlist.h" namespace "PTools":
    cdef cppclass CppAtomPair "PTools::AtomPair":
       CppAtomPair()
       CppAtomPair(CppAtomPair&)
       int atlig
       int atrec


cdef class AtomPair:
    cdef CppAtomPair * thisptr

    def __cinit__(self, *args):
       cdef CppAtomPair* catp
       self.thisptr = <CppAtomPair*> 0
       if len(args) == 0: #default constructor
          self.thisptr = new CppAtomPair()
          return
       if len(args) == 1 and isinstance(args[0], AtomPair):
          pyAtp = <AtomPair ?> args[0]
          catp = <CppAtomPair*> pyAtp.thisptr
          self.thisptr = new CppAtomPair(deref(catp))
          return
       raise "cannot reach here"
    
    def __dealloc__(self):
       if self.thisptr:
          del self.thisptr
          self.thisptr = <CppAtomPair*> 0

    property atlig:
       def __get__(self):
           return self.thisptr.atlig
       def __set__(self, int value):
           self.thisptr.atlig = value


    property atrec:
       def __get__(self):
           return self.thisptr.atrec
       def __set__(self, int value):
           self.thisptr.atrec = value



cdef extern from "pairlist.h" namespace "PTools":
    cdef cppclass CppAttractPairList "PTools::AttractPairList":
       CppAttractPairList()
       CppAttractPairList(CppAttractRigidbody &, CppAttractRigidbody &, double )
       CppAttractPairList(CppAttractRigidbody &, CppAttractRigidbody & )
       int Size()
       CppAtomPair operator[](int)



cdef class AttractPairList:
    cdef CppAttractPairList * thisptr

    def __cinit__(self, *args):
        self.thisptr = <CppAttractPairList*> 0
        if len(args) == 0: 
            self.thisptr = new CppAttractPairList()
        if isinstance(args[0], AttractRigidbody) and isinstance(args[1], AttractRigidbody):
            r1 = <AttractRigidbody> args[0]
            r2 = <AttractRigidbody> args[1]

            if len(args) == 2:
               self.thisptr = new CppAttractPairList(CppAttractRigidbody(deref(r1.thisptr)), CppAttractRigidbody(deref(r2.thisptr)))
               return
            if len(args) == 3 :
               self.thisptr = new CppAttractPairList(CppAttractRigidbody(deref(r1.thisptr)), CppAttractRigidbody(deref(r2.thisptr)), <double?> args[2] )
               return
        raise TypeError("arguments error in AttractPairList.__cinit__()")
          

    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr


    def __len__(self):
        return self.thisptr.Size()
     
    def __getitem__(self, unsigned int i):
        if i>=self.thisptr.Size():
            raise IndexError
        cdef CppAtomPair * catp = new CppAtomPair(deref(self.thisptr)[i])
        atp = AtomPair()
        if atp.thisptr:
            del atp.thisptr
        atp.thisptr = catp
        return atp
        
