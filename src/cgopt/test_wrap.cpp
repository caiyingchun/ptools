//#include <stdio.h>
//#include <stdlib.h>
#include <vector>
//#include <string.h>
#include <iostream>
//#include <math.h>
//#include <float.h>

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

int main(int argc, char **argv)
{ 

	// CHR main is to test that example values are properly passed to the fortran subroutine,
	// not as a realistic test case (in fact they produce a segfault in chrg_scorpion.f)
	int natom = 2;
	int natom_dim = 20000;

	std::vector<double> charge(natom_dim);
	charge[0] = 1.0;
	charge[1] = 1.0;

	std::vector<double> radius(natom_dim);
	radius[0] = 1.0;
	radius[1] = 1.0;

	std::vector<double> coorx(natom_dim);
	coorx[0] = 1.0;
	coorx[1] = 2.0;

	std::vector<double> coory(natom_dim);
	coory[0] = 1.0;
	coory[1] = 2.0;

	std::vector<double> coorz(natom_dim);
	coorz[0] = 1.0;
	coorz[1] = 2.0;


	int nbead = 2;
	int nbead_dim = 2000;

	std::vector<double> cgchg(nbead_dim);
	cgchg[0] = 1.0;
	cgchg[1] = 1.0;

	std::vector<double> cgrad(nbead_dim);
	cgrad[0] = 1.0;
	cgrad[1] = 1.0;

	std::vector<double> cgcox(nbead_dim);
	cgcox[0] = 1.1;
	cgcox[1] = 2.1;

	std::vector<double> cgcoy(nbead_dim);
	cgcoy[0] = 1.1;
	cgcoy[1] = 2.1;

	std::vector<double> cgcoz(nbead_dim);
	cgcoz[0] = 1.1;
	cgcoz[1] = 2.1;

	double delgrid = 1.5;

	static const int arr[] = {16,2,77,29};

	std::cout << "coucou" << std::endl;
	std::cout << "size: " << charge.size() << std::endl;
	std::cout << arr[0] << std::endl;
	std::cout << "Here comes the bus error from the poorly-chosen test values:" << std::endl;

	CHRG_SCORPION_FUN(&natom, &charge[0], &radius[0], &coorx[0], &coory[0], &coorz[0], 
						&nbead, &cgchg[0], &cgrad[0], &cgcox[0], &cgcoy[0], &cgcoz[0], &delgrid);

	return 0;
}

