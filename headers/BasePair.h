
#ifndef BASE_PAIR_H
#define BASE_PAIR_H

#include <vector>  
#include <Movement.h>

#include "rigidbody.h"

/*! \brief Rigidbody use by the DNA object
*
*/
namespace PTools
{
  
  class BasePair 
  {
    public:
    ///initialize a new object with a file
    BasePair(std::string filename);
    ///initialize a new object from a regular Rigidbody
    BasePair(const Rigidbody& rigbody);
    virtual ~BasePair() {}
    
    ///return a string containing the atoms data following the PDB format 
    std::string PrintPDB() const;

    ///return a string containing the atoms data of a base (identified by its chain) following the PDB format
    std::string PrintPDBofBase(std::string chain) ;

    ///change the chainID of the internal bases to 'A' for the first base (coresponding to the type) and 'B' for the second one
    void SetChainID();

    /// apply a Movement to the BasePair 
    void apply(const Movement& );
    /// apply a Matrix to the BasePair
    void apply(const Matrix&);
    
    /// return the Matrix of the BasePair
    Matrix get_matrix()const;
    
    /// return the Movemeny of the BasePair
    Movement GetMovement()const;
    
    /// return the Rigidbody of the BasePair
    Rigidbody get_rigid()const;
    /// return the Rigidbody of the specified base (by chain)
    Rigidbody get_rigidOfBase(std::string chain);
    /// define the Rigidbody of the BasePair
    void SetRigidBody(const Rigidbody&);
    
    /// return the Residue ID of the specified base (by chain)
    uint GetResIDofBase(std::string chain);
    /// change the ID of res to idA for base on strand A and idB for the one on strand B
    void SetResID(int idA,int idB);
    /// change the atoms numbers of the specified base (by chain) starting at startnum and returning the last atom number
    uint SetAtomNumberOfBase(std::string chain,int);

    
    std::string get_type() const;

    void SetType(std::string type);
    
    
    ///return the number of Atom
    unsigned int Size() const { return rigbody.Size(); }

    /// return the i-th Atom of the basePair
    Atom operator[] (uint i) const {
          if (i>=this->Size()) throw std::range_error("DNA: array out of bounds");
          return rigbody.copy_atom(i);};

    private:
    //atribut
    Rigidbody rigbody;
    std::string type;
    
  };
  
}



#endif // BASE_PAIR_H 