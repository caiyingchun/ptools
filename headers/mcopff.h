//  multicopy-forcefield
//
//



#ifndef _MCOPFF_H_
#define _MCOPFF_H_

#include "attractforcefield.h"
#include "rigidbody.h"

namespace PTools{


// typedef std::vector<AttractRigidbody> ensemble ;


class Region
{
private:

std::vector<AttractRigidbody> _copies;

public:
/*
   void euler_rotate(const dbl& phi, const dbl& ssi, const dbl& rot)
   {
      for (uint i=0; i<_copies.size(); i++)
      {
          _copies[i].euler_rotate(phi, ssi, rot);
      }

   };

   void translate(const Coord3D& co)
   {
       for(uint i =0; i< _copies.size(); ++i)
       {
          _copies[i].translate(co);
       }
   }*/


   void addCopy(const AttractRigidbody& cop){_copies.push_back(cop);};

   size_t size() const {return _copies.size();};


   AttractRigidbody& operator[](uint i){return _copies[i];};

};




class Mcoprigid //multicopy rigidbody
{

public:

    Mcoprigid();

    //using default copy operator

    void setMain(AttractRigidbody& main) ;
    void addEnsemble(const Region& reg){ _vregion.push_back(reg); std::vector<dbl> v; _weights.push_back(v);  };


    void euler_rotate(const dbl& phi, const dbl& ssi, const dbl& rot);
    void translate(const Coord3D& c);


    void PrintWeights();
    std::vector <std::vector<dbl> > getWeights(){return _weights;};


private:

    AttractRigidbody _main;
    std::vector< Region > _vregion ;

    bool _complete ;
    Coord3D _center ; ///<center of mass of the main region

    std::vector< std::vector <dbl> > _weights;

    friend class McopForceField;

};



/** \brief ForceField with multicopy
needs an attract forcefield (either 1 or 2) in constructor

no normal modes yet
*/
class McopForceField: public ForceField
{

public:

    McopForceField(BaseAttractForceField& ff, dbl cutoff)
            :_ff(ff), _cutoff(cutoff) {};


    dbl Function(const Vdouble&);
    void Derivatives(const Vdouble& v, Vdouble & g );


    void setReceptor(const Mcoprigid& rec) {_receptor = rec;};
    void setLigand(const Mcoprigid& lig) { _centered_ligand = lig;  };

    void calculate_weights(Mcoprigid& lig, bool print=false);

    uint Problemsize() {return 6;};
    void initMinimization(){};

private:

    BaseAttractForceField& _ff ;
    dbl _cutoff;

    bool _update_weights;

    Mcoprigid _centered_ligand ;
    Mcoprigid _moved_ligand ;
    Mcoprigid _receptor;


    


};

}//namespace PTools

#endif // _MCOPFF_H_



