# -*- coding: utf-8 -*-

import os
import sys

from _ptools import (ADNA, Atom, AtomPair, AtomSelection, Atomproperty,
                     AttractForceField1, AttractForceField2, AttractPairList,
                     AttractRigidbody, BDNA, BaseAttractForceField, BasePair,
                     Coord3D, CoordsArray, DNA, dist, dist2, Lbfgs, Matrix,
                     MatTrans2screw, Movement, Rigidbody, Rise, Rmsd, Roll,
                     ScorpionForceField, Screw, Shift, Slide,
                     Superpose_t, Surface, Tilt, Twist, Version, write_pdb,
                     crossproduct, dotproduct, norm, norm2, str_to_atom,
                     superpose)


DATA_DIR = os.path.join(sys.prefix, 'share', 'ptools', 'data')


from . import io
from . import exceptions
from . import forcefield
from . import reduce
from . import docking


__version__ = '2.0.0'


one_letter_residue_dict = {
    "ALA": "A",
    "CYS": "C",
    "ASP": "D",
    "GLU": "E",
    "PHE": "F",
    "GLY": "G",
    "HIS": "H",
    "HIE": "H",
    "HSP": "H",
    "HSE": "H",
    "HSD": "H",
    "ILE": "I",
    "LYS": "K",
    "LEU": "L",
    "MET": "M",
    "ASN": "N",
    "PRO": "P",
    "GLN": "Q",
    "ARG": "R",
    "SER": "S",
    "THR": "T",
    "VAL": "V",
    "TRP": "W",
    "TYR": "Y",
    "---": "-",
}


def rigidToSeq(rigid):
    """use residu names from the structure to extract the sequence
       This function needs CA atoms to be present. A missing CA atom will
       result in a missing letter in the sequence.
    """
    rca = rigid.CA().create_rigid()  # restrict to the CA atoms.
    seq = []
    for i in range(len(rca)):
        at = rca.CopyAtom(i)
        seq.append(one_letter_residue_dict[at.resid_type])

    return "".join(seq)


def getPDB(pdbname):
    import urllib2
    pdb = urllib2.urlopen("http://www.rcsb.org/pdb/files/%s.pdb" % pdbname)
    rigid = Rigidbody(pdb)
    return rigid
