#include "coord3d.h"

#include <string>
#include <sstream>

namespace PTools{

Coord3D& Coord3D::Normalize(){
    dbl norm = Norm(*this);
    x = x / norm;
    y = y / norm;
    z = z / norm;
    return *this;
}



std::string Coord3D::to_string(bool newline)
{
    std::stringstream result;
    result << x << "  " << y << "  " << z ;
    if (newline) result << "\n";
    return result.str();
}



}

