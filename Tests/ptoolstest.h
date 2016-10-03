#include <coord3d.h>
#include <ptools.h>

#include <cstdlib>

#include <cxxtest/TestSuite.h>

using namespace std;
using namespace PTools;


static const std::string TEST_1FIN_R_PDB = "data/1FIN_r.pdb";


class TestCoord3D : public CxxTest::TestSuite
{
Coord3D coo1, coo2, coo3;


public:
        void setUp() {
                this->coo1 = Coord3D(3.0, 4.0, 5.0);
                coo2 = Coord3D(1.0, 2.0, 7.5);
        }

        void testPlusOperator()
        {
                coo3 = coo1 + coo2 ;
                TS_ASSERT_EQUALS(coo3.x, 4.0);
                TS_ASSERT_EQUALS(coo3.y, 6.0);
                TS_ASSERT_EQUALS(coo3.z, 12.5);

        }


        void testMinusOperator(){
                coo3 = coo1 - coo2;
                TS_ASSERT_EQUALS(coo3.x, 2.0);
                TS_ASSERT_EQUALS(coo3.y, 2.0);
                TS_ASSERT_EQUALS(coo3.z, -2.5);
        }

        void testPlusEqualOperator()
        {
                coo3 = Coord3D(coo1);
                coo3 += coo2;
                TS_ASSERT_EQUALS(coo3.x, 4.0);
                TS_ASSERT_EQUALS(coo3.y, 6.0);
                TS_ASSERT_EQUALS(coo3.z, 12.5);
        }


};


class TestRigidbody: public CxxTest::TestSuite
{
public:

Rigidbody r,s, r2;
Coord3D A, B;



    void setUp()
    {
        r =  Rigidbody(TEST_1FIN_R_PDB);
    }


    void testCopy()
    {
        s = Rigidbody(r);
        TS_ASSERT_EQUALS(s.Size(), r.Size())
        TS_ASSERT_EQUALS(r.FindCenter(), s.FindCenter());
    }


    void testSize()
    {        TS_ASSERT_EQUALS(r.Size(), 2365);
    }

    void testSetAtom()
    {
        Atom atom (r.CopyAtom(3) ) ;
        atom.coords = Coord3D(3,4,5);
        r.SetAtom(3,atom);
        //#test to see if the mofification worked:
        Atom atom2 = r.CopyAtom(3);
        TS_ASSERT( Norm2(atom2.coords - Coord3D(3,4,5) ) < 1e6 );

    }


    void testUnsafeGetCoords()
    {
//         """in principle GetCoords(i,co) and unsafeGetCoords(i,co) should
//         lead to the exact same coordinates if a sync has been done before
//         calling the 'unsafe' version"""
        r2 = Rigidbody(TEST_1FIN_R_PDB);
        A = Coord3D(4.23, 5.72, 99.02);
        B = Coord3D(1.23, 6.33, 1.234);
        r.ABrotate(A,B, 2.2345);
        r2.ABrotate(A,B, 2.2345);
        r.Translate(Coord3D(34.23, 123.45,11.972));
        r2.Translate(Coord3D(34.23, 123.45,11.972));

        r2.syncCoords();
//         #same rotation and translation for r and r2: should have exact same coordinates

        for (int i=0; i<r.Size(); i++)
        {
            Coord3D co1 = Coord3D();
            Coord3D co2 = Coord3D();
            co1 = r.GetCoords(i);
            r2.unsafeGetCoords(i,co2);
            TS_ASSERT_EQUALS(co1,co2);
        }
    }

};


class TestBasicMoves: public CxxTest::TestSuite
{
public:

Rigidbody rigid1, rigid2, rigid3;

    void setUp()
    {
        rigid1=Rigidbody(TEST_1FIN_R_PDB);
        rigid2=Rigidbody(rigid1);
        rigid3=Rigidbody(rigid2);
    }

    void testBasicRmsd()
    {
        Rigidbody rigtmp(rigid1);
        TS_ASSERT_EQUALS(Rmsd(rigid1, rigid1), 0.0);
        rigid1.Translate(Coord3D(4,0,0));
        TS_ASSERT_EQUALS(Rmsd(rigtmp, rigid1), 4);
    }

    void testTranslation1()
    {
        Coord3D CoM1 = rigid1.FindCenter() ;
        rigid1.Translate(Coord3D(3.0, -55.67, 1));
        Coord3D CoM2 = rigid1.FindCenter();
        Coord3D diff=CoM2-CoM1;
        TS_ASSERT( Norm2(diff + Coord3D(-3.0, 55.67, -1.0)) < 1e-6);
        rigid1.Translate(Coord3D(-3.0, 55.67, -1.0));   //# translate back
        TS_ASSERT(Rmsd(rigid1, rigid2) < 1e-6);
    }

    void testTranslation2(){
        Coord3D vec1 = Coord3D (-123.54, 45.62, -99.003);
        Coord3D vec2 = Coord3D (36.3125, 2.78, -36.378);
        rigid2.Translate(vec1+vec2);
        rigid2.Translate(vec1-vec2);
        rigid2.Translate(Coord3D() - 2*vec1) ; //  #should be a global null translation + round error
        TS_ASSERT(Rmsd(rigid2, rigid3) < 1e-6);
    }


};



class TestCoordsArray: public CxxTest::TestSuite
{

public:
    CoordsArray c;
    Coord3D coo1, coo2, tr;

