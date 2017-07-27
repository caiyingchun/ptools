
import warnings

from cython.operator cimport dereference as deref
from libcpp.string cimport string


cdef extern from "<sstream>" namespace "std":
    cdef cppclass stringstream:
        stringstream()
        string str()
        void str(string & s)


cdef extern from "rigidbody.h" namespace "PTools":
    cdef cppclass CppRigidbody "PTools::Rigidbody":
        CppRigidbody(string) except+
        CppRigidbody()
        CppRigidbody(CppRigidbody &)
        unsigned int size()
        CppCoord3D get_coords(unsigned int)
        void unsafeget_coords(unsigned int, CppCoord3D &)
        void set_coords(unsigned int, CppCoord3D &)
        void rotate(CppCoord3D &, CppCoord3D &, double)
        void translate(CppCoord3D &)
        CppCoord3D find_center()
        void sync_coords()
        void euler_rotate(double, double, double)
        void apply_matrix(Array2D[double] &)
        CppAtom copy_atom(unsigned int)
        void add_atom(CppAtomproperty &, CppCoord3D)
        void add_atom(CppAtom &)
        void set_atom(unsigned int, CppAtom &)
        string print_pdb()
        CppRigidbody operator+(CppRigidbody &)
        void CenterToOrigin()

        # Returns radius of gyration.
        double radius_of_gyration()

        # Returns the radius of a Rigidbody (max distance from center).
        double radius()

        CppAtomproperty & get_atom_property(unsigned int)
        void set_atom_property(unsigned int, CppAtomproperty &)

        # AtomSelection:
        CppAtomSelection select_all_atoms()
        CppAtomSelection select_atomtype(string)
        CppAtomSelection select_restype(string)
        CppAtomSelection select_chainid(string)
        CppAtomSelection select_resid_range(int, int)
        CppAtomSelection get_CA()
        CppAtomSelection backbone()


cdef extern from "pdbio.h" namespace "PTools":
    # in fact ReadPDB does not really take a stringstream as input argument,
    # but it makes cython happy about typing and C++ is also happy due to
    # inheritance
    cdef void ReadPDB(stringstream&, CppRigidbody&)


