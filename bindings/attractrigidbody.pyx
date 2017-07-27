from cython.operator cimport dereference as deref
from libcpp.string cimport string


cdef extern from "attractrigidbody.h" namespace "PTools":
    cdef cppclass CppAttractRigidbody "PTools::AttractRigidbody":
        CppAttractRigidbody()
        CppAttractRigidbody(string&)  #filename
        CppAttractRigidbody(CppRigidbody&)
        CppAttractRigidbody(CppAttractRigidbody&)

        unsigned int getAtomTypeNumber(unsigned int)

        double getCharge(unsigned int)

        int isAtomActive(unsigned int)

        void resetForces()
        #void addForces(  #TODO: later
 
        void set_rotation(int)
        void set_translation(int)
        CppCoord3D find_center()

        unsigned int size()


        #returns radius of gyration
        double radius_of_gyration()

        #returns the radius of a Rigidbody (max distance from center)
        double radius()

        void print_matrix()

        CppAtomSelection get_CA()



cdef CppAttractRigidbody* _getAttractRigidbody_from_py_name(pyname):
    cdef char* name = pyname
    cdef string *cppname = new string(name)
    cdef CppAttractRigidbody *newrigid = new CppAttractRigidbody(deref(cppname))
    del cppname
    return newrigid


cdef class AttractRigidbody (Rigidbody) :
    # cdef CppAttractRigidbody* thisptr

    def __cinit__(self, arg):
        
        # first deallocate the previously allocated Rigidbody
        del self.thisptr
        self.thisptr = <CppRigidbody*> 0

        if isinstance(arg, Rigidbody):
           rigidbody = <Rigidbody> arg
           rigidbodyptr = <CppRigidbody*> rigidbody.thisptr
           self.thisptr = <CppRigidbody*> new CppAttractRigidbody(deref(rigidbodyptr))
           return
        elif isinstance(arg, str):
           self.thisptr = <CppRigidbody*> _getAttractRigidbody_from_py_name(arg)
           return
        elif isinstance(arg, AttractRigidbody):
           oldrigidbody = <AttractRigidbody> arg
           oldrigidbody_ptr = <CppAttractRigidbody*> oldrigidbody.thisptr
           self.thisptr = <CppRigidbody*> new CppAttractRigidbody(deref(oldrigidbody_ptr) )          
           return
        else:
           ret =  "Should never reach here(attractrigidbody.pyx:AttractRigidbody:__cinit__)"
           print ret
           print arg
           raise ret


    def __dealloc__(self):
       if self.thisptr:
           del self.thisptr
           self.thisptr = <CppRigidbody*> 0

    
    def getAtomTypeNumber(self, atomid):
         return (<CppAttractRigidbody*>self.thisptr).getAtomTypeNumber(atomid)

    def getCharge(self, atomid):
         return (<CppAttractRigidbody*>self.thisptr).getCharge(atomid)

    #void set_rotation(bool)
    def set_rotation(self, flag):
        (<CppAttractRigidbody*> self.thisptr).set_rotation(flag)

    #void set_translation(bool)
    def set_translation(self, flag):
        (<CppAttractRigidbody*> self.thisptr).set_translation(flag)

    def isAtomActive(self, atomid):
        return (<CppAttractRigidbody*> self.thisptr).isAtomActive(atomid)

    #void resetForces()
    def resetForces(self):
        (<CppAttractRigidbody*> self.thisptr).resetForces()

    
    def size(self):
        return self.thisptr.size()

    #define also the __len__ method:
    def __len__(self):
        return self.thisptr.size()

        
    def find_center(self):
        cdef CppRigidbody* rig = <CppRigidbody*> self.thisptr
        cdef CppCoord3D* co = new CppCoord3D (rig.find_center())
        ret = Coord3D()
        del ret.thisptr
        ret.thisptr = co
        
        return ret
        
    def translate(self, Coord3D co):
        cdef CppRigidbody* rig = <CppRigidbody*> self.thisptr
        rig.translate(deref(co.thisptr))
        
    def  euler_rotate(self, double phi, double ssi, double rot):
        cdef CppRigidbody* rig = <CppRigidbody*> self.thisptr
        rig.euler_rotate(phi, ssi, rot)


    #these function should be defined only in Rigdibody object and attractrigdbody should inherit from it:œ

    def radius(self):
       return self.thisptr.radius()

    def radius_of_gyration(self):
       return self.thisptr.radius_of_gyration()      


    def print_matrix(self):
       (<CppAttractRigidbody*> self.thisptr).print_matrix()

    def get_CA(self):
       ret = AtomSelection()
       del ret.thisptr
       cdef CppAtomSelection new_sel =  self.thisptr.get_CA()
       ret.thisptr  = new CppAtomSelection(new_sel)
       return ret