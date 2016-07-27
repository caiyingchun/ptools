#ifndef MOUVEMENT_H
#define MOUVEMENT_H

#include <string>  
#include "basetypes.h"
#include "geometry.h"
#include "rigidbody.h"  
  
namespace PTools
{
//base class movement--------------------------------------------------------  
/*! \brief an Object for describing movement to a BasePair
*the external mouvements are described by a Matrix
*/
  class Movement 
  {
    //atribut
    protected:
    Matrix m;
        
    public:
    Movement();
    explicit Movement(const Matrix& matrix);
    ~Movement();
    
    ///operator + : merge two Movements by multiplying the Matrix
    Movement operator+ (const Movement&) const;

    /// apply the Matrix to a Rigidbody
    void Apply(Rigidbody& rigbody)const;
    
    ///return the Matrix
    const Matrix& GetMatrix() const;
    
    ///print the Matrix
    void Print() const;

    /// Return a string representing the Movement' matrix.
    std::string toString() const;
  };
  
  //fonction pour les matrices, a relocaliser dans la partie ptools adapter
  ///Multiply two Matrix
  Matrix matrixMultiply(const Matrix& m1, const Matrix& m2);

  ///inverse a Matrix of dimension 4 by 4
  Matrix inverseMatrix44 (const Matrix& );

  ///inverse a Matrix representing a rotation and a translation 
  Matrix inverseTranformationMatrix(Matrix& );

  ///inverse a Matrix representing a rotation and a translation 
  Matrix inverseTranformationMatrixPlusPlus(Matrix &);

//child class-------------------------------------------------------- 
  /*! \brief translation on x (short axis)
  */
  class Shift: public Movement 
  {
    public:
    Shift(double);
    
  };

  /*! \brief translation on y (long axis)
  */
  class Slide: public Movement 
  {
    public:
    Slide(double);
    
  };
  
  /*! \brief translation on z (perpendicular axis)
  */
  class Rise: public Movement 
  {
    public:
    Rise(double);
    
  };
// rotation around Z, Y and then X -> order to respect

  /*! \brief rotation around z (perpendicular axis)
  */
  class Twist: public Movement
  {
    public:
    Twist(double);
  };

  /*! \brief rotation around y (long axis)
  */
  class Roll: public Movement
  {
    public:
    Roll(double);
  };

  /*! \brief rotation around x (short axis)
  */
  class Tilt: public Movement 
  {
    public:
    Tilt(double);
  };
  


  /*! \brief a mouvement describing the local parameter of a A dna
  *reference : S.Arnott, R.Chandrasekaran, D.L.Birdsall, A.G.W.Leslie and R.L.Ratliff, Nature 283, 743-746 (1980)
  */
  class ADNA: public Movement 
  {
    public:
    ADNA();
  };

  /*! \brief a mouvement describing the local parameter of a B dna
  *reference : S.Arnott, R.Chandrasekaran, D.L.Birdsall, A.G.W.Leslie and R.L.Ratliff, Nature 283, 743-746 (1980)
  */ 
  class BDNA: public Movement
  {
    public:
    BDNA();

  };
}//end namespace


#endif // MOUVEMENT_H 