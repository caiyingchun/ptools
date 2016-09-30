/* 
 * File:   Parameter.h
 * Author: boyer
 *
 * Created on March 22, 2010, 11:55 PM
 */

#ifndef _PARAMETER_H
#define	_PARAMETER_H

#include "BasePair.h"
#include "Movement.h"


/*! \brief
* a class to compute and hold the parameter between two base pairs
*/
namespace PTools
{

  class Parameter
  {
    public:
        Parameter();
        Parameter(const BasePair& bp1, const BasePair& bp2);
        ~Parameter();
        Rigidbody BuildAxisCentered( Rigidbody& bp);
        Rigidbody BuildAxisCGGeometricCenter( Rigidbody& bp);
        Rigidbody BuildAxisAAGeometricCenter( Rigidbody& bp);

        void MeasureParameters(const Rigidbody& oxyz1, const Rigidbody& oxyz2);

        Movement GetMov() const;

        //return the parameter in the following order, twist roll tilt rise slide shift. beware, the angle are in radian
        std::string ToString ()const;
        //return the parameter in the following order, twist roll tilt rise slide shift in readable arrangement
        std::string ToFormatedString ()const;
        
        double GetRise() const ;
        void SetRise(double rise) ;

        double GetRoll() const ;
        void SetRoll(double roll);

        double GetShift() const ;
        void SetShift(double shift);

        double GetSlide() const ;
        void SetSlide(double slide);

        double GetTilt() const ;
        void SetTilt(double tilt);

        double GetTwist() const ;
        void SetTwist(double twist) ;

        


    private:
    //atribut
        double shift;
	double slide;
	double rise;
	double tilt;
	double roll;
	double twist;
    //method
        
  };
  
}//end namespace

#endif	/* _PARAMETER_H */

