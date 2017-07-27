#include "pairlist.h"

namespace PTools
{


AttractPairList::AttractPairList(const AttractRigidbody & receptor , const AttractRigidbody & ligand, dbl cutoff )
{
    mp_ligand = &ligand;
    mp_receptor = &receptor;
    squarecutoff = cutoff*cutoff;
    no_update = false;
    update();
}




AttractPairList::AttractPairList(const AttractRigidbody & receptor, const AttractRigidbody & ligand)
{

    mp_ligand = &ligand;
    mp_receptor = &receptor;
    no_update = true ; //if infinite cutoff

    for (uint i = 0 ; i < mp_ligand->Size(); i++)
        for (uint j = 0; j < mp_receptor->Size(); j++)
        {
            vectl.push_back(i);
            vectr.push_back(j);
        }

}

AttractPairList::~AttractPairList()
{

}


/**
   Very basic implementation of an atom pairlist.
*/
void AttractPairList::update()
{


    if (no_update) return ;
    vectl.clear(); // clears the pairlist
    vectr.clear();

    //basic implementation of a pairlist generation:

    std::vector<uint> activelig;
    std::vector<uint> activerec;

    for (uint i=0; i<mp_ligand->Size(); i++)
    {
        if (mp_ligand->isAtomActive(i))
        {
            activelig.push_back(i);
        }
    }

    for (uint i=0; i<mp_receptor->Size(); i++)
    {
        if (mp_receptor->isAtomActive(i))
        {
            activerec.push_back(i);
        }
    }

    uint activeligsize = activelig.size();
    uint activerecsize = activerec.size();


    for (uint ii = 0 ; ii < activeligsize ; ii++)
    {

        for (uint jj = 0; jj < activerecsize; jj++)
        {
            uint i=activelig[ii];
            uint j=activerec[jj];


            Coord3D c1 = mp_ligand->get_coords(i) ;
            Coord3D c2 = mp_receptor->get_coords(j);
            if (Norm2(c1-c2) <= squarecutoff)
            {
                vectl.push_back(i);
                vectr.push_back(j);
            }


        }
    }


}


void AttractPairList::addPair(const AttractRigidbody & ligand, const AttractRigidbody & receptor, const AtomPair& pair)
{
    if (&ligand==mp_ligand && &receptor==mp_receptor)
    {
        vectl.push_back(pair.atlig);
        vectr.push_back(pair.atrec);
    }
    else
    {
        std::cerr << "error in PairList::add() : wrong receptor or ligand " << std::endl;
        abort();
    }
};








} //namespace PTools



