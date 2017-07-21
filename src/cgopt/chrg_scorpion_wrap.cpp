// Thanks to http://www.yolinux.com/TUTORIALS/LinuxTutorialMixingFortranAndC.html
#include <vector>
#include <iostream>

#if defined(WIN32) && !defined(__GNUC__) /* assume use Intel Fortran Compiler on win32 platform if not compiled with G    CC */
#    define CHRG_SCORPION_FUN chrg_scorpion 
#else
#    define CHRG_SCORPION_FUN chrg_scorpion_ /* assume use GNU f77 otherwise */
#endif


extern"C" {
	void CHRG_SCORPION_FUN(int *natom, double *charge, double *radius, double *coorx, double *coory, double *coorz,
						int *nbead, double *cgchg, double *cgrad, double *cgcox, double *cgcoy, double *cgcoz, double *delgrid);
}
