#include <sstream>
#include <stdio.h>

#include "atom.h"
#include "coord3d.h"

using namespace std;

namespace PTools{


std::string Atomproperty::tagDelimiter = ":";

//! Convert an atom to a string
std::string Atom::ToString() const {
    std::stringstream info;
    info << atomId << " " << atomType << " ";
    info << residType << " " << chainId << " " << residId;
    info << PrintCoord(coords);
    return info.str();
}


//! convert an atom to a string in PDB format
std::string Atom::ToPdbString() const
{
    char output[81];
    const char* atomname = this->atomType.c_str();
    const char* residName = this->residType.c_str();
    int residnumber = this->residId;
    const char* chainID = this->chainId.c_str();

    int atomnumber = atomId;

    double x = coords.x;
    double y = coords.y;
    double z = coords.z ;

    snprintf(output,80,"ATOM  %5d %-4s %3s %1s%4d    %8.3f%8.3f%8.3f%s",
	     atomnumber,atomname,residName,chainID,residnumber,x,y,z,extra.c_str());
//     output[79]='\n';
//     output[80]='\0';
    return std::string(output);
}

//! translate an atom with a Coord3D vector
void Atom::Translate(const Coord3D& tr)
{
    coords = coords+tr;
}


/**
 * Attempts to set a pdbAtomType from a string
 * 
 * The PDB atomType field (CA, N, HN1, ...) is delicate to set in
 * a user-friendly way. This field is represented with 4 chars but
 * the alignment of shorter names is not free. 
 * Indeed " CA " will represent Calpha atoms for aminoacids residus
 * while "CA  " will represent calcium atoms, normally written as 
 * HETATM in the PDB format. 
 * 
 * This method takes a "user-friendly" representation of atom types
 * and tries to set the correct alignment for the public field "pdbAtomType".
 * 
 * "CA" will represent Calpha atoms. use "\<CA" to respresent Calcium if you really need to
 * 
 * 
 * At some point in the future atomType might need to become an accessor function
 * and call this setAtomType function implicitely.
 
 */
void Atomproperty::setAtomType(const std::string& ty)
{
    if (ty.size() == 0) return; //don't do anything. TODO: raise an exception?
    
    this->atomType = ty; //first set the atomType
    
    //and update the _pdbAtomType as well:

       if (ty.size() == 4) this->_pdbAtomType = ty; //no really other choices
       else 
           if (ty[0] == '<')  //user wants the atom type to be left-aligned
           {
            for(int i=1; i<ty.size(); i++)
                this->_pdbAtomType[i-1]=ty[i];  //left-shift ty into _pdbAtomType
           }
               
           else 
               this->_pdbAtomType = " " + ty; //in most other cases there is a leading space in the atom type
}





} // namespace PTools




