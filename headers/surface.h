#include <iostream>
#include <fstream>
#include <string>

#include "rigidbody.h"

#ifndef SURFACE_H
#define SURFACE_H


namespace PTools
{

class Surface
{

public:

    Surface(int nphi, int ncosth, std::string file) /// Constructor (initialize private data)
    {
        m_nphi=nphi;
        m_ncosth=ncosth;
        setUp(nphi, ncosth);
        m_init=false;
        readsolvparam(file);
    };

    Rigidbody surfpoint(const Rigidbody & rigid, dbl srad); /// generate a grid of point around the protein
    void surfpointParams(int max, dbl shift); /// initialize some parameters of the grid generation
    Rigidbody outergrid(const Rigidbody & grid, const Rigidbody & rigid2, dbl rad); /// remove overlap between rigid1 and rigid2
    Rigidbody remove_closest(const Rigidbody & rigid1, dbl srad); /// fix the density of the grid (remove points that are too close to eachother)
    void readsolvparam(const std::string& file); /// read solvation parameters
    
private:

    //private functions
    void setUp(int nphi, int ncosth);

    //private data
    int m_nphi, m_ncosth;
    int m_numneh;
    bool m_init;
    dbl m_sradshift;
    std::vector<dbl>  csth , snth, cos_phgh , sin_phgh;
    std::vector<dbl>  radi, radius;
    std::vector<int> m_atomtypenumber;

};

}//namespace PTools


#endif //SURFACE_H



