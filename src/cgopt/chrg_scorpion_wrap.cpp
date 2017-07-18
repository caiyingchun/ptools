#include <stdio.h>
#include <stdlib.h>
#include <vector>
#include <string.h>
#include <iostream>
#include <math.h>
#include <float.h>

#if defined(WIN32) && !defined(__GNUC__) /* assume use Intel Fortran Compiler on win32 platform if not compiled with G    CC */
#    define CHRG_SCORPION_FUN chrg_scorpion 
#else
#    define CHRG_SCORPION_FUN chrg_scorpion_ /* assume use GNU f77 otherwise */
#endif


extern"C" {
	//void fortfunc_(int *ii, float *ff);
	void CHRG_SCORPION_FUN(int *natom, double *charge, double *radius, double *coorx, double *coory, double *coorz,
						int *nbead, double *cgchg, double *cgrad, double *cgcox, double *cgcoy, double *cgcoz, double *delgrid);
}
