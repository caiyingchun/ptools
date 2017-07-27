cdef extern from "coordsarray.h" namespace "PTools":
    cdef cppclass CppCoordsArray "PTools::CoordsArray":
      CppCoordsArray() 
      CppCoordsArray( CppCoordsArray & )
      void unsafeGetCoords(unsigned int , CppCoord3D& )
      void add_coord(CppCoord3D& co)
      unsigned int Size()
      void GetCoords(unsigned int, CppCoord3D&) 
      void SetCoords(unsigned int, CppCoord3D&)
      void Translate(CppCoord3D&)
      void euler_rotate(double , double, double)


cdef class CoordsArray:
    cdef CppCoordsArray *thisptr

    def __cinit__(self, other=0):
       cdef CoordsArray ca
       if other != 0 :
          ca = <CoordsArray?> other
          self.thisptr = new CppCoordsArray( deref(ca.thisptr))
       else:
          self.thisptr = new CppCoordsArray()

    def __len__(self):
        return self.thisptr.Size()

    def Size(self):
        print "Depreciated, use len(obj) instead"
        return self.thisptr.Size()

    #def unsafeGetCoords(self, int i, Coord3D co):
    #    cdef Coord3D c
    #    cdef CppCoord3D *coptr
    #    c = <Coord3D> co
    #    coptr = c.thisptr
    #    self.thisptr.unsafeGetCoords(i, deref(coptr))
    

    def unsafeGetCoords(self, int i, Coord3D co):
       self.thisptr.unsafeGetCoords(i, deref(co.thisptr))

    def add_coord(self, Coord3D co):
        self.thisptr.add_coord( deref(co.thisptr) )

    def GetCoords(self, i, Coord3D co):
        self.thisptr.GetCoords(i, deref(co.thisptr))

    def SetCoords(self, i, Coord3D co):
        self.thisptr.SetCoords(i, deref(co.thisptr))

    def Translate(self, Coord3D co):
        self.thisptr.Translate(deref(co.thisptr))

    def euler_rotate(self, double phi, double ssi, double rot):
        self.thisptr.euler_rotate(phi, ssi, rot)