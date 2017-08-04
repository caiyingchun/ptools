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
  if (rigbody.size()==0)
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
    return rigbody.select_chainid(chain).create_rigid().print_pdb();
}

void BasePair::SetChainID(){
  unsigned int rigsize=rigbody.size();
  for(unsigned int i =0; i< rigsize ; i++)
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
    rigbody.set_atom_property(i,ap);
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
  return rigbody.select_chainid(chain).create_rigid();
}


void BasePair::SetResID(int idA,int idB)
{
  unsigned int basesize=rigbody.size();
  for(unsigned int i =0; i< basesize ; i++)
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
    rigbody.set_atom_property(i,ap);
  }
}

uint BasePair::set_atomNumberOfBase(std::string chain,int num)
{
  unsigned int basesize=rigbody.size();
  for(unsigned int i =0; i< basesize ; i++)
  {
    Atomproperty ap=rigbody.get_atom_property(i);
    if (ap.chainId == chain)
    {
        ap.atomId = num;
        num++;
        rigbody.set_atom_property(i,ap);
    }
  }
  return num;
}

uint BasePair::GetResIDofBase(std::string chain)
{
  Atomproperty ap = rigbody.select_chainid(chain).create_rigid().get_atom_property(0);
  return ap.residId;
}


void  BasePair::set_rigidBody(const Rigidbody& rigbody)
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
