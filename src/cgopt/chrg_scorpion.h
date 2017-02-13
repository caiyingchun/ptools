/* chrg_scorpion.f -- translated by f2c (version 20090411).
   You must link the resulting object file with libf2c:
	on Microsoft Windows system, link with libf2c.lib;
	on Linux or Unix systems, link with .../path/to/libf2c.a -lm
	or, if you install libf2c.a in a standard place, with -lf2c -lm
	-- in that order, at the end of the command line, as in
		cc *.o -lf2c -lm
	Source for libf2c is in /netlib/f2c/libf2c.zip, e.g.,

		http://www.netlib.org/f2c/libf2c.zip
*/

#include "f2c.h"


static integer c__3 = 3;
static integer c__1 = 1;
static integer c__9 = 9;
static doublereal c_b23 = .001;
static integer c__5 = 5;
static logical c_true = TRUE_;
static integer c__2 = 2;

/* Subroutine */ int chrg_scorpion__(integer *natom, doublereal *charge, 
	doublereal *radius, doublereal *coorx, doublereal *coory, doublereal *
	coorz, integer *nbead, doublereal *cgchg, doublereal *cgrad, 
	doublereal *cgcox, doublereal *cgcoy, doublereal *cgcoz, doublereal *delgrid);
