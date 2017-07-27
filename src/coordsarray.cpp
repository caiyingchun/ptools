/****************************************************************************
 *   Copyright (C) 2008   Adrien Saladin                                    *
 *   adrien.saladin@gmail.com                                               *
 *                                                                          *
 *   This program is free software: you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation, either version 3 of the License, or      *
 *   (at your option) any later version.                                    *
 *                                                                          *
 *   This program is distributed in the hope that it will be useful,        *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
 *   GNU General Public License for more details.                           *
 *                                                                          *
 *   You should have received a copy of the GNU General Public License      *
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.  *
 *                                                                          *
 ***************************************************************************/


#include<stdexcept>

#include <iostream>
#include <sstream>

#include "coordsarray.h"
#include "geometry.h"




namespace PTools{



CoordsArray::CoordsArray()
{
    for (uint i=0; i<4; i++)
        for (uint j=0; j<4; j++)
        {
            mat44[i][j]=0;
            if (i==j) mat44[i][j]=1;
        }

}


CoordsArray::CoordsArray(const CoordsArray & ca) //copy constructor
{
    _refcoords   = ca._refcoords;
    _movedcoords = ca._movedcoords;

    _modified();

//copy of the matrix:
//Note: very naive way. May be slower than memcpy()
    for (uint i=0; i<4; i++)
        for (uint j=0; j<4; j++)
            this->mat44[i][j]=ca.mat44[i][j];

}


void CoordsArray::Translate(const Coord3D& tr)
{
    //updates rotation/translation matrix:
    this->mat44[0][3]+=tr.x;
    this->mat44[1][3]+=tr.y;
    this->mat44[2][3]+=tr.z;

    _modified();
}



void CoordsArray::MatrixMultiply(const dbl mat[4][4])
{
    mat44xmat44( mat, mat44, mat44 ); //multiply our internal matrix4x4 by mat
    _modified();  // invalidates coordinates
}

void CoordsArray::ResetMatrix()
{

    _modified();

    for (uint i=0; i<4; i++)
        for (uint j=0; j<4; j++)
        {
            if (i!=j) mat44[i][j]=0;
            else mat44[i][j]=1;
        }

}



std::string CoordsArray::print_matrix() const
{
    std::string out;
    out += "### MAT BEGIN\n";
    for (uint i=0; i<4; i++)
    {

        out += "MAT   ";
        for (uint j=0; j<4; j++)
        {
            char tmp[20]; 

            snprintf(tmp,19,"%14.7f ", real(this->mat44[i][j])) ;
            out += tmp;
        }
        out +="\n";
    }
    out +=  "### MAT END\n";
    return out;
}


Matrix CoordsArray::get_matrix() const
{
Matrix matrix(4,4);

for(uint i=0; i<4; i++)
  for(uint j=0; j<4; j++)
    matrix(i,j)=mat44[i][j];

return matrix;
}




void CoordsArray::get_coords(const uint i, Coord3D& co)  const throw(std::out_of_range)
{

    if (i>=size())
    {
        std::stringstream ss (std::stringstream::in | std::stringstream::out);
        ss <<  "CoordsArray::get_coords : out of range :  ";
        ss << i << " is out of bounds (object size: " << size() << ")\n";
        std::string message = ss.str() ;
        std::cerr << message ;
        throw std::out_of_range (message);
    }

    (*this.*_getcoords)(i,co);
};


void CoordsArray::set_coords(const uint k, const Coord3D& co)
{
//sets the coordinate [i] to be 'co' after rotation/translation

Coord3D co2 (co);

co2.x -= mat44[0][3];
co2.y -= mat44[1][3];
co2.z -= mat44[2][3];

dbl matinv[4][4]; //invert matrix


for(uint i=0; i<3; i++)
  for(uint j=0; j<3;j++)
    matinv[i][j]=mat44[j][i];

for(uint i=0; i<4; i++)
 {
   matinv[i][3]=0;
   matinv[3][i]=0;
 }
   matinv[3][3]=1;


Coord3D final;


PTools::matrix44xVect(matinv,co2, final );

_refcoords[k] = final;
_modified();


}



/*!  \brief this function makes an euler rotation with the Attract convention.
*
*   Note that for this new implementation only the 4x4 rotational/translational
*   matrix is updated. This may allow a big speedup (to be tested) and a
*   higher flexibility  (  rig.Translate(a); rig.Translate(minus(a)); may now be delayed
*   until the coordinates are really needed.
*   If coordinates are never asked (why?), then no costly calculation is performed !
*/
void CoordsArray::euler_rotate(dbl phi, dbl ssi, dbl rot)
{

    dbl  cp, cs, ss, sp, cscp, sscp, sssp, crot, srot, cssp ;

    cs=cos(ssi);
    cp=cos(phi);
    ss=sin(ssi);
    sp=sin(phi);
    cscp=cs*cp;
    cssp=cs*sp;
    sscp=ss*cp;
    sssp=ss*sp;
    crot=cos(rot);
    srot=sin(rot);


    dbl eulermat[4][4];

    eulermat[0][0] = crot*cscp + srot*sp;
    eulermat[0][1] = srot*cscp - crot*sp;
    eulermat[0][2] = sscp;
    eulermat[0][3] = 0.0;

    eulermat[1][0] = crot*cssp-srot*cp ;
    eulermat[1][1] = srot*cssp+crot*cp;
    eulermat[1][2] = sssp;
    eulermat[1][3] = 0.0;

    eulermat[2][0] = -crot*ss;
    eulermat[2][1] = -srot*ss;
    eulermat[2][2] = cs;
    eulermat[2][3] = 0.0;

    eulermat[3][0] = 0.0;
    eulermat[3][1] = 0.0;
    eulermat[3][2] = 0.0;
    eulermat[3][3] = 1.0;

    //matrix multiplication
    this->MatrixMultiply(eulermat);
//       mat44xmat44( eulermat , this->mat44, this->mat44);

}



}//namespace PTools


