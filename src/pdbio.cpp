#include <algorithm>
#include <cctype>
#include <iostream>
#include <fstream>
#include <istream>

#include "atom.h"
#include "stdio.h"
#include "pdbio.h"

using namespace std;

namespace PTools{


std::string strip( std::string const& str, char const* sepSet ) {
    std::string::size_type const first = str.find_first_not_of(sepSet);
    return ( first==std::string::npos )
           ? std::string()
           : str.substr(first, str.find_last_not_of(sepSet)-first+1);
}


bool isAtom(const std::string & line ) {
    //cout << ligne.size()<< endl ;
    if (line.size()<10 ) return false;

    if (line.substr(0,6)==(std::string) "ATOM  " ) return true ;
    return false;
}


bool isHeteroAtom(const std::string& line) {
    if (line.size()<10) return false;

    if (line.substr(0,6) == "HETATM") return true;
    return false;
}




std::string readatomtype(const std::string &ligne) {
    std::string type="" ;
    int i=12 ;
    while (ligne[i]==' ')
    {
        i++;
        if (i>15) return type ;
    }

    int j=i ;
    while (ligne[j]!=' ') j++ ;

    type=ligne.substr(i,j-i) ;
    std::transform(type.begin(),type.end(),
                   type.begin(), //destination
                   (int(*)(int)) toupper //to upper: convert to upper case
                  );

    //cout << type <<"a" ;



    return type;
}


std::string readresidtype(const std::string &ligne) {
    std::string type="" ;
    int i=17 ;
    while (ligne[i]==' ')
    {
        i++;
        if (i>19) return type ;
    }

    int j=i ;
    while (ligne[j]!=' ') j++ ;

    type=ligne.substr(i,j-i) ;
    std::transform(type.begin(),type.end(),
                   type.begin(), //destination
                   (int(*)(int)) toupper //to upper: convert to upper case
                  );

    //cout << type <<"a" ;



    return type;
}



/**
 * returns Coord3D from a PDB-like string
 */
Coord3D pdbToCoords(const std::string & line)
{
 double x,y,z;
 std::string sx,sy,sz;
 
 sx=line.substr(30,8);
 sy=line.substr(38,8);
 sz=line.substr(46,8);
 
 x=atof(sx.c_str());
 y=atof(sy.c_str());
 z=atof(sz.c_str());
 
 return Coord3D(x,y,z);
 
    
}


/**
 * Set Atomproperty from a PDB-like string
 * 
 */
void pdbToAtomproperty(const std::string & line, Atomproperty& atp)
{
    
    atp.atomType = readatomtype(line);
    atp._pdbAtomType = line.substr(12,4);
    
    
    atp.residType = readresidtype(line);
    std::string chainID = line.substr(21,1);
    if (chainID == " ") chainID = "";
    atp.chainId = chainID;
    atp.residId = atoi(line.substr(22,4).c_str());
    atp.atomId = atoi(line.substr(6,5).c_str());
    std::string extra = line.substr(54); //extracts everything after the position 54 to the end of line
    atp.extra = extra ;

}



/** 
 * parses a PDB-formatted string and updates the given Atom instance
 * 
 */
void readAtom(const std::string& line, Atom& at)
{

    if (isAtom(line))
        {
            pdbToAtomproperty(line, at);
            at.coords = pdbToCoords(line);
             
            return;
        }
        
    throw std::runtime_error("in pdbio.readAtom(): input is not an atom\n");
    
}



void ReadPDB(istream& file, Rigidbody& protein) {

    std::string line ;

    while ( std::getline(file, line))
    {
        if (isAtom(line))
        {
            
            Coord3D pos = pdbToCoords(line);
            Atomproperty a;
            pdbToAtomproperty(line, a);
            protein.add_atom(a,pos);

        }
    }
}



void ReadPDB(const std::string name,Rigidbody& protein ) {
    std::string nomfich=name ;
	// pointer toward the filename given in the constructor argument
    ifstream file(nomfich.c_str()); 
    if (!file)
    {
        std::ostringstream oss;
        throw std::invalid_argument("##### ReadPDB:Could not open file \"" + nomfich + "\" #####") ;
    }
    ReadPDB(file, protein);
    file.close();
    return;

}

void write_pdb(const Rigidbody& rigid, std::string filename)
{

    FILE* file= fopen(filename.c_str(),"w") ;

    for (uint i=0; i<rigid.size();i++)
    {

        const char * chainID="A" ;

        Atom at = rigid.copy_atom(i);
        const char* atomname=at._pdbAtomType.c_str();
        const char* residName=at.residType.c_str();
        int residnumber = at.residId;
        chainID = at.chainId.c_str();

        int atomnumber = at.atomId;

        Coord3D coord = at.coords;
        dbl x = coord.x;
        dbl y = coord.y;
        dbl z = coord.z ;

        fprintf(file, "ATOM  %5d %-4s %3s %1s%4d    %8.3f%8.3f%8.3f%s", atomnumber,atomname,residName,chainID,residnumber,real(x),real(y),real(z),at.extra.c_str());
        

        fprintf(file,"\n");
    }

    fclose(file);
}

} //namespace PTools



