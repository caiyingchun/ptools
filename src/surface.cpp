
#include "surface.h"
#include "attractrigidbody.h"

#include <cassert>

namespace PTools
{

void Surface::setUp(int nphi, int ncosth)
{
    // dimension csth(ncosth),snth(ncosth),phgh(nphi)

    const dbl pi= 3.141592654;
    //  precalculate costh,sinth and phigh for different ncosth...
    for (uint ik=0; ik < (uint) ncosth; ik++)
    {
        csth.push_back (   -1.0 + ( ( (dbl) ik+1) - 0.5  ) * (2.0 / (dbl) ncosth ) ) ;
        snth.push_back (   sqrt(1.0 -csth[ik]*csth[ik] ) );
    }

    for ( int ik=0; ik<nphi; ik++)
    {
        cos_phgh.push_back ( cos(2.0 * pi *  ((dbl)ik-1.0)/(dbl) nphi )) ;
        sin_phgh.push_back ( sin(2.0 * pi *  ((dbl)ik-1.0)/(dbl) nphi )) ;
    }

}

void Surface::surfpointParams(int max, dbl shift)
{
    m_numneh = max;
    m_sradshift = shift;
    m_init=true;
}

void Surface::readsolvparam(const std::string& file)
{
    std::string line ;
    //int count = 0;
    radi.clear();

    std::ifstream sfile(file.c_str());
    if (! sfile)
        {
            //  the file cannot be opened
            std::string msg = " Cannot Locate file ";
	    msg.append(file.c_str());
	    msg.append("\n");
            std::cerr << msg ;
            throw msg;
	}

    while (std::getline(sfile, line))
    {
        //count++ ; // count number of line (unused at the moment)
        //int size_line = line.size(); // count line length (unused at the moment)
        //dbl data1=atof(line.substr(1,6).c_str()); // read first column - atom type id (unused at the moment)
        dbl data2=atof(line.substr(7,13).c_str()); // read second column - radius (unused at the moment)
        //dbl data3=atof(line.substr(14,20).c_str()); // read third column - solvation parameters (unused at the moment)
        //std::string data4=line.substr(21,size_line).c_str(); // read last column (unused at the moment)
        radi.push_back(data2);
     }
}

Rigidbody Surface::surfpoint(const Rigidbody & rigid, dbl srad)
{
    Rigidbody rigidsurf;
    int size_rigid = rigid.Size();
    std::vector<int> neigh;
    radius.clear();

    // fix neighbours parameters if not initialized
    if (!m_init)
    {
        m_numneh = 2000;
        m_sradshift = 0.0;
    }
    // read radius
    AttractRigidbody rigid_tmp(rigid);
    m_atomtypenumber.resize(size_rigid);
    for (uint i=0; i< rigid_tmp.Size(); i++)
    { m_atomtypenumber[i] = rigid_tmp.getAtomTypeNumber(i);}
    for (int i=0; i<size_rigid; i++)
    {
        Atom m_atom = rigid_tmp.copy_atom(i);
        radius.push_back(radi[m_atomtypenumber[i]]);
    }

    // generate grid points
    for (int i=0; i<size_rigid; i++)
        if ( radius[i] != 0.0 )
        {
            Coord3D coord1 = rigid.get_coords(i);
            int numneh = 0;
            neigh.clear();
            for (int j=0; j<size_rigid; j++) // generate neighbor list
                if (i!=j)
                {
                    Coord3D coord2 = rigid.get_coords(j);
                    dbl ccdist = Norm2(coord1 - coord2);
                    dbl rr = (radius[i]+radius[j]+2.0*srad) * (radius[i]+radius[j]+2.0*srad);
                    if (ccdist <= rr)
                    { neigh.push_back(j);
                        numneh+=1;
                        if  ( numneh > m_numneh )
                        {
                            std::string msg = " ERROR: Atom has too many neighbors \n"  ;
                            std::cout << msg;
                            throw msg;
                        }
                    }
                }
            numneh = numneh - 1;
            for (int j=0; j<m_ncosth; j++) // generate points around each atoms
            {
                dbl costh = csth[j];
                dbl sinth = snth[j];
                for (int k=0; k<m_nphi; k++)
                {
                    dbl cphigh = cos_phgh[k];
                    dbl sphigh = sin_phgh[k];
                    Coord3D coord4;
                    coord4.x = (radius[i]+srad+m_sradshift)*sinth*cphigh;
                    coord4.y = (radius[i]+srad+m_sradshift)*sinth*sphigh;
                    coord4.z = (radius[i]+srad+m_sradshift)*costh;
                    int l = 0;
                    bool coverd = false;
                    while ((!coverd) && (l <= numneh))
                    {
                        Coord3D coord5 = rigid.get_coords(neigh[l]);
                        dbl ddd = Norm2(coord1 + coord4 - coord5);
                        if (ddd < (radius[neigh[l]] + srad+m_sradshift)*(radius[neigh[l]] + srad+m_sradshift))
                        { coverd = true; }
                        l+=1;
                    }
                    if (!coverd)
                    {
                        Atom m_atom2 = rigid.copy_atom(i);
                        m_atom2.coords = coord1 + coord4;
                        rigidsurf.add_atom(m_atom2);
                    }
                }
            }

            // fill the top and bottom positions
            dbl costh = -1;
            while (costh<=1.0)
            {
                Coord3D coord4;
                coord4.x = 0.0;
                coord4.y = 0.0;
                coord4.z = (radius[i]+srad+m_sradshift)*costh;
                int l = 0;
                bool coverd = false;
                while ((!coverd) && (l <= numneh))
                {
                    Coord3D coord5 = rigid.get_coords(neigh[l]);
                    dbl ddd = Norm2(coord1 + coord4 - coord5);
                    if (ddd < (radius[neigh[l]] + srad+m_sradshift)*(radius[neigh[l]] + srad+m_sradshift))
                    { coverd = true; }
                    l+=1;
                }
                if (!coverd)
                {
                    Atom m_atom2 = rigid.copy_atom(i);
                    m_atom2.coords = coord1 + coord4 ;
                    rigidsurf.add_atom(m_atom2);
                }
                costh+=2;
            }
        }
    return rigidsurf;
}

Rigidbody Surface::outergrid(const Rigidbody & grid, const Rigidbody & rigid2, dbl rad)
{
    //used to remove grid points that are too close from the receptor
    //ie: there is not enough space to put the ligand at a distance < ligand.radius from the receptor
    
    int grid_size = grid.Size();
    int size2 = rigid2.Size();
    Rigidbody rigid3;
    double srad = rad*rad;
    
    for (int i=0; i < grid_size; i++)
    {
        Coord3D xyz1 = grid.get_coords(i);
        bool select = true;
        for (int j=0; j<size2; j++)
        {
            Coord3D xyz2 = rigid2.get_coords(j);
            dbl dist=Norm2(xyz1-xyz2);
            if (dist < srad) { select = false; }
        }
        if (select) { rigid3.add_atom(grid.copy_atom(i)); }
    }
    return rigid3;
}

Rigidbody Surface::removeclosest(const Rigidbody & rigid, dbl srad)
{
    
    int const size=rigid.Size();
    Rigidbody rigid2;
    
    srad=srad*srad;
    
    std::vector<bool> list(size, true);

    for (int i=0; i<size; i++)
    {
        Coord3D  xyz1 = rigid.get_coords(i);
        for (int j=0; j<size; j++)
            if ((list[i]) && (i!=j))
            {
                Coord3D  xyz2 = rigid.get_coords(j);
                dbl dist=Norm2(xyz1 - xyz2);
                if (dist < srad) { list[j] = false; }
            }
    }
    for (int i=0; i<size; i++)
    if (list[i]) { rigid2.add_atom(rigid.copy_atom(i)); }
    return rigid2;
}

}//namespace PTools
