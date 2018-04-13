from cython.operator cimport dereference as deref
from libcpp.string cimport string


cdef extern from "coord3d.h" namespace "PTools":
    cdef cppclass CppCoord3D  "PTools::Coord3D":  
        double x, y, z
        CppCoord3D()
        CppCoord3D(double nx, double ny, double nz)
        CppCoord3D(CppCoord3D &)
        bint operator==(CppCoord3D&)
        CppCoord3D Normalize()


    cdef CppCoord3D operator+ (CppCoord3D& A, CppCoord3D& B)
    cdef CppCoord3D operator- (CppCoord3D& A, CppCoord3D& B)
    cdef CppCoord3D operator* (double scal, CppCoord3D A)
    
    cdef double Norm(CppCoord3D&)
    cdef double Norm2(CppCoord3D&)
    cdef double dotProduct(CppCoord3D&, CppCoord3D&)
    cdef CppCoord3D crossProduct(CppCoord3D&, CppCoord3D&)

    
        
cdef make_coord3D(CppCoord3D c):
    cdef Coord3D result = Coord3D(c.x, c.y, c.z)
    return result
        
        
cdef class Coord3D:
    cdef CppCoord3D *thisptr
    def __cinit__(self, x=0, y=0, z=0):
        cdef Coord3D oldco
        if isinstance(x, Coord3D):
            oldco = <Coord3D> x
            self.thisptr = new CppCoord3D(deref(oldco.thisptr))
        else:
            self.thisptr = new CppCoord3D(x,y,z)
        
    def __dealloc__(self):
        del self.thisptr

    def _compare(self, other):
        cdef Coord3D tmp = <Coord3D> other
        cdef CppCoord3D myself = deref(self.thisptr)
        cdef CppCoord3D tocompare = deref(tmp.thisptr)
        return myself == tocompare
 
    def __richcmp__(self, other, b):
        return self._compare(other)

        
    property x:
       def __get__(self): return self.thisptr.x
       def __set__(self,x): self.thisptr.x = x
    property y:
       def __get__(self): return self.thisptr.y
       def __set__(self,y): self.thisptr.y = y
    property z:
       def __get__(self): return self.thisptr.z
       def __set__(self,z): self.thisptr.z = z

    def __abs__(Coord3D self):
        cdef Coord3D result = Coord3D(abs(self.x), abs(self.y), abs(self.z))
        return result
    
    def __add__(Coord3D self, Coord3D other):
        
          cdef CppCoord3D cppself = deref(self.thisptr)
          cdef CppCoord3D cppother = deref(other.thisptr)
          cdef CppCoord3D cppresult = cppself+cppother
        
          cdef Coord3D result = Coord3D(cppresult.x, cppresult.y, cppresult.z)
          return result
          
    def __sub__(Coord3D self, Coord3D other):
        cdef CppCoord3D cppself = deref(self.thisptr)
        cdef CppCoord3D cppother = deref(other.thisptr)
        cdef CppCoord3D cppresult = cppself-cppother
        
        cdef Coord3D result = Coord3D(cppresult.x, cppresult.y, cppresult.z)
        return result
          
    def __mul__(self, scal):
         cdef Coord3D pymyself
         cdef double cscal
         if not isinstance(self, Coord3D):
             self, scal = scal, self
         
         pymyself = <Coord3D> self
         cscal = <double> scal
         
         cdef CppCoord3D r = cscal * deref(pymyself.thisptr)
         return make_coord3D(r)

    def __div__(self, scal):
         return Coord3D(self.x / scal, self.y / scal, self.z / scal)

    def __neg__(self):
         return make_coord3D(CppCoord3D()-deref(self.thisptr))     
         
    def __str__(self):
        return "%f %f %f"%(self.x, self.y, self.z)
    
    def normalize(self):
        return make_coord3D(deref(self.thisptr).Normalize())


def norm(Coord3D v):
    return Norm(deref(v.thisptr))

def norm2(Coord3D v):
    return Norm2(deref(v.thisptr))

def dotproduct(Coord3D u, Coord3D v):
    return  dotProduct(deref(u.thisptr), deref(v.thisptr))

def crossproduct(Coord3D u, Coord3D v):
    cdef CppCoord3D cppresult = crossProduct(deref(u.thisptr), deref(v.thisptr))
    cdef Coord3D result = Coord3D(cppresult.x, cppresult.y, cppresult.z)
    return result
