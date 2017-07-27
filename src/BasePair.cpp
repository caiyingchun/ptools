#include <iostream>
#include <stdexcept>


#include <rigidbody.h>
#include <pdbio.h>
#include <BasePair.h>
#include <Movement.h>

#include "atomselection.h"

using namespace std;
using namespace PTools;


BasePair::BasePair(std::string filename)
{
  cout << "opening : " << filename << endl;
  ReadPDB(filename,rigbody);
  this->type = rigbody.get_atom_property(0).residType;
}


BasePair::BasePair(const Rigidbody& rigbody)
{
  if (rigbody.Size()==0)
  {
    throw std::runtime_error("cannot initialize a BasePair with an empty Rigidbody");
  }
  this->rigbody=rigbody;
  this->type = rigbody.get_atom_property(0).residType;
}

string BasePair::print_pdb()const
{
  return rigbody.print_pdb ();
}

std::string BasePair::print_pdbofBase(std::string chain) 
{
    return rigbody.SelectChainId(chain).create_rigid().print_pdb();
}

void BasePair::SetChainID(){
  unsigned int rigSize=rigbody.Size();
  for(unsigned int i =0; i< rigSize ; i++)
  {
    Atomproperty ap=rigbody.get_atom_property(i);
    if (ap.residType == type)
    {
        ap.chainId = "A";
    }
    else
    {
        ap.chainId = "B";
    }
    rigbody.SetAtomProperty(i,ap);
  }
}

void BasePair::apply( const Movement& m)
{
  m.apply(rigbody);
}


void BasePair::apply(const Matrix& m)
{
  apply(Movement (m));
}

Matrix BasePair::get_matrix() const
{
  return rigbody.get_matrix();
}


Movement BasePair::GetMovement()const
{
  return Movement(get_matrix());
}


Rigidbody BasePair::get_rigid()const
{
  return rigbody;
}


Rigidbody BasePair::get_rigidOfBase(std::string chain)
{
  return rigbody.SelectChainId(chain).create_rigid();
}


void BasePair::SetResID(int idA,int idB)
{
  unsigned int baseSize=rigbody.Size();
  for(unsigned int i =0; i< baseSize ; i++)
  {
    Atomproperty ap=rigbody.get_atom_property(i);
    if (ap.chainId == "A")
    {
        ap.residId = idA;
    }
    else
    {
        ap.residId = idB;
    }     
    rigbody.SetAtomProperty(i,ap);
  }
}

uint BasePair::SetAtomNumberOfBase(std::string chain,int num)
{
  unsigned int baseSize=rigbody.Size();
  for(unsigned int i =0; i< baseSize ; i++)
  {
    Atomproperty ap=rigbody.get_atom_property(i);
    if (ap.chainId == chain)
    {
        ap.atomId = num;
        num++;
        rigbody.SetAtomProperty(i,ap);
    }
  }
  return num;
}

uint BasePair::GetResIDofBase(std::string chain)
{
  Atomproperty ap = rigbody.SelectChainId(chain).create_rigid().get_atom_property(0);
  return ap.residId;
}


void  BasePair::SetRigidBody(const Rigidbody& rigbody)
{
  this->rigbody=rigbody;
}

string BasePair::get_type() const {
    return type;
}

void BasePair::SetType(string type) {
    this->type = type;
}
//end namespace
