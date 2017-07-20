cdef extern from "atom.h" namespace "PTools":
    cdef cppclass CppAtomproperty "PTools::Atomproperty":
        CppAtomproperty()
        CppAtomproperty(CppAtomproperty&)

        void setAtomType(string &)
        string residuetag()

        string atomElement
        string atomType
        string _pdbAtomType
        string residType
        double atomCharge
        string chainId
        int residId
        int atomId
        string extra
        
    cdef cppclass CppAtom "PTools::Atom"(CppAtomproperty):
        CppAtom()
        CppAtom(CppAtomproperty, CppCoord3D)
        
        string ToString()
        string ToPdbString()
        void Translate(CppCoord3D&)
        CppCoord3D coords
        
    cdef double cppDist "PTools::Dist" (CppAtom& , CppAtom& )
    cdef double cppDist2 "PTools::Dist2" (CppAtom& , CppAtom& )

cdef extern from "cython_wrappers.h":
    cdef void cy_copy_atom(CppAtom* , CppAtom* )


cdef extern from "atom.h" namespace "PTools::Atomproperty":
    string getTagDelimiter()
    void setTagDelimiter(string &)
    
        
cdef class Atomproperty:
    cdef CppAtomproperty * thisptr
    
    def __cinit__(self):
        self.thisptr = new CppAtomproperty()
        
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr

    @classmethod
    def get_tag_delimiter(cls):
        return getTagDelimiter()

    @classmethod
    def set_tag_delimiter(cls, bytes value):
        cdef char* c = value
        setTagDelimiter(string(c))

    def residuetag(self):
        return self.thisptr.residuetag()
    
    property atomType:
        def __get__(self):
            return <bytes> self.thisptr.atomType.c_str()
        def __set__(self, bytes b):
            cdef char* c = b
            cdef string cppname = string(c)
            self.thisptr.setAtomType(cppname)

    property _pdbAtomType:
        def __get__(self):
            return <bytes> self.thisptr._pdbAtomType.c_str()
        def __set__(self, bytes b):
            cdef char* c = b
            cdef string cppname = string(c)
            self.thisptr._pdbAtomType = cppname
        
    property residType:
        def __get__(self):   
            return <bytes> self.thisptr.residType.c_str()
    
        def __set__(self, bytes residtype):
            cdef char * c_residtype = residtype
            self.thisptr.residType = string(c_residtype)

    property atomCharge:
        def __get__(self):
            return self.thisptr.atomCharge
    
        def __set__(self, double charge):
            self.thisptr.atomCharge = charge

    property atomElement:
        def __get__(self):
            return self.thisptr.atomElement
    
        def __set__(self, bytes element):
            self.thisptr.atomElement = element
    
    property chainId:
        def __get__(self):
            return <bytes> self.thisptr.chainId.c_str()
    
        def __set__(self, bytes chainid):
            cdef char * c_chainid = chainid
            self.thisptr.chainId = string(c_chainid)
    
    property residId:    
        def __get__(self):
            return self.thisptr.residId
        
        def __set__(self, int resid):
            self.thisptr.residId = resid 
        
    
    property atomId:
        def __get__(self):
            return self.thisptr.atomId
        def __set__(self, int atomid):
            self.thisptr.atomId = atomid

    property extra:
        def __set__(self, bytes extra):
            cdef char* c_extra = extra
            self.thisptr.extra = string(c_extra)
        def __get__(self):
            return self.thisptr.extra.c_str()

        
cdef class Atom(Atomproperty):
    #cdef CppAtom * thisptr
    #def __cinit__(self, Atomproperty atproperty, Coord3D coords):
    def __cinit__(self, *args ):
        cdef CppAtomproperty * cppatpropptr
        cdef CppCoord3D * cpp_coptr
        
        #the contructor of Atomproperty was already called here,
        #so thisptr already points to allocated data
        #we allocate here new data for a CppAtom instead of a CppAtomproperty
        del self.thisptr
        self.thisptr = <CppAtomproperty*> 0
        
        if len(args) == 0:
            #no argument: allocate empty object
            self.thisptr = new CppAtom()
        else:
           #contructor called with (Atomproperty atproperty, Coord3D coords)
           if isinstance(args[0],Atomproperty) and isinstance(args[1], Coord3D):
               atproperty = <Atomproperty?> args[0]
               coords = <Coord3D?> args[1]
               cppatpropptr = atproperty.thisptr
               cpp_coptr = coords.thisptr
               self.thisptr = new CppAtom(deref(cppatpropptr), deref(cpp_coptr))
               return
           else:
              raise TypeError("error: wrong argument type in Atom initialization")
        
    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr
            self.thisptr = <CppAtomproperty*> 0
    
    property coords:
        def __get__(self):
            co = Coord3D()
            cdef CppCoord3D c_coord3D = (<CppAtom*>self.thisptr).coords
            co.x = c_coord3D.x
            co.y = c_coord3D.y
            co.z = c_coord3D.z
            return co
        
        def __set__(self, Coord3D co):
            (<CppAtom*>self.thisptr).coords = deref(co.thisptr)

    def set_coords(self, co):
        self.coords = co
        
    def ToString(self):
        return <bytes> (<CppAtom*>self.thisptr).ToString().c_str()
    def __str__(self):
        return self.ToString()
        
    def ToPdbString(self):
        return <bytes> (<CppAtom*>self.thisptr).ToPdbString().c_str()
    
    def Translate(self,Coord3D co):
       (<CppAtom*>self.thisptr).Translate(deref(co.thisptr))

    
def Dist(Atom at1, Atom at2):
    return cppDist(deref(<CppAtom*>at1.thisptr), deref(<CppAtom*>at2.thisptr))
    
def Dist2(Atom at1, Atom at2):
    return cppDist2(deref(<CppAtom*>at1.thisptr), deref(<CppAtom*>at2.thisptr))
        
