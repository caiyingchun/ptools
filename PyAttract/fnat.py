#!/usr/bin/env python

import sys

from ptools import AttractPairList, AttractRigidbody, Rigidbody


def contact(receptor, ligand, cutoff=7):
    """return residues in interaction, use ptools::pairlist"""

    if isinstance(receptor, Rigidbody):
        receptor = AttractRigidbody(receptor)

    if isinstance(ligand, Rigidbody):
        ligand = AttractRigidbody(ligand)

    resnblig = []
    for i in range(len(ligand)):
        at = ligand.CopyAtom(i)
        resnblig.append(at.residId)
    resnbrec = []
    for j in range(len(receptor)):
        at = receptor.CopyAtom(j)
        resnbrec.append(at.residId)

    pl = AttractPairList(receptor, ligand, cutoff)
    contactnat = set()  # residue list in interaction

    for i in range(len(pl)):
        ap = pl[i]
        contactnat.add((resnbrec[ap.atrec], resnblig[ap.atlig]))

    return contactnat


def fnat(receptor, ligcrist, ligprobe):
    """return native fraction (fnat)"""
    corig = contact(receptor, ligcrist)
    cnew = contact(receptor, ligprobe)
    intersect = corig & cnew
    f = float(len(intersect)) / float(len(corig))
    return f


def main():
    if len(sys.argv) < 4:
        print "usage:  fnat.py receptor lig_ref lig"
        sys.exit(1)
    recname = sys.argv[1]
    ligname = sys.argv[2]
    ligname2 = sys.argv[3]
    lig = AttractRigidbody(ligname)
    lig2 = AttractRigidbody(ligname2)
    rec = AttractRigidbody(recname)

    FNAT = fnat(rec, lig, lig2)
    print FNAT


if __name__ == "__main__":
    main()
