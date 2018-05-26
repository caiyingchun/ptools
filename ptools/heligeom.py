
"""PTools heligeom."""

from __future__ import print_function

import math
import string
import sys

import ptools


HELI_ANALYZE_TEMPLATE = """\
axis point:           %(axis_point)s
axis unit vector:     %(axis_unit_vector)s
rotation angle:       %(angle)6.2f rad (%(angle_deg).2f deg)
translation:          %(normtranslation)6.2f A

monomers per turn:    %(monomers_per_turn)6.2f
pitch:                %(pitch)6.2f A
distance to the axis: %(dist_to_axis_min)6.2f (min) %(dist_to_axis_max)6.2f (max) A
helix direction:      %(direction)s
"""

def distance(a, b):
    """Calculate the distance between two ptools.Coord3D."""
    return ptools.norm(ptools.crossproduct(a, b))

def dist_axis(rig, hp):
    """Return the minimal and maximal distances between the axis and the
    rigid body."""
    natoms = len(rig)
    all_distances = [distance(rig.get_coords(i) - hp.point, hp.unit_vector)
                     for i in xrange(0, natoms)]
    return min(all_distances), max(all_distances)

def get_pstart(start, hp, dmin, dmax):
    # project center of mass on axis, so we can have a line to place the
    # position of the sphere point
    ap = ptools.Atomproperty()
    m1 = start
    cm = m1.find_center()
    v = cm - hp.point
    s = ptools.dotproduct(v, hp.unit_vector)
    p = (hp.point + hp.unit_vector * s)

    # normal to the axis that contains the center of mass of the monomer
    v2 = cm - p
    v2 = v2.normalize()

    # midpoint betwen dist min and max to the axis
    pmid = p + v2 * (dmin + (dmax - dmin) / 2)

    # midpoint in the groove, at half the pitch
    pitch = hp.normtranslation * (360. / abs(math.degrees(hp.angle)))
    pgroove = pmid + (hp.unit_vector * (pitch / 2))

    pstart = ptools.Rigidbody()
    pstart.add_atom(ptools.Atom(ap, pgroove))
    return pstart

def get_part(groove, n, nbmono):
    inf = ptools.Rigidbody()
    for i in xrange(n - 1, n + 3):
        inf = inf + groove.select_chain_id(string.ascii_uppercase[i % 26]).create_rigid()
    sup = ptools.Rigidbody()
    for i in xrange(n - 2 + nbmono, n + 2 + nbmono):
        sup = sup + groove.select_chain_id(string.ascii_uppercase[i % 26]).create_rigid()
    return inf, sup

def groove_width_calculation(hp, mono1):
    # grooves
    nbmono = abs(int(round((360. / abs(math.degrees(hp.angle))) + 0.5)))
    n = 1
    end = n + nbmono + 1
    O = hp.point
    axe = hp.unit_vector
    groove = extend(hp, mono1, nbmono * 3, False, False)
    start = groove.select_chain_id(string.ascii_uppercase[n]).create_rigid()
    dmin, dmax = dist_axis(mono1, hp)

    nb = 0
    fic = open('groove.out', 'w')
    for i in xrange(n, end):
        # gen point
        inf, sup = get_part(groove, i, nbmono)
        infSize = inf.size()
        supSize = sup.size()
        nbpoint = abs(int(math.degrees(hp.angle)) * 2)
        for j in xrange(nbpoint):
            ldist = []
            start.ab_rotate(O, O + axe, hp.angle / nbpoint)
            start.translate(axe * hp.normtranslation / nbpoint)
            for k in xrange(int(round(dmin + (dmax - dmin) / 2)), int(round(dmax))):
                pstart = get_pstart(start, hp, k, k)

                # get the min dist on the inferior part
                mindistinf = ptools.dist(pstart.copy_atom(0), inf.copy_atom(0))
                for k in xrange(1, infSize):
                    tempdist = ptools.dist(pstart.copy_atom(0), inf.copy_atom(k))
                    if tempdist < mindistinf:
                        mindistinf = tempdist

                # the same on the superior part
                mindistsup = ptools.dist(pstart.copy_atom(0), sup.copy_atom(0))
                for k in xrange(1, supSize):
                    tempdist = ptools.dist(pstart.copy_atom(0), sup.copy_atom(k))
                    if tempdist < mindistsup:
                        mindistsup = tempdist
                # get the two point on the vector and take the mid size
                ldist.append((mindistinf + mindistsup) / 2)
            fic.write(str(nb / 2.) + "\t" + str(min(ldist)) + "\t" + str(int(round(dmin + (dmax - dmin) / 2)) + ldist.index(min(ldist))) + "\n")
            nb += 1
    fic.close()

