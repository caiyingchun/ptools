//
// C++ Interface: atomselection
//
// Description:
//
//

#ifndef ATOMSELECTION_H
#define ATOMSELECTION_H

#include "rigidbody.h"

namespace PTools {


class AtomSelection{

private:
    //private data
    const Rigidbody* m_rigid;
    std::vector<int> m_list;

    //private methods



public:
    AtomSelection(){};
    AtomSelection(const AtomSelection& oldsel);
    AtomSelection(const Rigidbody& rigid); ///< translate a Rigidbody object into an AtomSelection
    ~AtomSelection();

    uint Size() const {return m_list.size();}; ///< returns the size of the selection
    void SetRigid(const Rigidbody& rig) {m_rigid=&rig;};

    /// return the i-th atom of the list
    Atom operator[] (uint i) const {
          if (i>=this->Size()) throw std::range_error("AtomSelection: array out of bounds");
          return m_rigid->copy_atom(m_list[i]);}; 

    Atom copy_atom(uint i) const {return m_rigid->copy_atom(m_list[i]);}
    void add_atomIndex(int i) {m_list.push_back(i);}; ///< adds an Atom index
    Rigidbody create_rigid(); ///< makes a new rigid copy (independant copy) from an AtomsSelection object.

    AtomSelection non(const AtomSelection& atsel);


    //friends:
    friend AtomSelection operator& (const AtomSelection& atsel1,const  AtomSelection& atsel2);
    friend AtomSelection operator| (const AtomSelection& atsel1,const AtomSelection& atsel2);
    friend AtomSelection operator! (const AtomSelection& seltoinverse);
    friend AtomSelection op_not (const AtomSelection& seltoinverse);
};


AtomSelection operator& (const AtomSelection& atsel1,const  AtomSelection& atsel2);
AtomSelection operator| (const AtomSelection& atsel1,const AtomSelection& atsel2);
AtomSelection operator! (const AtomSelection& seltoinverse);

inline AtomSelection op_not (const AtomSelection& seltoinverse) {return !seltoinverse;};

}

#endif // ATOMSELECTION_H
