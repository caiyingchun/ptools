cdef extern from "rmsd.h" namespace "PTools":
    cdef double CppRmsd "PTools::Rmsd" (CppRigidbody& r1, CppRigidbody& r2) except +ValueError
    cdef double CppRmsd "PTools::Rmsd" (CppAtomSelection & r1, CppAtomSelection& r2) except +ValueError

    
def rmsd(r1, r2):
    """calculates the RMSD between two objects (either Rigibody or AtomSelection). This function does NOT perform
    superposition before the calculation"""

    cdef CppAtomSelection* er1 = <CppAtomSelection*> 0
    cdef CppAtomSelection* er2 = <CppAtomSelection*> 0
    cdef AtomSelection as1
    cdef CppRigidbody* rb1

    del_er1 = False
    del_er2 = False

     
    if isinstance(r1, AtomSelection):
       # conversion AtomSelection => CppAtomSelection*
       as1 = <AtomSelection?> r1
       er1 = as1.thisptr 
    elif isinstance(r1, Rigidbody):
       # conversion Rigibody => CppAtomSelection *
       rb1 = (<Rigidbody?>r1).thisptr
       er1 = new CppAtomSelection(deref(rb1))
       del_er1 = True
    else: raise RuntimeError("first argument should be an AtomSelection or a Rigidbody")



    if isinstance(r2, AtomSelection):
       # conversion AtomSelection => CppAtomSelection*
       as2 = <AtomSelection?> r2
       er2 = as2.thisptr

    elif isinstance(r2, Rigidbody):
       # conversion Rigibody => CppAtomSelection *
       rb2 = (<Rigidbody?>r2).thisptr
       er2 = new CppAtomSelection(deref(rb2))
       del_er2 = True
    else: raise RuntimeError("second argument should be an AtomSelection or a Rigidbody")
    
    rmsd = CppRmsd(deref(er1), deref(er2))

    if del_er1:
       del er1
    if del_er2:
       del er2

    return rmsd

    #cdef CppRigidbody* er1 = r1.thisptr
    #cdef CppRigidbody* er2 = r2.thisptr
    #return CppRmsd(deref(er1), deref(er2))
    

        