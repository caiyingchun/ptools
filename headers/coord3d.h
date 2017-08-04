#ifndef COORD3D_H
#define COORD3D_H


#include <math.h>
#include <string>
#include <vector>
#include <ostream>

#include "basetypes.h"

namespace PTools{


struct Coord3D
{
    dbl x,y,z;

    Coord3D() {x=0.0; y=0.0;z=0.0;};
    Coord3D(dbl nx, dbl ny, dbl nz){x=nx;y=ny;z=nz;};
    Coord3D(const Coord3D& old) {x=old.x; y=old.y; z=old.z;};

    inline Coord3D & operator= (const Coord3D &);
    inline bool operator==(const Coord3D& b) {return (b.x==x && b.y==y && b.z==z); };
    Coord3D&  Normalize(); ///< Normalize vector to unity (in place)

    std::string to_string(bool newline=true);

};


typedef std::vector<Coord3D> VCoord3D;

/// Define = operator : Coord3D = Coord3D
inline Coord3D & Coord3D::operator= (const Coord3D & C)
{
	//note: this function works in the case of self assignation
    x = C.x;
    y = C.y;
    z = C.z;
    return *this;
}

/// Define + operator : Coord3D + Coord3D
inline Coord3D operator+ (const Coord3D& A,const Coord3D& B)
{
    Coord3D P(A);
    P.x += B.x ;
    P.y += B.y ;
    P.z += B.z ;
    return P;
}

/// define - operator : Coord3D - Coord3D
inline Coord3D operator- (const Coord3D& A,const Coord3D& B)
{
    Coord3D P(A);
    P.x -= B.x ;
    P.y -= B.y ;
    P.z -= B.z ;
    return P;
}


inline Coord3D & operator+=(Coord3D & a, const Coord3D & x ){a = a + x ; return a; }  //operator +=
inline Coord3D & operator-=(Coord3D & a, const Coord3D & x ){a = a - x ; return a; }  //operator -=


/// Vector dot product.
inline dbl dotProduct(const Coord3D & a, const Coord3D & b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

/// Vector cross product.
inline Coord3D crossProduct(const Coord3D & u, const Coord3D & v)
{
    return Coord3D(u.y * v.z - u.z * v.y,
                   u.z * v.x - u.x * v.z,
                   u.x * v.y - u.y * v.x);
}


/// Vector Norm
inline dbl Norm(const Coord3D & A)
{
    return sqrt (A.x*A.x + A.y*A.y + A.z*A.z) ;
}

/// Vector norm * norm
inline dbl Norm2(const Coord3D & A)
{
    return  (A.x*A.x + A.y*A.y + A.z*A.z);
}


/// define * operator : Coord3D x dbl
inline Coord3D operator* (const Coord3D& A, dbl scal)
{
    Coord3D P(A);
    P.x *= scal ;
    P.y *= scal ;
    P.z *= scal ;
    return P;
}

/// define * operator : dbl * Coord3D
inline Coord3D operator* (dbl scal, const Coord3D& A) {
    return A * scal ;
}


/// define / operator : Coord3D / dbl
inline Coord3D operator/ (const Coord3D& A, dbl d) {
    return (1/d) * A ;
}



/// print coordinates in string
inline std::string PrintCoord(const Coord3D& A) {
    int size=100;
    char *info = new char [size];
    snprintf(info, size, "%8.3f %8.3f %8.3f", real(A.x), real(A.y), real(A.z));
    std::string result(info);
    delete[] info;
    return result;
}


inline std::ostream& operator<< (std::ostream& out, const Coord3D& co)
{
    out << PrintCoord(co);
	return out;
}




inline Coord3D minus(const Coord3D& orig)
{
    Coord3D min;
    min.x = -orig.x;
    min.y = -orig.y;
    min.z = -orig.z;
    return min;
}




}

#endif //CORRD3D_H

