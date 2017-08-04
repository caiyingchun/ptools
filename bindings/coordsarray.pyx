cdef extern from "coordsarray.h" namespace "PTools":
    cdef cppclass CppCoordsArray "PTools::CoordsArray":
      CppCoordsArray() 
      CppCoordsArray( CppCoordsArray & )
      void unsafeget_coords(unsigned int , CppCoord3D& )
      void add_coord(CppCoord3D& co)
      unsigned int size()
      void get_coords(unsigned int, CppCoord3D&) 
      void set_coords(unsigned int, CppCoord3D&)
      void translate(CppCoord3D&)
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
        return self.thisptr.size()

    def size(self):
        print "Depreciated, use len(obj) instead"
        return self.thisptr.size()

    #def unsafeget_coords(self, int i, Coord3D co):
    #    cdef Coord3D c
    #    cdef CppCoord3D *coptr
    #    c = <Coord3D> co
    #    coptr = c.thisptr
    #    self.thisptr.unsafeget_coords(i, deref(coptr))
    

    def unsafeget_coords(self, int i, Coord3D co):
       self.thisptr.unsafeget_coords(i, deref(co.thisptr))

    def add_coord(self, Coord3D co):
        self.thisptr.add_coord( deref(co.thisptr) )

    def get_coords(self, i, Coord3D co):
        self.thisptr.get_coords(i, deref(co.thisptr))

    def set_coords(self, i, Coord3D co):
        self.thisptr.set_coords(i, deref(co.thisptr))

    def translate(self, Coord3D co):
        self.thisptr.translate(deref(co.thisptr))

    def euler_rotate(self, double phi, double ssi, double rot):
        self.thisptr.euler_rotate(phi, ssi, rot)