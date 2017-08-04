#ifndef ATOM_H
#define ATOM_H

#include "basetypes.h"

#include <stdio.h>
#include <string>
#include "coord3d.h"

namespace PTools{


struct Atomproperty {
    std::string atomType;  ///< CA, N, HN1, ...
    void setAtomType(const std::string &ty); ///< attempts to set a pdbAtomType from a string

    std::string _pdbAtomType; ///<  PDB atomType field is not really user-friendly ( " CA ", ...) 

    std::string atomElement; ///< C, N, H, O, etc.
    std::string residType; ///< LEU, ARG, ...
    std::string chainId; ///< A, B, etc.
    int residId; ///< residue number
    int atomId; ///< atom number
    dbl atomCharge; ///< charge of the atom
    std::string extra; ///< extra data

    /// default constructor
    Atomproperty()
    {
        atomType="X";
        atomElement="X";
        _pdbAtomType="?";
        residType="XXX";
        chainId="X";
        residId=1;
        atomId=1;
        atomCharge=0.0;
    };

    /// Get/Set separator string used to separate elements in tag string.
    static std::string tagDelimiter;

    static std::string getTagDelimiter()
    {
        return tagDelimiter;
    }

    static void setTagDelimiter(const std::string & delimiter)
    {
        tagDelimiter = delimiter;
    }

    /// Construct a residue tag that should be unique for a molecule.
    /// Residue tag is made of residue name, residue sequence number and chain
    /// identifier. Those elements are separated by AtomProperty tagDelimiter.
    std::string residuetag() const
    {
        char buf[10];
        std::sprintf(buf, "%d", residId);
        std::string residStr(buf);
        return residType + tagDelimiter + residStr + tagDelimiter + chainId;
    }

};


struct Atom : public Atomproperty
{

public:
    Coord3D coords; ///< Atom cartesian coordinates


    Atom() {};
    Atom(Atomproperty ap, Coord3D co)
            : Atomproperty(ap), coords(co) {};
    
    /// convert atom (properties and coordinates) to std::string
    std::string ToString() const;

    /// convert atom (properties and coordinates) to classical PDB-like string
    std::string to_pdb_string() const ;

    /// translation of an atom
    void translate(const Coord3D& tr);

};


/// distance between two atoms
inline dbl dist(const Atom& at1, const Atom& at2)
{
    return Norm(at1.coords-at2.coords);
}

/// distance**2 between two atoms
inline dbl dist2(const Atom& at1, const Atom& at2)
{
    return Norm2(at1.coords - at2.coords );
}


}

#endif


