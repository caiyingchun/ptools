#include <iostream>
#include <cassert>
#include <stdexcept>


#include "rmsd.h"
#include "atom.h"
#include "atomselection.h"
#include "rigidbody.h"

#include "geometry.h" //for scalar product


#define EPSILON 1e-3




namespace PTools {

dbl Rmsd(const AtomSelection& atsel1, const AtomSelection& atsel2)
{
    if (atsel1.Size() == 0  ||  atsel2.Size() == 0)
    {
        throw std::invalid_argument("EmptyRigidbody");
    }

    if (atsel1.Size() != atsel2.Size())
    {
        throw std::invalid_argument("RmsdSizesDiffers");
    }

    dbl sum = 0.0;


    for (uint i=0; i<atsel1.Size(); ++i)
    {
        Atom atom1=atsel1.copy_atom(i);
        Atom atom2=atsel2.copy_atom(i);

        sum+=dist2(atom1,atom2);
    }

    return sqrt(sum/(dbl) atsel1.Size()) ;


}



} //namespace PTools

