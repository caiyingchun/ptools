
#include <iostream>
#include <Movement.h>

using namespace std;


namespace PTools {

const double RADIAN = 0.01745329251994329; //degree to radian conversion    
    
//base class movement--------------------------------------------------------
Movement::Movement()
{
  m= Matrix(4,4);
}


Movement::Movement(const Matrix& matrix)
{
  this->m=matrix;
}


Movement::~Movement()
{
  
}


void Movement::apply(Rigidbody& rigbody)const
{
  Matrix oldmouvement = rigbody.GetMatrix ();
  //rigbody.apply_matrix(inverseTranformationMatrixPlusPlus(oldmouvement));
  rigbody.apply_matrix(inverseMatrix44 (oldmouvement));
  rigbody.apply_matrix(matrixMultiply(oldmouvement,m));
}


const Matrix& Movement::GetMatrix() const
{
  return m;
}


Movement Movement::operator+ (const Movement& mov) const
{
  Matrix mat = mov.GetMatrix();
  return Movement(matrixMultiply(m,mat)); 
}


void Movement::Print() const
{
  m.Print();
}

std::string Movement::toString() const
{
    return m.str();
}

//functions for matrix (to displace to ptools)--------------------------------------------------------
Matrix matrixMultiply(const Matrix& m1, const Matrix& m2)
{
  double mat1[4][4];
  double mat2[4][4];
  double res44[4][4];
  
  //convert the Matrix to a two dimensional array of double  
  for(uint i=0; i<4;i++)
  {
    for(uint j=0;j<4;j++)
    {
      mat1[i][j]=m1(i,j);
      mat2[i][j]=m2(i,j);
    }
  }
  
  mat44xmat44(mat1,mat2,res44);
  Matrix mResult = Matrix (4,4);
  
  //convert back the result to matrice
  for(uint i=0; i<4;i++)
  {
    for(uint j=0;j<4;j++)
    {
      mResult(i,j)=res44[i][j];
    }
  }
  
  return mResult;
}


Matrix inverseTranformationMatrix(const Matrix & m)
{
  //1 the inverse of a translation matrix is the translation matrice with the oposite signs on each of the translation components.
  //2 the inverse of a rotation matrix is the rotation matrix's transpose.
  //3 the inverse of a matrix produt is the product of the inverse matrices ordered in reverse.
  
  //so the inverse of a transformation matrix is the product of the rotation matrix's transpose with the inverse of the translation matrix
  
  Matrix rotation = Matrix(4,4);

  rotation(0,0) = m(0,0); rotation(0,1) = m(1,0); rotation(0,2) = m(2,0); rotation(0,3) = 0;
  rotation(1,0) = m(0,1); rotation(1,1) = m(1,1); rotation(1,2) = m(2,1); rotation(1,3) = 0;
  rotation(2,0) = m(0,2); rotation(2,1) = m(1,2); rotation(2,2) = m(2,2); rotation(2,3) = 0;
  rotation(3,0) = 0;      rotation(3,1) = 0;      rotation(3,2) = 0;      rotation(3,3) = 1;
  
  Matrix translation = Matrix(4,4);
  
  translation(0,0) = 1; translation(0,1) = 0; translation(0,2) = 0; translation(0,3) = -m(0,3);
  translation(1,0) = 0; translation(1,1) = 1; translation(1,2) = 0; translation(1,3) = -m(1,3);
  translation(2,0) = 0; translation(2,1) = 0; translation(2,2) = 1; translation(2,3) = -m(2,3);
  translation(3,0) = 0; translation(3,1) = 0; translation(3,2) = 0; translation(3,3) = 1;
  
  
  return matrixMultiply( rotation, translation );
}


Matrix inverseTranformationMatrixPlusPlus(const Matrix& m)
{
  //1 the inverse of a translation matrix is the translation matrice with the oposite signs on each of the translation components.
  //2 the inverse of a rotation matrix is the rotation matrix's transpose.
  //3 the inverse of a matrix produt is the product of the inverse matrices ordered in reverse.
  
  //so the inverse of a transformation matrix is the product of the rotation matrix's transpose with the inverse of the translation matrix
  
  Matrix inv = Matrix(4,4);

  inv(0,0) = m(0,0); inv(0,1) = m(1,0); inv(0,2) = m(2,0); inv(0,3) = -(m(0,0)*m(0,3))-(m(1,0)*m(1,3))-(m(2,0)*m(2,3));
  inv(1,0) = m(0,1); inv(1,1) = m(1,1); inv(1,2) = m(2,1); inv(1,3) = -(m(0,1)*m(0,3))-(m(1,1)*m(1,3))-(m(2,1)*m(2,3));
  inv(2,0) = m(0,2); inv(2,1) = m(1,2); inv(2,2) = m(2,2); inv(2,3) = -(m(0,2)*m(0,3))-(m(1,2)*m(1,3))-(m(2,2)*m(2,3));
  inv(3,0) = 0;      inv(3,1) = 0;      inv(3,2) = 0;      inv(3,3) = 1;
      
  return  inv;
}



Matrix inverseMatrix44 (const Matrix&  a)
{ 
  Matrix inv = Matrix(4,4);
  
  double detA= 
  (a(0,0) * a(1,1) * a(2,2) * a(3,3))  +  (a(0,0) * a(1,2) * a(2,3) * a(3,1))  +  (a(0,0) * a(1,3) * a(2,1) * a(3,2)) +
  (a(0,1) * a(1,0) * a(2,3) * a(3,2))  +  (a(0,1) * a(1,2) * a(2,0) * a(3,3))  +  (a(0,1) * a(1,3) * a(2,2) * a(3,0)) +
  (a(0,2) * a(1,0) * a(2,1) * a(3,3))  +  (a(0,2) * a(1,1) * a(2,3) * a(3,0))  +  (a(0,2) * a(1,3) * a(2,0) * a(3,1)) +
  (a(0,3) * a(1,0) * a(2,2) * a(3,1))  +  (a(0,3) * a(1,1) * a(2,0) * a(3,2))  +  (a(0,3) * a(1,2) * a(2,1) * a(3,0)) - 
  (a(0,0) * a(1,1) * a(2,3) * a(3,2))  -  (a(0,0) * a(1,2) * a(2,1) * a(3,3))  -  (a(0,0) * a(1,3) * a(2,2) * a(3,1)) - 
  (a(0,1) * a(1,0) * a(2,2) * a(3,3))  -  (a(0,1) * a(1,2) * a(2,3) * a(3,0))  -  (a(0,1) * a(1,3) * a(2,0) * a(3,2)) - 
  (a(0,2) * a(1,0) * a(2,3) * a(3,1))  -  (a(0,2) * a(1,1) * a(2,0) * a(3,3))  -  (a(0,2) * a(1,3) * a(2,1) * a(3,0)) - 
  (a(0,3) * a(1,0) * a(2,1) * a(3,2))  -  (a(0,3) * a(1,1) * a(2,2) * a(3,0))  -  (a(0,3) * a(1,2) * a(2,0) * a(3,1)) ;
  
  inv(0,0)=
  ((a(1,1) * a(2,2) * a(3,3))  +  (a(1,2) * a(2,3) * a(3,1))  +  (a(1,3) * a(2,1) * a(3,2)) 
  -(a(1,1) * a(2,3) * a(3,2))  -  (a(1,2) * a(2,1) * a(3,3))  -  (a(1,3) * a(2,2) * a(3,1)))
  /detA;
  
  inv(0,1)=
  ((a(0,1) * a(2,3) * a(3,2))  +  (a(0,2) * a(2,1) * a(3,3))  +  (a(0,3) * a(2,2) * a(3,1)) 
  -(a(0,1) * a(2,2) * a(3,3))  -  (a(0,2) * a(2,3) * a(3,1))  -  (a(0,3) * a(2,1) * a(3,2)))
  /detA;
  
  inv(0,2)=
  ((a(0,1) * a(1,2) * a(3,3))  +  (a(0,2) * a(1,3) * a(3,1))  +  (a(0,3) * a(1,1) * a(3,2)) 
  -(a(0,1) * a(1,3) * a(3,2))  -  (a(0,2) * a(1,1) * a(3,3))  -  (a(0,3) * a(1,2) * a(3,1)))
  /detA;
  
  inv(0,3)=
  ((a(0,1) * a(1,3) * a(2,2))  +  (a(0,2) * a(1,1) * a(2,3))  +  (a(0,3) * a(1,2) * a(2,1)) 
  -(a(0,1) * a(1,2) * a(2,3))  -  (a(0,2) * a(1,3) * a(2,1))  -  (a(0,3) * a(1,1) * a(2,2)))
  /detA;
  
  
  
  inv(1,0)=
  ((a(1,0) * a(2,3) * a(3,2))  +  (a(1,2) * a(2,0) * a(3,3))  +  (a(1,3) * a(2,2) * a(3,0)) 
  -(a(1,0) * a(2,2) * a(3,3))  -  (a(1,2) * a(2,3) * a(3,0))  -  (a(1,3) * a(2,0) * a(3,2)))
  /detA;
  
  inv(1,1)=
  ((a(0,0) * a(2,2) * a(3,3))  +  (a(0,2) * a(2,3) * a(3,0))  +  (a(0,3) * a(2,0) * a(3,2)) 
  -(a(0,0) * a(2,3) * a(3,2))  -  (a(0,2) * a(2,0) * a(3,3))  -  (a(0,3) * a(2,2) * a(3,0)))
  /detA;
  
  inv(1,2)=
  ((a(0,0) * a(1,3) * a(3,2))  +  (a(0,2) * a(1,0) * a(3,3))  +  (a(0,3) * a(1,2) * a(3,0)) 
  -(a(0,0) * a(1,2) * a(3,3))  -  (a(0,2) * a(1,3) * a(3,0))  -  (a(0,3) * a(1,0) * a(3,2)))
  /detA;
  
  inv(1,3)=
  ((a(0,0) * a(1,2) * a(2,3))  +  (a(0,2) * a(1,3) * a(2,0))  +  (a(0,3) * a(1,0) * a(2,2)) 
  -(a(0,0) * a(1,3) * a(2,2))  -  (a(0,2) * a(1,0) * a(2,3))  -  (a(0,3) * a(1,2) * a(2,0)))
  /detA;
  
  
  
  inv(2,0)=
  ((a(1,0) * a(2,1) * a(3,3))  +  (a(1,1) * a(2,3) * a(3,0))  +  (a(1,3) * a(2,0) * a(3,1)) 
  -(a(1,0) * a(2,3) * a(3,1))  -  (a(1,1) * a(2,0) * a(3,3))  -  (a(1,3) * a(2,1) * a(3,0)))
  /detA;
  
  inv(2,1)=
  ((a(0,0) * a(2,3) * a(3,1))  +  (a(0,1) * a(2,0) * a(3,3))  +  (a(0,3) * a(2,1) * a(3,0)) 
  -(a(0,0) * a(2,1) * a(3,3))  -  (a(0,1) * a(2,3) * a(3,0))  -  (a(0,3) * a(2,0) * a(3,1)))
  /detA;
  
  inv(2,2)=
  ((a(0,0) * a(1,1) * a(3,3))  +  (a(0,1) * a(1,3) * a(3,0))  +  (a(0,3) * a(1,0) * a(3,1)) 
  -(a(0,0) * a(1,3) * a(3,1))  -  (a(0,1) * a(1,0) * a(3,3))  -  (a(0,3) * a(1,1) * a(3,0)))
  /detA;
  
  inv(2,3)=
  ((a(0,0) * a(1,3) * a(2,1))  +  (a(0,1) * a(1,0) * a(2,3))  +  (a(0,3) * a(1,1) * a(2,0)) 
  -(a(0,0) * a(1,1) * a(2,3))  -  (a(0,1) * a(1,3) * a(2,0))  -  (a(0,3) * a(1,0) * a(2,1)))
  /detA;
  
  
  
  inv(3,0)=
  ((a(1,0) * a(2,2) * a(3,1))  +  (a(1,1) * a(2,0) * a(3,2))  +  (a(1,2) * a(2,1) * a(3,0)) 
  -(a(1,0) * a(2,1) * a(3,2))  -  (a(1,1) * a(2,2) * a(3,0))  -  (a(1,2) * a(2,0) * a(3,1)))
  /detA;
  
  inv(3,1)=
  ((a(0,0) * a(2,1) * a(3,2))  +  (a(0,1) * a(2,2) * a(3,0))  +  (a(0,2) * a(2,0) * a(3,1)) 
  -(a(0,0) * a(2,2) * a(3,1))  -  (a(0,1) * a(2,0) * a(3,2))  -  (a(0,2) * a(2,1) * a(3,0)))
  /detA;
  
  inv(3,2)=
  ((a(0,0) * a(1,2) * a(3,1))  +  (a(0,1) * a(1,0) * a(3,2))  +  (a(0,2) * a(1,1) * a(3,0)) 
  -(a(0,0) * a(1,1) * a(3,2))  -  (a(0,1) * a(1,2) * a(3,0))  -  (a(0,2) * a(1,0) * a(3,1)))
  /detA;
  
  inv(3,3)=
  ((a(0,0) * a(1,1) * a(2,2))  +  (a(0,1) * a(1,2) * a(2,0))  +  (a(0,2) * a(1,0) * a(2,1)) 
  -(a(0,0) * a(1,2) * a(2,1))  -  (a(0,1) * a(1,0) * a(2,2))  -  (a(0,2) * a(1,1) * a(2,0)))
  /detA;
  return inv;
}


//child class--------------------------------------------------------

Shift::Shift(double alpha)
 :Movement()
{
   m(0,0)=1;    m(0,1)=0;          m(0,2)=0;           m(0,3)=alpha;
   m(1,0)=0;    m(1,1)=1;          m(1,2)=0;           m(1,3)=0;
   m(2,0)=0;    m(2,1)=0;          m(2,2)=1;           m(2,3)=0;
   m(3,0)=0;    m(3,1)=0;          m(3,2)=0;           m(3,3)=1;
}


Slide::Slide(double alpha)
 :Movement()
{
   m(0,0)=1;    m(0,1)=0;          m(0,2)=0;           m(0,3)=0;
   m(1,0)=0;    m(1,1)=1;          m(1,2)=0;           m(1,3)=alpha;
   m(2,0)=0;    m(2,1)=0;          m(2,2)=1;           m(2,3)=0;
   m(3,0)=0;    m(3,1)=0;          m(3,2)=0;           m(3,3)=1;
}


Rise::Rise(double alpha)
 :Movement()
{
   m(0,0)=1;    m(0,1)=0;          m(0,2)=0;           m(0,3)=0;
   m(1,0)=0;    m(1,1)=1;          m(1,2)=0;           m(1,3)=0;
   m(2,0)=0;    m(2,1)=0;          m(2,2)=1;           m(2,3)=alpha;
   m(3,0)=0;    m(3,1)=0;          m(3,2)=0;           m(3,3)=1;
}


Twist::Twist(double alpha)
 :Movement()
{
  alpha = (alpha * RADIAN);//conversion in radian
  
   m(0,0)=cos(alpha);    m(0,1)=-sin(alpha);  m(0,2)=0;   m(0,3)=0;
   m(1,0)=sin(alpha);    m(1,1)=cos(alpha);   m(1,2)=0;   m(1,3)=0;
   m(2,0)=0;             m(2,1)=0;            m(2,2)=1;   m(2,3)=0;
   m(3,0)=0;             m(3,1)=0;            m(3,2)=0;   m(3,3)=1;
  
}


Roll::Roll(double alpha) 
 :Movement()
{
  alpha = (alpha * RADIAN);//conversion in radian
  
   m(0,0)=cos(alpha);     m(0,1)=0;   m(0,2)=sin(alpha);  m(0,3)=0;
   m(1,0)=0;              m(1,1)=1;   m(1,2)=0;           m(1,3)=0;
   m(2,0)=-sin(alpha);    m(2,1)=0;   m(2,2)=cos(alpha);  m(2,3)=0;
   m(3,0)=0;              m(3,1)=0;   m(3,2)=0;           m(3,3)=1;
  
}


Tilt::Tilt(double alpha)
 :Movement()
{
  alpha = (alpha * RADIAN);//conversion in radian
  
   m(0,0)=1;    m(0,1)=0;          m(0,2)=0;           m(0,3)=0;
   m(1,0)=0;    m(1,1)=cos(alpha); m(1,2)=-sin(alpha); m(1,3)=0;
   m(2,0)=0;    m(2,1)=sin(alpha); m(2,2)=cos(alpha);  m(2,3)=0;
   m(3,0)=0;    m(3,1)=0;          m(3,2)=0;           m(3,3)=1;
  
}

// Movement for building "classic" DNA
// reference for parameter:
// S.Arnott, R.Chandrasekaran, D.L.Birdsall, A.G.W.Leslie and R.L.Ratliff, Nature 283, 743-746 (1980) 
ADNA::ADNA():Movement()
{
  m=(Twist( 31.1185909091 )+Roll( 2.06055181818 )+Tilt( 2.12008054545 )+Rise( 3.37983727273 )+Slide( -2.41029181818 )+Shift( -0.549621454545 )).GetMatrix();
}

BDNA::BDNA():Movement()
{
  m=(Twist( 35.9063052632 )+Roll( -2.66592947368 )+Tilt( -1.80234789474 )+Rise( 3.27145684211 )+Slide( -1.34487389474 )+Shift( -0.425181378947 )).GetMatrix();

}

} //namespace PTools

