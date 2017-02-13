cdef extern from "chrg_scorpion.h":
    int chrg_scorpion__(int *, double *, double *, 
                      double *, double* ,
                      double *, int *,  double* ,
                      double *, double* ,
                      double *, double* ,
                      double*
                      )


def optimize(int natom, charge, radius, cx, cy, cz, int nbead, cgch, cgr, cgx, cgy, cgz, double delgrid):
    cdef double ccharge [20000], cradius[20000], ccx[20000], ccy[20000], ccz[20000]
    cdef double ccgch [2000], ccgr[2000], ccgx[2000], ccgy[2000], ccgz[2000]
    
    for i in range(natom):
       ccharge[i] = charge[i]
       cradius[i] = radius[i]
       ccx[i] = cx[i] 
       ccy[i] = cy[i] 
       ccz[i] = cz[i]
        
    for i in range(nbead):
       ccgch[i] = cgch[i]
       ccgr[i] = cgr[i]
       ccgx[i] = cgx[i] 
       ccgy[i] = cgy[i] 
       ccgz[i] = cgz[i]
  
    result = chrg_scorpion__( &natom, ccharge, cradius, ccx, ccy, ccz, &nbead, ccgch, ccgr, ccgx, ccgy, ccgz,&delgrid)

    output = []
    for i in range(nbead):
        output.append(ccgch[i])

    return output
