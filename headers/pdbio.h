#ifndef PDBIO_H
#define PDBIO_H

#include <cctype>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <iostream>
#include <stdexcept>


#include "rigidbody.h"

namespace PTools
{


void readAtom(const std::string & line, Atom& at); ///< create an Atom from a PDB-formatted string
void ReadPDB(std::istream& fichier,Rigidbody& protein ); ///< read a PDB file from a file pointer and load data in Rigidbody
void ReadPDB(const std::string name,Rigidbody& protein ); ///< read a PDB file from a filename and load data in Rigidbody
void write_pdb(const Rigidbody& rigid, std::string filename); ///< write a PDB file given a Rigidbody and a filename

}

#endif //#ifndef PDBIO_H


