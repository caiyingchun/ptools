#ifndef PAIRLIST_H
#define PAIRLIST_H

#include "attractrigidbody.h"


#include <vector>


namespace PTools
{


struct AtomPair
{
    int atlig;
    int atrec;
};



/*! \brief Contains list of pairs of atoms in interaction
*
*
*/

class AttractPairList
{
public:
    AttractPairList(const AttractRigidbody & receptor, const AttractRigidbody & ligand, dbl cutoff );
    AttractPairList(const AttractRigidbody & receptor,const AttractRigidbody &  ligand); ///< constructor with infinite cutoff ;
    AttractPairList(){}; //null constructor for use with std::vector

    ~AttractPairList();

    ///update pairlist
    void update();

    ///< add a pair and checks if correct ligand and receptor are provided
    void addPair(const AttractRigidbody& ligand, const AttractRigidbody& receptor, const AtomPair& pair) ;

    ///return the current cutoff
    dbl GetCutoff() {
        return sqrt(squarecutoff);
    };

    ///return number of pairs of atoms in interaction (distance <= cutoff)
    uint Size() {
        return vectl.size();
    };

    /// get atom pair number i of the pairlist
    AtomPair operator[](int i) {
        AtomPair pair;
        pair.atlig=vectl[i];
        pair.atrec=vectr[i];
        return pair;
    };


private:

    dbl squarecutoff ; ///< cutoff^2
    const AttractRigidbody* mp_ligand;
    const AttractRigidbody* mp_receptor;

    bool no_update; ///< if true the pairlist is never updated

    std::vector <int> vectl ; ///< index of ligands atoms
    std::vector <int> vectr ; ///< index of receptor atoms

};




}//namespace PTools

#endif