def change_chain(rig, letter):
    rsize = rig.size()
    for i in xrange(0, rsize):
        at = rig.get_atom_property(i)
        at.chain_id = letter
        rig.set_atom_property(i, at)
    return rig

def extend(hp, mono1, nb, Z=False, seq=False):
    final = ptools.Rigidbody()
    monoTest = mono1.select_all_atoms().create_rigid()
    i = 0
    O = hp.point
    axe = hp.unit_vector
    if Z is True:
        # align on Z
        # 1 make Z axis, unit prot axis
        at = ptools.Atomproperty()

        Zaxis = ptools.Rigidbody()
        O = ptools.Coord3D(0, 0, 0)
        Zaxis.add_atom(ptools.Atom(at, O))
        axe = ptools.Coord3D(0, 0, 1)
        Zaxis.add_atom(ptools.Atom(at, ptools.Coord3D(0, 0, 1)))

        Protaxis = ptools.Rigidbody()
        Protaxis.add_atom(ptools.Atom(at, hp.point))
        Protaxis.add_atom(ptools.Atom(at, hp.point + hp.unit_vector.normalize()))
        # 2 superpose and get matrix
        m = ptools.superpose(Zaxis, Protaxis).matrix
        # 3 apply matrix to rigidbody
        monoTest.apply_matrix(m)
    # 4 modify axis
    # extends the pdb structure
    monoTest = change_chain(monoTest, string.ascii_uppercase[i % 26])
    final = final + monoTest
    if seq:
        print(final.print_pdb())
    i += 1
    for j in xrange(nb - 1):
        monoTest.ab_rotate(O, O + axe, hp.angle)
        monoTest.translate(axe * hp.normtranslation)
        monoTest = change_chain(monoTest, string.ascii_uppercase[i % 26])
        if seq:
            print(monoTest.print_pdb())
        else:
            final = final + monoTest
        i += 1
    return final

def heli_analyze(mono1, mono2, doprint=True):
    """ Calculate and return the screw transformation from mono1 to mono2 (Rigidbodies)."""
    def coord3d_to_str(v):
        return '{:6.2f}{:8.2f}{:8.2f}'.format(v.x, v.y, v.z)

    hp = ptools.mat_trans_to_screw(ptools.superpose(mono2, mono1).matrix)

    if doprint:
        dmin, dmax = dist_axis(mono1, hp)
        rotation_angle_degrees = math.degrees(hp.angle)
        print("hp.angle is", hp.angle)
        if abs(hp.angle) > 0.0:
            pitch = abs(hp.normtranslation * (360. / abs(rotation_angle_degrees)))
            monomers_per_turn = 360. / abs(rotation_angle_degrees)
        else:
            # Attention: zeros here indicate NaN (divide by zero)
            pitch = 0.0
            monomers_per_turn = 0.0
        direction = "right-handed" if hp.angle * hp.normtranslation > 0 else "left-handed"

        s = HELI_ANALYZE_TEMPLATE % {
            'axis_point': coord3d_to_str(hp.point),
            'axis_unit_vector': coord3d_to_str(hp.unit_vector),
            'angle': hp.angle,
            'angle_deg': rotation_angle_degrees,
            'normtranslation': hp.normtranslation,
            'monomers_per_turn': monomers_per_turn,
            'pitch': pitch,
            'dist_to_axis_min': dmin,
            'dist_to_axis_max': dmax,
            'direction': direction
        }

        print(s, file=sys.stderr)
    return hp

def heli_construct(mono1, hp, N, Z=False, seq=False, writefile=None):
    """ Construct an N-mer by repeating the screw transformation hp."""
    final = extend(hp, mono1, N, Z, seq)   # if seq, final will only contain one monomer
    if writefile == "print" or writefile == "PRINT":
        # Print to screen
        if not seq:
            print(final.print_pdb())
    else:
        if writefile is not None:
            # Write to file with name provided
            ptools.write_pdb(final, writefile)
    return final

