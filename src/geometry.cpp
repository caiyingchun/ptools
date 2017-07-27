#include "geometry.h"


namespace PTools{



/** \brief Matrix multiplication
*  This function is a simple matrix multiplication routine for 4x4 matrix
*/
void mat44xmat44( const dbl mat1[ 4 ][ 4 ], const dbl mat2[ 4 ][ 4 ], dbl result[ 4 ][ 4 ] )
{
// gives mat1*mat2 (mat2 left multiplied by mat1)
// this works even if result == mat1 (ie pointing the to same memory)

    dbl temp[4][4];

    //std::cout << mat1 << " " << mat2 << " " << result;
    //printmat44(mat1);
    //printmat44(mat2);

    for ( int rl = 0; rl < 4; rl++ )
        for ( int rc = 0; rc < 4; rc++ )
        {
            // compute the element result[rl][rc]:
            dbl sum = 0.0 ;
            for ( int p = 0; p < 4; p++ )
                sum += mat1[ rl ][ p ] * mat2[ p ][ rc ] ;
            temp[ rl ][ rc ] = sum ;
        }

    //printmat44(result);
    memcpy(result, temp, 16*sizeof(dbl));

}




void MakeRotationMatrix( Coord3D A, Coord3D B, dbl theta, dbl out[ 4 ][ 4 ] )
{

    // compute AB vector (dx; dy; dz):
    dbl dx = B.x - A.x ;
    dbl dy = B.y - A.y ;
    dbl dz = B.z - A.z ;

    dbl mat1[ 4 ][ 4 ] ;

    
    MakeTranslationMat44( Coord3D() - A , mat1 );
    

    dbl cost = cos( theta );
    dbl sint = sin( theta );
        

    //we normalize the AB vector
    dbl x,y,z;
    dbl L = sqrt(dx*dx+dy*dy+dz*dz);
    x = dx / L;
    y = dy / L;
    z = dz / L;
   
    dbl rodrig[4][4];
    
    //Rodrigues' rotation matrix:
    
    rodrig[0][0] = cost + x*x*(1-cost);
    rodrig[1][0] = x*y*(1-cost) + z*sint;
    rodrig[2][0] = z*x*(1-cost) - y*sint;
    rodrig[3][0] = 0;
    
    rodrig[0][1] = x*y*(1-cost) - z*sint ; 
    rodrig[1][1] = cost + y*y*(1-cost);
    rodrig[2][1] = z*y*(1-cost) + x*sint;
    rodrig[3][1] = 0;
    
    rodrig[0][2] = x*z*(1-cost) + y*sint;
    rodrig[1][2] = y*z*(1-cost)-x*sint;
    rodrig[2][2] = cost + z*z*(1-cost);
    rodrig[3][2] = 0;
    
    rodrig[0][3] = 0;
    rodrig[1][3] = 0;
    rodrig[2][3] = 0;
    rodrig[3][3] = 1;
    
    
    
    //left multiply translation matrix by the Rodrigues matrix:
    mat44xmat44(rodrig, mat1, out);
    
    //translate back to point A:
    MakeTranslationMat44(A, mat1);
    
    //left multiply rot+trans matrix by the back translation to A:
    
    mat44xmat44(mat1, out, out);
    
}




void rotate( Coord3D A, Coord3D B, Rigidbody& target, dbl theta )
{

    dbl matrix[ 4 ][ 4 ];
    MakeRotationMatrix( A, B, theta, matrix );
    target.MatrixMultiply(matrix);
//     mat44xrigid( source, result, matrix );
}






void VectProd( const Coord3D& u, const Coord3D& v, Coord3D& UvectV )
{
    UvectV.x = u.y * v.z - u.z * v.y ;
    UvectV.y = u.z * v.x - u.x * v.z ;
    UvectV.z = u.x * v.y - u.y * v.x ;
}

void printmat44( const dbl mat[ 4 ][ 4 ] )
{

    for (uint i=0; i<4; i++)
    {
        for (uint j=0; j<4; j++)
        {
            printf("%12.7f", real(mat[i][j])) ;
        }
        std::cout << std::endl;
    }

    std::cout << "\n\n";
}


void MakeVect( const Coord3D& a, const Coord3D& b, Coord3D& result )
{
    result.x = b.x - a.x;
    result.y = b.y - a.y;
    result.z = b.z - a.z;
}



dbl Dihedral( const Coord3D& a, const Coord3D& b, const Coord3D& c, const Coord3D& d )
{
    // calculate the dihedral angle defined by a, b, c and d.
    // The method is described in: J.K Rainey, Ph.D. Thesis,
    // University of Toronto, 2003. 
	// Collagen structure and preferential assembly explored 
	// by parallel microscopy and bioinformatics.
    // also described here: 
	// http://structbio.biochem.dal.ca/jrainey/dihedralcalc.html

    Coord3D b1 = b-a;
    Coord3D b2 = c-b;
    Coord3D b3 = d-c;

    Coord3D n1;
    VectProd (b2, b3, n1);
    Coord3D n2;
    VectProd(b1, b2, n2);

    Coord3D n3;
    VectProd(b2,b3,n3);

    dbl phi  = atan2( Norm(b2) * ScalProd(b1, n1),  ScalProd(n2 , n3) ) ;
    return phi;

}



dbl Angle(const Coord3D& vector1, const Coord3D& vector2)
{
    dbl pdtscal=ScalProd(vector1,vector2);
    dbl A = sqrt(ScalProd(vector1,vector1)) ;
    dbl B = sqrt(ScalProd(vector2,vector2));

    dbl costheta = pdtscal / (A*B) ;
    return acos(costheta);
}

dbl MakeTranslationMat44(Coord3D t, dbl out[4][4] )
{
    for (int i=0; i<4; i++)
      for(int j=0; j<4; j++)
      {
        if (i==j) out[i][i]=1.0;
        else out[i][j]=0.0;
      }

     out[0][3]=t.x;
     out[1][3]=t.y;
     out[2][3]=t.z;

}




} //namespace PTools

