from cython.operator cimport dereference as deref
from libcpp.utility cimport pair
from libcpp cimport bool

cdef extern from "basetypes.h":
    cdef cppclass Array2D[T]:
       Array2D()
       Array2D(int, int)
       T& getItem(int, int)
       void setItem(int, int, T)
       void detach()
       string str()
       int get_nrows()
       int get_ncolumns()
       pair[int,int] get_dim()
       void Print()

    cdef cppclass cppSuperpose_t "Superpose_t" :
        double rmsd
        Array2D[double] matrix

cdef extern from "cython_wrappers.h":
     cdef void cy_copy_array2d(Array2D[double]*, Array2D[double] *) # args: (source, destination)


cdef class Matrix:
    cdef Array2D[double] * thisptr

    def __cinit__(self, row=0, col=0):
        if row==0 and col==0:
            self.thisptr = new Array2D[double]()
        else:
            self.thisptr = new Array2D[double](row, col)

    def __dealloc__(self):
        del self.thisptr

    def __str__(self):
        return self.thisptr.str().c_str()

    def __getitem__(self, key):
        assert len(key) == 2
        n, m = key
        return self.thisptr.getItem(n, m)

    def __setitem__(self, key, value):
        assert len(key) == 2
        n, m = key
        self.thisptr.setItem(n, m, value)

    def str(self):
        return self.__str__()

    def detach(self):
       self.thisptr.detach()

    def get_nrows(self):
        return self.thisptr.get_nrows()

    def get_ncolumns(self):
        return self.thisptr.get_ncolumns()

    def get_dim(self):
        return self.thisptr.get_dim()

    def Print(self):
        self.thisptr.Print()

    cdef assign_cpp_pointer(self, Array2D[double]* array2Dpointer):
        cy_copy_array2d(array2Dpointer, self.thisptr)
    


cdef class Superpose_t:
   cdef double rmsd
   cdef Matrix matrix
   
   def __cinit__(self, double rmsd, Matrix matrix):
      self.rmsd = rmsd
      self.matrix = matrix

   property rmsd:
     def __get__(self):
        return self.rmsd

   property matrix:
     def __get__(self):
        return self.matrix




#cdef class Superpose_t:
#   cdef cppSuperpose_t * thisptr
   
#   def __cinit__(self):
#      self.thisptr = new cppSuperpose_t()

#   property rmsd:
#     def __get__(self):
#        return self.thisptr.rmsd
"""
   property matrix:
     def __get__(self):
        #cdef Array2D[double] * newarray = new Array2D[double]
        pass    
        #mat = Matrix()
        #del mat.thisptr
        #mat.thisptr = 
        #return self.thisptr.matrix"""

   