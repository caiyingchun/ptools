/* 
 * File:   Stacking.h
 * Author: boyer
 *
 * Created on May 15, 2010, 5:12 AM
 */

#ifndef _STACKING_H
#define	_STACKING_H

#include "rigidbody.h"

namespace PTools {


class Stacking{

private:
    //private data


    //private methods
    Rigidbody AxisPyrimidine(const Rigidbody& pyr, const Coord3D& centerBase1, const Coord3D& centerBase2)const;
    Rigidbody AxisPyrimidineCopyPurine( const Coord3D& centerBase1, const Rigidbody& axisPurine )const;
    Rigidbody AxisPurine(const Rigidbody& pur, const Coord3D& center )const;

public:
    Stacking();
    ~Stacking();
    Rigidbody Axis( Rigidbody& bp1,  Rigidbody& bp2);
    Rigidbody Axis( Rigidbody& bp1);
    bool IsStacked(const Rigidbody& axe1, const Rigidbody& axe2,double angleThreshold,double overlapThreshold)const;
  
};

}

#endif	/* _STACKING_H */

