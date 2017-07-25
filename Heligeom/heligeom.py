# Original: Chantal Prevost and Benjamin Boyer
# 6 Oct 2015 Charles Robert and Chantal Prevost: Some refactoring, added unittests in Tests:
# 19 Juill 2017 CP : added sequential output, groove width calculation

from __future__ import print_function

import math
import sys
import string

from ptools import (Coord3D, Rigidbody, Atomproperty, MatTrans2screw, Norm, superpose, WritePDB, AttractPairList, Dist)


def ScalProd(a, b):
    return a.x * b.x + a.y * b.y + a.z * b.z


def VectProd(u, v):
    UvectV = Coord3D()
    UvectV.x = u.y * v.z - u.z * v.y
    UvectV.y = u.z * v.x - u.x * v.z
    UvectV.z = u.x * v.y - u.y * v.x
    return UvectV


def distAxis(rig, hp):
    """Computes the distance between the axis and each atom, returns the
    smallest and biggest distances."""
    rigSize = rig.Size()
    vect = Coord3D()
    dmin, dmax = -1, -1

    for i in xrange(0, rigSize):
        c = rig.GetCoords(i)

        vect.x = c.x - hp.point.x
        vect.y = c.y - hp.point.y
        vect.z = c.z - hp.point.z

        d = Norm(VectProd(vect, hp.unitVector))

        if dmin == -1:
            dmin = d
        elif d < dmin:
            dmin = d

        if dmax == -1:
            dmax = d
        elif d > dmax:
            dmax = d
    return dmin, dmax


def residSize(rig):  # CP: this function seems to have no use here : remove ?
    rsize = 0
    temp = -1
    for i in xrange(rig.Size()):
        rid = rig.GetAtomProperty(i).GetResidId()
        if rid != temp:
            temp = rid
            rsize += 1
    return rsize

def getpstart (start,hp,dmin,dmax):
    #project center of mass on axis, so we can have a line to place the position of the sphere point
    ap = Atomproperty()
    m1= start
    cm = m1.FindCenter ()
    v= cm-hp.point
    s=ScalProd(v,hp.unitVector)
    p=(hp.point+ hp.unitVector*s)
    
    # normal to the axis that contains the center of mass of the monomer 
    v2 = cm-p
    v2 = v2.Normalize ()
    
    #midpoint betwen dist min and max to the axis
    pmid = p+v2*(dmin +(dmax-dmin)/2)
    
    
    #midpoint in the groove, at half the pitch
    pitch = hp.normtranslation*(360./abs(math.degrees(hp.angle)))
    pgroove = pmid + (hp.unitVector* (pitch/2))
    
    pstart = Rigidbody()
    pstart.AddAtom(ap,pgroove)
    return pstart


def getpart(groove,n,nbmono):
    inf = Rigidbody()
    for i in xrange(n-1,n+3):
        inf = inf+ groove.SelectChainId(string.ascii_uppercase[i%26]).CreateRigid ()
    sup = Rigidbody()
    for i in xrange(n-2+nbmono,n+2+nbmono):
        sup = sup+ groove.SelectChainId(string.ascii_uppercase[i%26]).CreateRigid ()
    return inf,sup

def groove_width_calculation(hp,mono1):
    #grooves
    nbmono=abs(int(round((360./abs(math.degrees(hp.angle)))+0.5)))
    n = 1
    end = n+nbmono+1
    O = hp.point
    axe =hp.unitVector
    groove = extend(hp,mono1,nbmono*3,False,False)
    start = groove.SelectChainId(string.ascii_uppercase[n]).CreateRigid ()
    dmin,dmax = distAxis(mono1,hp)
    
    nbtot=720
    nb=0
    fic = open("groove.out",'w')
    for i in xrange(n,end):
        #gen point
        inf,sup = getpart(groove,i,nbmono)
        infSize = inf.Size()
        supSize = sup.Size()
        nbpoint= abs(int(math.degrees(hp.angle))*2) 
        for j in xrange(nbpoint):     
            ldist=[]
            start.ABrotate ( O, O+ axe, hp.angle/nbpoint )
            start.Translate( axe * hp.normtranslation/nbpoint )
            for k in xrange(int(round(dmin+(dmax-dmin)/2)),int(round(dmax))):
                pstart = getpstart(start,hp,k,k)

                #get the min dist on the inferior part
                pl=AttractPairList(pstart,inf)
                mindistinf = Dist(pstart.CopyAtom(0),inf.CopyAtom(0))
                for k in xrange(1,infSize):
                    tempdist= Dist(pstart.CopyAtom(0),inf.CopyAtom(k))
                    if tempdist < mindistinf:
                        mindistinf=tempdist
                        
                #the same on the superior part
                pl=AttractPairList (pstart, sup)
                mindistsup = Dist(pstart.CopyAtom(0),sup.CopyAtom(0))
                for k in xrange(1,supSize):
                    tempdist= Dist(pstart.CopyAtom(0),sup.CopyAtom(k))
                    if tempdist < mindistsup:
                        mindistsup=tempdist
                #get the two point on the vector and take the mid size
                ldist.append((mindistinf+mindistsup)/2)
                #print pstart.PrintPDB()
            fic.write(str(nb/2.)+"\t"+str(min(ldist))+"\t"+str(int(round(dmin+(dmax-dmin)/2))+ldist.index(min(ldist)))+"\n")
            nb+=1
      
        fic.close()      


def changeChain(rig, letter):
    rsize = rig.Size()
    for i in xrange(0, rsize):
        at = rig.GetAtomProperty(i)
        at.SetChainId(letter)
        rig.SetAtomProperty(i, at)
    return rig