cdef class Rigidbody:
    cdef CppRigidbody* thisptr

    def __cinit__(self, filename=''):
        cdef CppRigidbody * oldrigidptr
        cdef Rigidbody  oldrigid
        cdef char * name
        cdef string * cppname
        cdef CppRigidbody * newrigid

        if isinstance(filename, str):
            if filename == '':
                self.thisptr = new CppRigidbody()
            else:
                # there is a filename, loading the pdb file
                name = filename
                cppname = new string(name)
                newrigid = new CppRigidbody(deref(cppname))
                del cppname
                self.thisptr = newrigid

        elif isinstance(filename, Rigidbody):
            oldrigid = <Rigidbody> filename
            oldrigidptr = <CppRigidbody*> (oldrigid.thisptr)
            self.thisptr = new CppRigidbody(deref(oldrigidptr))
            if not self.thisptr:
                print "FATAL: this should never happen"

        elif hasattr(filename, "read"):
            # we consider filename as a file-like object
            # print "reading rigidbody from file-like"
            self.thisptr = new CppRigidbody()
            loadPDBfromPythonFileLike(filename, self.thisptr)

        else:
            raise RuntimeError("invalid argument in Rigidbody()")

    def __dealloc__(self):
        if self.thisptr:
            del self.thisptr
            self.thisptr = <CppRigidbody*> 0

    def __len__(self):
        return self.thisptr.size()

    def __str__(self):
        s = self.thisptr.print_pdb()
        return s

    def __add__(Rigidbody self, Rigidbody other):
        cdef CppRigidbody cppself = deref(self.thisptr)
        cdef CppRigidbody cppother = deref(other.thisptr)
        cdef CppRigidbody * result = new CppRigidbody(cppself + cppother)
        cdef Rigidbody pyrb = Rigidbody()
        del pyrb.thisptr
        pyrb.thisptr = result
        return pyrb

    def size(self):
        return len(self)

    def get_coords(self, unsigned int i):
        cdef Coord3D c = Coord3D()
        cdef CppCoord3D cpp = self.thisptr.get_coords(i)
        c.x = cpp.x
        c.y = cpp.y
        c.z = cpp.z
        return c

    def print_pdb(self):
        return str(self)

    def unsafeget_coords(self, unsigned int i, Coord3D co):
        self.thisptr.unsafeget_coords(i, deref(co.thisptr))

    def set_coords(self, int i, Coord3D co):
        self.thisptr.set_coords(i, deref(co.thisptr))

    def translate(self, Coord3D tr):
        self.thisptr.translate(deref(tr.thisptr))

    def find_center(self):
        cdef Coord3D c = Coord3D()
        cdef CppCoord3D cpp = self.thisptr.find_center()
        c.x = cpp.x
        c.y = cpp.y
        c.z = cpp.z
        return c

    def rotate(self, Coord3D A, Coord3D B, double theta):
        self.thisptr.rotate(deref(A.thisptr), deref(B.thisptr), theta)
        return None

    def euler_rotate(self, double phi, double ssi, double rot):
        self.thisptr.euler_rotate(phi, ssi, rot)

    def sync_coords(self):
        self.thisptr.sync_coords()

    def apply_matrix(self, Matrix mat):
        self.thisptr.apply_matrix(deref(mat.thisptr))

    def copy_atom(self, unsigned int atid):
        cdef CppAtom cpp_at = self.thisptr.copy_atom(atid)
        cdef Atom at = Atom()
        cdef CppAtom * cpp_dest = <CppAtom*> at.thisptr
        cy_copy_atom(& cpp_at, cpp_dest)
        return at

    def add_atom(self, Atom at):
        self.thisptr.add_atom(deref(<CppAtom*>at.thisptr))

    def set_atom(self, unsigned int position, Atom at):
        self.thisptr.set_atom(position, deref(<CppAtom*>at.thisptr))

    def get_atom_property(self, unsigned int position):
        cdef CppAtomproperty cppatprop = self.thisptr.get_atom_property(position)
        cdef Atomproperty pyAtprop = Atomproperty()
        cdef CppAtomproperty * new_atomprop = new CppAtomproperty(cppatprop)
        del pyAtprop.thisptr
        pyAtprop.thisptr = new_atomprop
        return pyAtprop

    def set_atom_property(self, unsigned int position, Atomproperty prop):     
        if position < 0  or position >= len(self):
            raise IndexError('atom index out of bounds')
        self.thisptr.set_atom_property(position, deref(<CppAtomproperty*>prop.thisptr))

    def radius(self):
        return self.thisptr.radius()

    def radius_of_gyration(self):
        return self.thisptr.radius_of_gyration()

    def select_all_atoms(self):
        ret = AtomSelection()
        del ret.thisptr
        cdef CppAtomSelection new_sel = self.thisptr.select_all_atoms()
        ret.thisptr = new CppAtomSelection(new_sel)
        return ret

    def select_atomtype(self, bytes b):
        ret = AtomSelection()
        del ret.thisptr
        cdef char * c_typename = b
        cdef string * cpp_atomtype = new string(c_typename)
        cdef CppAtomSelection new_sel = self.thisptr.select_atomtype(deref(cpp_atomtype))
        del cpp_atomtype
        ret.thisptr = new CppAtomSelection(new_sel)
        return ret

    def select_restype(self, bytes b):
        ret = AtomSelection()
        del ret.thisptr
        cdef char * c_typename = b
        cdef string * cpp_residtype = new string(c_typename)
        cdef CppAtomSelection new_sel = self.thisptr.select_restype(deref(cpp_residtype))
        del cpp_residtype
        ret.thisptr = new CppAtomSelection(new_sel)
        return ret

    def select_chainid(self, bytes b):
        ret = AtomSelection()
        del ret.thisptr
        cdef char * c_typename = b
        cdef string * cpp_chainid = new string(c_typename)
        cdef CppAtomSelection new_sel = self.thisptr.select_chainid(deref(cpp_chainid))
        del cpp_chainid
        ret.thisptr = new CppAtomSelection(new_sel)
        return ret

    def select_resid_range(self, int i, int j):
        ret = AtomSelection()
        del ret.thisptr
        cdef CppAtomSelection new_sel = self.thisptr.select_resid_range(i, j)
        ret.thisptr = new CppAtomSelection(new_sel)
        return ret

    def get_CA(self):
        ret = AtomSelection()
        del ret.thisptr
        cdef CppAtomSelection new_sel = self.thisptr.get_CA()
        ret.thisptr = new CppAtomSelection(new_sel)
        return ret

    def backbone(self):
        ret = AtomSelection()
        del ret.thisptr
        cdef CppAtomSelection new_sel = self.thisptr.backbone()
        ret.thisptr = new CppAtomSelection(new_sel)
        return ret

    def center_to_origin(self):
        self.thisptr.CenterToOrigin()


cdef CppRigidbody* _getRigidbody_from_py_name(pyname):
    cdef char * name = pyname
    cdef string * cppname = new string(name)
    cdef CppRigidbody *newrigid = new CppRigidbody(deref(cppname))
    del cppname
    return newrigid


cdef loadPDBfromPythonFileLike(file, CppRigidbody* rigid):
    cdef string cppstring
    lines = file.readlines()

    for i in lines:
        cppstring += <char*> i

    cdef stringstream sstr
    sstr.str(cppstring)
    ReadPDB(sstr, deref(rigid))


cdef c_to_python_string():
    cdef char * test = "hello world"
    cdef bytes b = test
    return b
