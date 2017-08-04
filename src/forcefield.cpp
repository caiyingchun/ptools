#include "forcefield.h"
#include "geometry.h"
#include "rmsd.h"
#include "pdbio.h"


#include <fstream>
#include <math.h>  //for fabs()
#include <sstream> //for istringstream


using std::ios_base;

// temporary:
// convert a std::string in an other type if >> is correctly defined 
#include <sstream>
template<typename T>
bool from_string( const std::string & Str, T & Dest )
{
    // create a stream from the input string
    std::istringstream iss( Str );
    // try the conversion toward Dest
    return (iss >> Dest) != 0;
}





namespace PTools
{



void PrintVec(const Vdouble& vec)
{
    std::cout << "Vector: " ;
    for (uint i=0; i<vec.size(); i++)
        std::cout << vec[i] << "  " ;

    std::cout << "\n";

}



#ifdef AUTO_DIFF

static bool numerical_warning=false;
void ForceField::NumDerivatives(const Vdouble& stateVars, Vdouble& delta, bool print)
{

    if (!numerical_warning)
    {
        std::cout << "Warning: using numerical derivatives in production may lead to poor performances\n" ;
        numerical_warning=true;
    }
    for (uint j=0; j<Problemsize(); j++)
    {

        std::vector<dbl> newvars1 = stateVars;
        std::vector<dbl> newvars2 = stateVars;



//         dbl h=1.0/20000.0;

        imag(newvars1[j])=1;
        dbl F1=Function(newvars1);
//         newvars2[j]-=h;
//         dbl F2=Function(newvars2);
//         dbl diff=(F1-F2)/(2*h) ;
        delta[j]=imag(F1);
        if (print) std::cout << "function : " << real(F1) << std::endl ;
    }

    if (print)
    {
        std::cout << "Numerical derivatives: \n";
        for (uint i=0; i<Problemsize(); i++)
        {
            std::cout <<  "Derivatives[" << i<< "]"  <<  real(delta[i]) << std::endl ;
        }
        std::cout << "\n";

    }
}
#else
void ForceField::NumDerivatives(const Vdouble& stateVars, Vdouble& delta, bool print)
{
    std::cout << "This feature was not enabled at compile-time. Please recompile with #define AUTO_DIFF \n";
}

#endif  //AUTO_DIFF





}//namespace PTools