    void setUp()
    {
        c = CoordsArray();
        coo1 = Coord3D(3.0, 4.0, 5.0);
        coo2 = Coord3D(1.0, 2.0, 7.5);
        c.AddCoord(coo1);
        c.AddCoord(coo2);
        //c = c;
        tr = Coord3D(3.0, 4.5, -3.0);
    }
    void  testSize()
    {
        TS_ASSERT(c.Size() == 2);
    }
     
    void  testGetAtom()
    {
        Coord3D c1 ;
        c.GetCoords(0, c1);
        TS_ASSERT(  Norm2(c1 - Coord3D(3.0, 4.0, 5.0))<1e-6 );
    }

    void  testBasicTranslation()
    {
        c.Translate(tr);
        Coord3D c1;
        Coord3D c2;
        c.GetCoords(0, c1 );
        c.GetCoords(1, c2 );
        TS_ASSERT(c1 == Coord3D(6.0, 8.5, 2.0));
    }

    void  testSetCoords()
    {
        /*"""brief explanation:
        For lazy evaluation, corrdinates are stored unrotated/untranslated along
        with the rotation/translation 4x4 matrix. When user set the coordinates,
        this means: 'change the current coordinates of atom i' and not 'change
        the initial coordinates of atom i' so here we check that this is the case"""*/
        c.Translate(tr); //#do some translation
        c.AttractEulerRotate(2.0,4.0,5.0); // # do a rotation
        Coord3D co = Coord3D(3,2,1); // #new coordinates to be added
        c.SetCoords(0,co);
        Coord3D co2=Coord3D();
        c.GetCoords(0,co2); // #get the coordinates back
        TS_ASSERT(Norm2(co-co2)<1.0e-6);
    }

};



class Random
{


public:
void seed(int i)
{
 srand(i);
}

double random()
{
double f =  ((double) rand()/(double)RAND_MAX);
return f;
}


};




class TestSuperposition: public CxxTest::TestSuite
{
public:

Random random;
Rigidbody prot1;



    void setUp()
    {
        prot1 = Rigidbody(TEST_1FIN_R_PDB);
        random.seed(123);
    }

    void testTransRot()
    {
        double x,y,z,a,b,c;

        Rigidbody prot2(prot1);


        for (int i=0; i<20; i++)
        {
//              #random translation coordinates:
            x = (random.random()-0.5)*50.0;
            y = (random.random()-0.5)*50.0;
            z = (random.random()-0.5)*50.0;
            prot2.Translate(Coord3D(x,y,z));
            a = (random.random()-0.5)*50.0;
            b = (random.random()-0.5)*50.0;
            c = (random.random()-0.5)*50.0;
            prot2.AttractEulerRotate(a,b,c);

            Superpose_t sup = superpose(prot1,prot2); //# superpose(reference, mobile)
            Matrix matrix = sup.matrix;
            prot2.ApplyMatrix(matrix);
            TS_ASSERT(Rmsd(prot2,prot1)<1e-6);

        }

   }

};





double randfloat()
{
    return (double) rand() / (double) RAND_MAX ;
}

double rdrange(double a, double b)
{
    return randfloat()*(b-a)+a;
}

Coord3D rdCoord(double a, double b)
{
    double x = rdrange(a,b);
    double y = rdrange(a,b);
    double z = rdrange(a,b);
    return Coord3D(x,y,z);
}

class TestRot: public CxxTest::TestSuite
{


public:
    void testTransRot()
    {

        srand(time(NULL));

        for (int nrepet = 0; nrepet<50; nrepet++)
        {

            Rigidbody r1(TEST_1FIN_R_PDB);
            Rigidbody r2(r1);
            double x = (randfloat()-0.5)*50.0;
            double y = (randfloat()-0.5)*50.0;
            double z = (randfloat()-0.5)*50.0;

            r2.ABrotate(rdCoord(-20,20), rdCoord(-10,10), rdrange(-3.1415926,3.1415926) );

            r2.Translate(Coord3D(x,y,z));

            Superpose_t s = superpose(r1,r2);

            r2.ApplyMatrix(s.matrix);
            TS_ASSERT( Rmsd(r1,r2) < 1e-4 );


        }

    }
    void testVissage()
    {

        for(int i=0; i<1000; i++)
        {
        Rigidbody r1(TEST_1FIN_R_PDB);
        Rigidbody r2(r1);

        double x = (randfloat()-0.5)*50.0;
        double y = (randfloat()-0.5)*50.0;
        double z = (randfloat()-0.5)*50.0;

        r2.ABrotate(rdCoord(-20,20), rdCoord(-10,10), rdrange(-3.1415926,3.1415926) );

        r2.Translate(Coord3D(x,y,z));

        Superpose_t  s = superpose(r1,r2);

        Screw v =  MatTrans2screw(s.matrix);
//        v.Print();

        Rigidbody r3;
        r3.ABrotate(v.point, v.point+v.unitVector, v.angle);
        r3.Translate(v.normtranslation*v.unitVector);


//        r3.GetMatrix().Print();

//        s.matrix.Print();

        if(!s.matrix.almostEqual(r3.GetMatrix(),1e-2))
           {
               cout << "(((((((((((((((((\n";
               s.matrix.Print();
               cout << "\n";
               r3.GetMatrix().Print();
               cout << v.angle << "\n";

           }


         TS_ASSERT(s.matrix.almostEqual(r3.GetMatrix(),1e-2));


        }

    }












};










