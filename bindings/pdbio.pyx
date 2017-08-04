from cython.operator cimport dereference as deref
from libcpp.string cimport string


cdef extern from "pdbio.h" namespace "PTools":
    cdef void Cppwrite_pdb "PTools::write_pdb" (CppRigidbody&, string)
    cdef void CppReadAtom "PTools::readAtom" (string, CppAtom) except+




def write_pdb(Rigidbody rig, bytes filename):
    """writes a rigidbody object to a PDB file"""
    if rig is None:
       raise RuntimeError("expected Rigidbody, None given")
    cdef string cpp_filename = <string?> filename
    Cppwrite_pdb(deref(rig.thisptr),  cpp_filename)


def strToAtom(bytes line):
    """converts a PDB-formatted Python string into an Atom object"""
    cdef char* c_str = <char *> line
    cdef string* cpp_str = new string(c_str)
    cdef CppAtom* c_at =  new CppAtom()

    CppReadAtom(deref(cpp_str), deref(c_at))
    
    at = Atom()
    del at.thisptr
    at.thisptr = c_at

    del cpp_str

    return at

    