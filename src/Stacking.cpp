
#include <geometry.h>
#include <rigidbody.h>
#include <iostream>
#include <Movement.h>
#include <BasePair.h>
#include <Stacking.h>
#include <atomselection.h>
using namespace std;


namespace PTools
{

Stacking::Stacking()
{

}

Stacking::~Stacking()
{

}



Rigidbody Stacking::Axis( Rigidbody& bp1,  Rigidbody& bp2)
{
    //1 determine if the considered basePair is a G-C or a A-T
    bool bp1isGC = bp1.SelectAtomType("GG1").Size()>0;
    bool bp2isGC = bp2.SelectAtomType("GG1").Size()>0;

    //2 build rigidbody for pyrimidine

    Rigidbody pyrBp1;
    if (bp1isGC)
    {
        pyrBp1 = bp1.SelectAtomType("GC1").CreateRigid() + bp1.SelectAtomType("GC2").CreateRigid();
    }
    else
    {
        pyrBp1 = bp1.SelectAtomType("GT1").CreateRigid() + bp1.SelectAtomType("GT2").CreateRigid();
    }

    Rigidbody pyrBp2;
    if (bp2isGC)
    {
        pyrBp2 = bp2.SelectAtomType("GC1").CreateRigid() + bp2.SelectAtomType("GC2").CreateRigid();
    }
    else
    {
        pyrBp2 = bp2.SelectAtomType("GT1").CreateRigid() + bp2.SelectAtomType("GT2").CreateRigid();
    }

    //3 build rigidbody for purine
    Rigidbody purBp1;
     if (bp1isGC)
    {
        purBp1 = bp1.SelectAtomType("GG1").CreateRigid() + bp1.SelectAtomType("GG2").CreateRigid() + bp1.SelectAtomType("GG3").CreateRigid();
    }
    else
    {
        purBp1 = bp1.SelectAtomType("GA1").CreateRigid() + bp1.SelectAtomType("GA2").CreateRigid() + bp1.SelectAtomType("GA3").CreateRigid();
    }

    Rigidbody purBp2;
    if (bp2isGC)
    {
        purBp2 = bp2.SelectAtomType("GG1").CreateRigid() + bp2.SelectAtomType("GG2").CreateRigid() + bp2.SelectAtomType("GG3").CreateRigid();
    }
    else
    {
        purBp2 = bp2.SelectAtomType("GA1").CreateRigid() + bp2.SelectAtomType("GA2").CreateRigid() + bp2.SelectAtomType("GA3").CreateRigid();
    }

    //4 compute center
    Coord3D pyrBp1center = pyrBp1.FindCenter() ;
    Coord3D pyrBp2center = pyrBp2.FindCenter() ;
    Coord3D purBp1center = purBp1.FindCenter() ;
    Coord3D purBp2center = purBp2.FindCenter() ;

    Rigidbody axis;
    
    if(  Norm(pyrBp1center-pyrBp2center) < Norm(pyrBp1center-purBp2center) )
    {
       axis = AxisPyrimidine( pyrBp1, pyrBp1center, pyrBp2center );
    }
    else
    {
       axis = AxisPyrimidine( pyrBp1, pyrBp1center, purBp2center );
    }

    axis = axis + AxisPurine(purBp1,purBp1center);
 


    return axis;

}

Rigidbody Stacking::Axis( Rigidbody& basePair)
{
    //1 determine if the considered basePair is a G-C or a A-T
    bool basePairIsGC = basePair.SelectAtomType("GG1").Size()>0;

    //2 build rigidbody for pyrimidine

    Rigidbody pyrBp;
    if (basePairIsGC)
    {
        pyrBp = basePair.SelectAtomType("GC1").CreateRigid() + basePair.SelectAtomType("GC2").CreateRigid();
    }
    else
    {
        pyrBp = basePair.SelectAtomType("GT1").CreateRigid() + basePair.SelectAtomType("GT2").CreateRigid();
    }

    //3 build rigidbody for purine
    Rigidbody purBp;
     if (basePairIsGC)
    {
        purBp = basePair.SelectAtomType("GG1").CreateRigid() + basePair.SelectAtomType("GG2").CreateRigid() + basePair.SelectAtomType("GG3").CreateRigid();
    }
    else
    {
        purBp = basePair.SelectAtomType("GA1").CreateRigid() + basePair.SelectAtomType("GA2").CreateRigid() + basePair.SelectAtomType("GA3").CreateRigid();
    }



    //4 compute center
    Coord3D pyrBp1center = pyrBp.FindCenter() ;
    Coord3D purBp1center = purBp.FindCenter() ;

    Rigidbody axis;


    axis = axis + AxisPurine(purBp,purBp1center);
    axis = axis + AxisPyrimidineCopyPurine(pyrBp1center, axis);


    return axis;

}

Rigidbody Stacking::AxisPyrimidine(const Rigidbody& pyr, const Coord3D& centerBase1, const Coord3D&  centerBase2)const
{
    //build pyr axis
    //1 get the projection of the center of the first base on the line defines
    //by the center of the second base and the vector of the first base.
    Coord3D vectorBp1Bp2 = centerBase1 - centerBase2;
    Coord3D vectorBp1pyr2 = (pyr.CopyAtom(1).coords - centerBase1).Normalize();

    double proj=ScalProd(vectorBp1Bp2,vectorBp1pyr2);

    //2 project the center of the second base to the correct place.
    Coord3D N = centerBase2 + vectorBp1pyr2 * proj;

    //3 normalise
    Coord3D topOfAxis = (N - centerBase1).Normalize();
    
    //4 build the Axis for Pyrimidines
    Rigidbody pyrAxis;
    pyrAxis.AddAtom(Atomproperty(),centerBase1);
    pyrAxis.AddAtom(Atomproperty(),centerBase1+topOfAxis);


    return pyrAxis;
}

Rigidbody Stacking::AxisPyrimidineCopyPurine( const Coord3D& centerBase1, const Rigidbody& axisPurine )const
{
    Coord3D vectorPlanPur = axisPurine.GetCoords(1)-axisPurine.GetCoords(0);
    
    Rigidbody pyrAxis;
    pyrAxis.AddAtom(Atomproperty(),centerBase1);
    pyrAxis.AddAtom(Atomproperty(),centerBase1+vectorPlanPur);
    return pyrAxis;
}

Rigidbody Stacking::AxisPurine(const Rigidbody& pur, const Coord3D& center)const
{
    //1 define two vector of the plan (check the chain to assure a clockwise order)
    Coord3D vectorPlan1 ;
    Coord3D vectorPlan2 ;
    if (pur.GetAtomProperty(0).chainId=="A"){
        vectorPlan1 = pur.GetCoords(1)-center;
        vectorPlan2 = pur.GetCoords(0)-center;
    }
    else
    {
        vectorPlan1 = pur.GetCoords(0)-center;
        vectorPlan2 = pur.GetCoords(1)-center;
    }

    //2 find orthogonal vector to defined plan
    Coord3D topOfAxis;
    VectProd(vectorPlan1.Normalize(), vectorPlan2.Normalize(), topOfAxis);
    topOfAxis = topOfAxis.Normalize();
    //3 build the Axis for Purine
    Rigidbody purAxis;
    purAxis.AddAtom(Atomproperty(),center);
    purAxis.AddAtom(Atomproperty(),center+topOfAxis);

    return purAxis;
}

bool Stacking::IsStacked(const Rigidbody& axe1, const Rigidbody& axe2,double angleThreshold,double overlapThreshold)const
{
    Coord3D vector1 =axe1.GetCoords(1)-axe1.GetCoords(0);
    Coord3D vector2 =axe2.GetCoords(1)-axe2.GetCoords(0);
    Coord3D vectorD =(axe2.GetCoords(0)-axe1.GetCoords(0)).Normalize();
//    cerr <<acos(ScalProd(vector1,vector2)) <<endl;
//    cerr <<acos(ScalProd(vector1,vectorD)) <<endl;

    return ((acos(ScalProd(vector1,vector2))<angleThreshold) && (acos(ScalProd(vector1,vectorD)) < overlapThreshold));

}



}