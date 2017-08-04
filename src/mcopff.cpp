#include "mcopff.h"
#include <cassert>


namespace PTools
{


Mcoprigid::Mcoprigid()
{
    _complete = false;

};




void Mcoprigid::setMain(AttractRigidbody& main) {
    _main=main;
    _center = _main.find_center();

};


void Mcoprigid::euler_rotate(const dbl& phi, const dbl& ssi, const dbl& rot)
{
//Warning: makes euler rotation without centering
//the Mcoprigid object must be centered


//rotates the main body:
    _main.euler_rotate(phi, ssi, rot);


//for each multicopy region, rotates the copy:
    for (uint i=0; i < _vregion.size(); i++)
        for (uint j=0; j<_vregion[i].size(); j++)
            _vregion[i][j].euler_rotate(phi, ssi, rot);

}


void Mcoprigid::translate(const Coord3D& c)
{
//translates the main body:
    _main.translate(c);

//for each multicopy region, translates the copy:
    for (uint i=0; i < _vregion.size(); i++)
        for (uint j=0; j<_vregion[i].size(); j++)
            _vregion[i][j].translate(c);

}



void Mcoprigid::PrintWeights()
{
    for (uint loopregion=0; loopregion<_weights.size(); loopregion++)
    {
        std::cout << "copy region: " << loopregion << std::endl << "weights: ";
        for (uint copy=0; copy<_weights[loopregion].size(); copy++)
        {
            std::cout << _weights[loopregion][copy] << "  " ;
        }

    }
}





///////////////////////////////////////////////////
//     Forcefield implementation
///////////////////////////////////////////////////



void McopForceField::calculate_weights(Mcoprigid& lig, bool print)
{


//loop over copies regions
    for (uint loopregion=0; loopregion < _receptor._vregion.size() ; loopregion++)
    {
        if (print)
          {
             std::cout << " Region: " << loopregion << "\n";
          }

        //calculates interaction energy between receptor copies and ligand body:
        std::vector<dbl> Eik;

        for (uint copy = 0; copy < _receptor._vregion[loopregion].size(); copy++)
        {
            AttractPairList cpl ( lig._main, _receptor._vregion[loopregion][copy], _cutoff );
            dbl e = _ff.nonbon8( lig._main, _receptor._vregion[loopregion][copy] , cpl );
            Eik.push_back(e);
        }



        const dbl RT = 0.592 * 298.0 ;

        //calculate weights
        dbl sumweights = 0.0;
        std::vector<dbl> weights;

        for (uint i=0; i<Eik.size(); i++)
        {
            dbl e = exp( -Eik[i]/RT) ;
            weights.push_back( e )  ;
            sumweights += e ;
        }

        //normalize weights

        for (uint i=0; i< weights.size(); i++)
        {
            weights[i] = weights[i]/sumweights ;
            if (print) std::cout << "copy " << i << "  weight: " << weights[i] << std::endl; 
        }

        _receptor._weights[loopregion]=weights;




    }



}





/** \brief calculates energy of the system
*
* this functions returns nonbonded energy of a receptor with multicopy and a ligand without copy.
*
*/
dbl McopForceField::Function(const Vdouble & v)
{

    dbl ener = 0.0 ;
    dbl enercopy =0.0;

// 1) put the objects to the right place

    _moved_ligand = _centered_ligand;

    Mcoprigid & lig = _moved_ligand ;
    assert(lig._vregion.size()==0);


    lig.euler_rotate(v[0],v[1],v[2]);
    lig.translate(Coord3D(v[3],v[4],v[5]));


//2) calculates the energy


    //2.1) main ligand body with main receptor

    AttractPairList pl (_receptor._main,   lig._main, _cutoff );
    ener += _ff.nonbon8(_receptor._main, lig._main, pl );


    //2.2) main lignd with receptor copies:
    assert(_receptor._vregion.size() == _receptor._weights.size());
        
    for (uint loopregion=0; loopregion < _receptor._vregion.size() ; loopregion++)
    {

        //calculates interaction energy between receptor copies and ligand body:
//         std::vector<dbl> Eik;


        Region& ref_ensemble = _receptor._vregion[loopregion];
        std::vector<dbl>& ref_weights = _receptor._weights[loopregion];

        assert( ref_ensemble.size() == ref_weights.size());

        for (uint copynb = 0; copynb < ref_ensemble.size(); copynb++)
        {

            dbl& weight = ref_weights[copynb];
            AttractRigidbody& copy = ref_ensemble[copynb];

            AttractPairList cpl ( lig._main, copy, _cutoff );
            std::vector<Coord3D> copyforce(copy.size());
            std::vector<Coord3D> mainforce(lig._main.size());

//             dbl e = _ff.nonbon8( lig._main, _receptor._vregion[loopregion][copy] , cpl );
            dbl e = _ff.nonbon8_forces(lig._main, copy, cpl, mainforce, copyforce);
            enercopy += e * weight;//lig._weights[loopregion][copy];

            //multiply forces by copy weight:
            for(uint i=0; i<copyforce.size(); i++)
            { copyforce[i] = weight*copyforce[i]; }
            for(uint i=0; i<mainforce.size(); i++)
            { mainforce[i] = weight*mainforce[i]; }

            //add force to main ligand and receptor copy
            assert(lig._main.size() == mainforce.size());
            for (uint i=0; i<lig._main.size(); i++)
               lig._main.m_forces[i]+=mainforce[i];

            assert(copy.size()==copyforce.size());
            for(uint i=0; i<copyforce.size(); i++)
               copy.m_forces[i]+=copyforce[i];


        }


    }

    return ener + enercopy;

}


void McopForceField::Derivatives(const Vdouble& v, Vdouble & g )
{

//sum the forces over x, y and z:

Coord3D ligtransForces; //translational forces for the ligand:
for(uint i=0; i<_moved_ligand._main.size(); i++)
 {
     ligtransForces += _moved_ligand._main.m_forces[i];
 }


Coord3D receptortransForces;
for(uint i=0; i<_receptor._main.size(); i++)
{
receptortransForces+= _receptor._main.m_forces[i];
}


for (uint i=0; i <_receptor._vregion.size(); i++)
 {
   Region& ens = _receptor._vregion[i];
   std::vector<dbl> & weights =  _receptor._weights[i];

   for(uint j=0; j<ens.size(); j++)
   {
     AttractRigidbody& copy = ens[j];
       for (uint atomnb=0; atomnb < copy.size(); ++atomnb)
       {
            receptortransForces += weights[j] * copy.m_forces[atomnb];
       }

   }

//TODO DEBUG:
std::cout << "differences between the two forces: " <<  (ligtransForces - receptortransForces).to_string() << std::endl ;

 }





}





} // namespace PTools