def extend(hp, mono1, nb, Z=False, seq=False):
    final = Rigidbody()
    monoTest = mono1.SelectAllAtoms().CreateRigid()
    i = 0
    O = hp.point
    axe = hp.unitVector
    if Z is True:
        # align on Z
        # 1 make Z axis, unit prot axis
        at = Atomproperty()

        Zaxis = Rigidbody()
        O = Coord3D(0, 0, 0)
        Zaxis.AddAtom(at, O)
        axe = Coord3D(0, 0, 1)
        Zaxis.AddAtom(at, Coord3D(0, 0, 1))

        Protaxis = Rigidbody()
        Protaxis.AddAtom(at, hp.point)
        Protaxis.AddAtom(at, hp.point + hp.unitVector.Normalize())
        # 2 superpose and get matrix
        m = superpose(Zaxis, Protaxis).matrix
        # 3 apply matrix to rigidbody
        monoTest.ApplyMatrix(m)
    # 4 modify axis
    # extends the pdb structure
    monoTest = changeChain(monoTest, string.ascii_uppercase[i % 26])
    final = final + monoTest
    if seq:
        print(final.PrintPDB())
    i += 1
    for j in xrange(nb - 1):
        monoTest.ABrotate(O, O + axe, hp.angle)
        monoTest.Translate(axe * hp.normtranslation)
        monoTest = changeChain(monoTest, string.ascii_uppercase[i % 26])
        if seq:
            print(monoTest.PrintPDB())
        else: 
            final = final + monoTest
        i += 1
    return final


def heliAnalyze(mono1, mono2, doprint=True):
    """ Calculate and return the screw transformation from mono1 to mono2."""

    hp = MatTrans2screw(superpose(mono2, mono1).matrix)

    if doprint:
        dmin, dmax = distAxis(mono1, hp)

        print("", file=sys.stderr)
        print("axis point:\t\t%6.2f%8.2f%8.2f\n" % (hp.point.x, hp.point.y, hp.point.z) + "axis unit vector:\t%6.2f%8.2f%8.2f\n" % (hp.unitVector.x, hp.unitVector.y, hp.unitVector.z) + "rotation angle:\t %13.2f" % (hp.angle) + " rad   (%0.2f" % (math.degrees(hp.angle)) + " deg) \ntranslation\t\t%6.2f A" % (hp.normtranslation), file=sys.stderr)
        print("", file=sys.stderr)
        print("monomers per turn:\t%6.2f" % (360. / abs(math.degrees(hp.angle))), file=sys.stderr)
        print("pitch:\t\t\t%6.2f A" % (abs(hp.normtranslation*(360./abs(math.degrees(hp.angle))))), file=sys.stderr)

        print("distance to the axis:\t%6.2f (min)%8.2f (max) A" % (dmin, dmax), file=sys.stderr)
        if hp.angle * hp.normtranslation > 0:
            sens = "right-handed"
        else:
            sens = "left-handed"
        print("helix direction : \t " + sens, file=sys.stderr)
        print("", file=sys.stderr)
    return hp


def heliConstruct(mono1, hp, N, Z=False, seq=False, writefile=None):
    """ Construct an N-mer by repeating the screw transformation hp."""
    final = extend(hp, mono1, N, Z, seq)   # if seq, final will only contain one monomer
    if writefile == "print" or writefile == "PRINT":
        # Print to screen
        if not seq:
           print(final.PrintPDB())
    else:
       if writefile is not None:
           # Write to file with name provided
           WritePDB(final,writefile)
    return final


if __name__ == "__main__":

    nargs = len(sys.argv)
    #print(sys.argv)
    if nargs < 3:
        print("usage: heligeom.py monomer1.pdb monomer2.pdb [numberOfNewMonomer] [-Z] [-seq] [-o out.pdb] [-groove]")
        print("")
        print("")
        print("   where  monomer1.pdb and monomer2.pdb are the name of the pdb file of your monomer")
        print("   and numberOfNewMonomer is an optional argument for the number of new monomer you want to add to make a helicoidal structure")
        print("   by default, the new (optional) pdb file is printed on the standard output and the helix parameters are redirected on the error output")
        print("   with the -Z option, the generated pdb file is aligned on the Z axis")
        print("   with the -seq option, the pdb file is written sequentially, which enables generating very long helices without creating memory issues") 
        print("       this option is valid only when printing on the standard output")
        print("   the -o option must be followed by a file name for output")
        print("   the -Z, -seq and -o options are only used if NumberOfNewMonomer is specified")
        print("   the -groove option producess a file groove.out containing groove width values at successive points around the axis separated by 0.5 degrees")

        raise SystemExit

    Z = False
    seq = False
    N = 0
    grvcalc = False
    outputname = None

    if nargs > 3:
        try:
            N = max(0, int(sys.argv[3]))
            outputname = "print"
        except:
            print("Number of monomers must be an integer")
            raise SystemExit

    if nargs > 4:
        ikp = 0
        for iarg in range(4,nargs):
           arg = sys.argv[iarg]
           if arg == "-Z" or arg == "-z":
               Z = True
           elif arg == "-seq":
               seq = True
           elif arg == "-o":
              ikp = iarg 
           elif arg == "-groove":
              grvcalc = True
           elif iarg == ikp + 1:
              outputname = arg
           else:
              print("Unrecognized argument %s" % arg)
              raise SystemExit

    if outputname != "print":
       seq = False

    mono1 = Rigidbody(sys.argv[1])
    mono2 = Rigidbody(sys.argv[2])
    hp = heliAnalyze(mono1, mono2, True)

    if N > 0:
        # Construct and output PDB to screen
        final = heliConstruct(mono1, hp, N, Z,seq, outputname)

    if grvcalc :
        groove_width_calculation(hp,mono1)
