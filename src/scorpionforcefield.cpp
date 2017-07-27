#include "scorpionforcefield.h"


#include <fstream>
#include <math.h>  //for fabs()
#include <sstream> //for istringstream


using std::ios_base;


namespace PTools {


ScorpionForceField::ScorpionForceField(std::string paramsFileName, dbl cutoff)
//         :m_refreceptor(recept), m_refligand(lig), m_receptor(recept), m_ligand(lig),m_savligand(lig),
//         plist(recept,lig,cutoff)

{

    InitParams(paramsFileName);

    m_rstk=0.0; //no restraint by default
    m_cutoff = cutoff;

}



void ScorpionForceField::InitParams(const std::string & paramsFileName )
{
    int indice;
    dbl sigma;
    dbl lambda;
    dbl epsilon;
    

    std::ifstream aminon(paramsFileName.c_str());
    if (!aminon)
    {
        //the file cannot be opened
        std::string msg = "Forcefield.cpp: Cannot Locate file forcefield parameters (scorpion.par)\n";
        std::cout << msg ;
        throw std::invalid_argument(msg);
    }

    while (!aminon.eof())
    {
        aminon >> indice >> epsilon >> lambda >> sigma ;
        m_epsilon.push_back(epsilon) ;
        m_lambda.push_back(lambda) ;
        m_sigma.push_back(sigma) ;

        assert(m_sigma.size()<64);
    }


    //initialisation of the pre-calculated array of rc and ac
    for (uint i=0; i<m_sigma.size();i++)
        for (uint j=0; j<m_sigma.size(); j++)
        {
            m_lamb6[i][j]=pow(0.5*(m_lambda[i]+m_lambda[j]),6);
            m_sig2[i][j]=0.25*(m_sigma[i]+m_sigma[j])*(m_sigma[i]+m_sigma[j]);
            m_epsij[i][j]=sqrt(m_epsilon[i]*m_epsilon[j]);
 
        }
}



std::vector<dbl> fswitch (dbl x) //fonction de switch et sa derivee
{

std::vector<dbl> result(2); //probablement std::pair a utiliser...

const dbl ron = 6.0 ;
const dbl roff = 9.0 ;

if (x <= ron ) 
  {
  result[0]=1.0 ;
  result[1]=0.0 ;
  return result;
  }

if (x >= roff)
  {
  result[0]=0.0 ;
  result[1]=0.0 ;
  return result;
  }
  
dbl rofr = roff-x ;
dbl rron = x-ron ;
dbl rofron = roff-ron ;
rofron = rofron*rofron*rofron ;
result[0] = rofr*rofr*(rofr+3*rron)/rofron ; //f(x)
result[1] = -6.0*rofr*rron/rofron ; //f'(x)
  
return result;
}


std::vector<dbl> fsigmo (dbl x)
{

std::vector<dbl> result(2); //probablement std::pair a utiliser...

const dbl plato = 80.0 ;
const dbl slope = 1.2 ;
const dbl epsint = 1.0 ;

dbl sr = slope*x ;
dbl exsr = exp(-sr) ;

result[0] = plato-0.5*(plato-epsint)*(sr*sr+2.0*sr+2.0)*exsr ;
result[1] = 0.5*(plato-epsint)*slope*sr*sr*exsr ;

return result;
}



dbl ScorpionForceField::nonbon8_forces(AttractRigidbody& rec, AttractRigidbody& lig, AttractPairList & pairlist, std::vector<Coord3D>& forcerec, std::vector<Coord3D>& forcelig, bool print)
{

    assert(forcerec.size() == rec.Size());
    assert(forcelig.size() == lig.Size());

    dbl sumLJ=0.0 ;
    dbl sumElectrostatic=0.0;


    //synchronize coordinates for using unsafeget_coords
    rec.syncCoords();
    lig.syncCoords();

    Coord3D a, b;


    for (uint iter=0; iter<pairlist.Size(); iter++)
    {

        uint ir = pairlist[iter].atrec;
        uint jl = pairlist[iter].atlig;

        uint rAtomCat = rec.getAtomTypeNumber(ir);
        uint lAtomCat = lig.getAtomTypeNumber(jl);

        dbl lij = m_lamb6[ rAtomCat ][ lAtomCat ];
        dbl sij = m_sig2[ rAtomCat ][ lAtomCat ];
        dbl eij = m_epsij[ rAtomCat ][ lAtomCat ];


        lig.unsafeget_coords(jl,a);
        rec.unsafeget_coords(ir,b);

        Coord3D dx = a-b ;
        dbl r2 = Norm2(dx);
        dbl r1 = Norm(dx);

        if (r2 < 0.001 ) r2=0.001;
        dbl rr2 = 1.0/r2 ; // 1/r^2
        dbl rr23 = rr2*rr2*rr2 ; // 1/r^6
        dbl elr6 = eij*lij*rr23 ; // epsilon*lambda^6/r^6
        dbl r2s2 = r2/sij ; // r^2/sigma^2
        dbl er2s2 = eij*exp(-r2s2) ; // epsilon*exp(-r^2/sigma^2)
        std::vector<dbl> vswi = fswitch(r1); // vswi[0]=fonction, vswi[1]=derivee

        dbl vlj = elr6*vswi[0]-er2s2 ;

        sumLJ += vlj;

        dbl fb = elr6*(6.0*vswi[0]-r1*vswi[1])-2.0*r2s2*er2s2 ; 

        dx = rr2*dx;
        Coord3D fdb = fb*dx ;

        //assign force to the atoms:
        forcelig[jl] -= fdb ;
        forcerec[ir] += fdb ;



        //electrostatic part:
        dbl chargeR = rec.m_charge[ir];
        dbl chargeL = lig.m_charge[jl];
        dbl charge = chargeR * chargeL * (332.053986);
      
        if (fabs(charge) > 0.0)
        { 
            std::vector<dbl> sigmo = fsigmo(r1);
            dbl et = charge/sigmo[0]/r1;
           
            sumElectrostatic+=et;

            Coord3D fdb = et*(sigmo[1]*r1/sigmo[0]+1.0)*dx;
            forcelig[jl] -= fdb ;
            forcerec[ir] += fdb ;
        }
    }

    m_vdw = sumLJ;
    m_elec = sumElectrostatic;

//    std::cout << "ELJ: " << sumLJ*4.184 << " EElec: " << sumElectrostatic*4.184 << std::endl ;
    return sumLJ + sumElectrostatic;
}


} //namespace PTools
