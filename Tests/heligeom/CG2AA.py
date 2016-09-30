import sys
from ptools import *

#check the arguments
if len (sys.argv) != 2:
    print """ERROR: incorrect number of arguments ( expected: 1 )
usage: CG2AA.py CGfilename
""" 
    sys.exit(0)

#translate the DNA in all atom representation
dna = DNA ("../data/pb.aa.pdb",sys.argv[1])

print dna.printPDB() 

