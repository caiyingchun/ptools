
"""heligeom_cmd - PTools heligeom command."""

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


def create_subparser(parent):
    parser = parent.add_parser('heligeom', help=__doc__)
    parser.set_defaults(func=run)

    parser.add_argument('monomer1.pdb',
                        help="first monomer input file")
    parser.add_argument('monomer2.pdb',
                        help="second monomer input file")
    parser.add_argument('-n', '--number-of-new-monomers', type=int, default=0,
                        help="number of new monomer you want to add to make "
                             "a helicoidal structure")
    parser.add_argument('-o', '--output', default='print',
                        help="output file name")
    parser.add_argument('-Z', '--align-on-z', action='store_true',
                        help="align output PDB on the Z-axis")
    parser.add_argument('-s', '--seq', action='store_true',
                        help="the pdb file is written sequentially, which "
                        "enables generating very long helices without "
                        "creating memory issues. "
                        "This option is valid only when printing on "
                        "the standard output")
    parser.add_argument('--groove', action='store_true',
                        help="producess a file groove.out containing groove "
                             "width values at successive points around the "
                             "axis separated by 0.5 degrees")


def check_args(args):
    """Check input files exists and command-line arguments
    self-compatibility."""

    # Check monomer input PDB files exist.
    ptools.io.check_file_exists(getattr(args, 'monomer1.pdb'))
    ptools.io.check_file_exists(getattr(args, 'monomer2.pdb'))

    # Check command-line arguments self-compatibility.
    if args.align_on_z and not args.number_of_new_monomers:
        ptools.io.error("Option '--align-on-z only valid in conjunction with "
                        "--number-of-new-monomers")

    if args.seq and not args.number_of_new_monomers:
        ptools.io.error("Option '--seq only valid in conjunction with "
                        "--number-of-new-monomers")

    if args.output and not args.number_of_new_monomers:
        ptools.io.error("Option '--output only valid in conjunction with "
                        "--number-of-new-monomers")

    if args.seq and args.output != 'print':
        ptools.io.error("Option '--seq only valid when --output is 'print'")


def distance(a, b):
    """Calculate the distance between two ptools.Coord3D."""
    return ptools.norm(ptools.cross_product(a, b))


def distAxis(rig, hp):
    """Return the minimal and maximal distances between the axis and the
    rigid body."""
    natoms = len(rig)
    all_distances = [distance(rig.get_coords(i) - hp.point, hp.unitVector)
                     for i in xrange(0, natoms)]
    return min(all_distances), max(all_distances)


def getpstart(start, hp, dmin, dmax):
    # project center of mass on axis, so we can have a line to place the
    # position of the sphere point
    ap = ptools.Atomproperty()
    m1 = start
    cm = m1.find_center()
    v = cm - hp.point
    s = ptools.dot_product(v, hp.unitVector)
    p = (hp.point + hp.unitVector * s)

    # normal to the axis that contains the center of mass of the monomer
    v2 = cm - p
    v2 = v2.Normalize()

    # midpoint betwen dist min and max to the axis
    pmid = p + v2 * (dmin + (dmax - dmin) / 2)

    # midpoint in the groove, at half the pitch
    pitch = hp.normtranslation * (360. / abs(math.degrees(hp.angle)))
    pgroove = pmid + (hp.unitVector * (pitch / 2))

    pstart = ptools.Rigidbody()
    pstart.add_atom(ptools.Atom(ap, pgroove))
    return pstart


def getpart(groove, n, nbmono):
    inf = ptools.Rigidbody()
    for i in xrange(n - 1, n + 3):
        inf = inf + groove.select_chainid(string.ascii_uppercase[i % 26]).create_rigid()
    sup = ptools.Rigidbody()
    for i in xrange(n - 2 + nbmono, n + 2 + nbmono):
        sup = sup + groove.select_chainid(string.ascii_uppercase[i % 26]).create_rigid()
    return inf, sup


def groove_width_calculation(hp, mono1):
    # grooves
    nbmono = abs(int(round((360. / abs(math.degrees(hp.angle))) + 0.5)))
    n = 1
    end = n + nbmono + 1
    O = hp.point
    axe = hp.unitVector
    groove = extend(hp, mono1, nbmono * 3, False, False)
    start = groove.select_chainid(string.ascii_uppercase[n]).create_rigid()
    dmin, dmax = distAxis(mono1, hp)

    nb = 0
    fic = open('groove.out', 'w')
    for i in xrange(n, end):
        # gen point
        inf, sup = getpart(groove, i, nbmono)
        infsize = inf.size()
        supsize = sup.size()
        nbpoint = abs(int(math.degrees(hp.angle)) * 2)
        for j in xrange(nbpoint):
            ldist = []
            start.rotate(O, O + axe, hp.angle / nbpoint)
            start.translate(axe * hp.normtranslation / nbpoint)
            for k in xrange(int(round(dmin + (dmax - dmin) / 2)), int(round(dmax))):
                pstart = getpstart(start, hp, k, k)

                # get the min dist on the inferior part
                mindistinf = ptools.dist(pstart.copy_atom(0), inf.copy_atom(0))
                for k in xrange(1, infsize):
                    tempdist = ptools.dist(pstart.copy_atom(0), inf.copy_atom(k))
                    if tempdist < mindistinf:
                        mindistinf = tempdist

                # the same on the superior part
                mindistsup = ptools.dist(pstart.copy_atom(0), sup.copy_atom(0))
                for k in xrange(1, supsize):
                    tempdist = ptools.dist(pstart.copy_atom(0), sup.copy_atom(k))
                    if tempdist < mindistsup:
                        mindistsup = tempdist
                # get the two point on the vector and take the mid size
                ldist.append((mindistinf + mindistsup) / 2)
            fic.write(str(nb / 2.) + "\t" + str(min(ldist)) + "\t" + str(int(round(dmin + (dmax - dmin) / 2)) + ldist.index(min(ldist))) + "\n")
            nb += 1
    fic.close()


def changeChain(rig, letter):
    rsize = rig.size()
    for i in xrange(0, rsize):
        at = rig.get_atom_property(i)
        at.chainId = letter
        rig.set_atom_property(i, at)
    return rig


def extend(hp, mono1, nb, Z=False, seq=False):
    final = ptools.Rigidbody()
    monoTest = mono1.select_all_atoms().create_rigid()
    i = 0
    O = hp.point
    axe = hp.unitVector
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
        Protaxis.add_atom(ptools.Atom(at, hp.point + hp.unitVector.Normalize()))
        # 2 superpose and get matrix
        m = ptools.superpose(Zaxis, Protaxis).matrix
        # 3 apply matrix to rigidbody
        monoTest.apply_matrix(m)
    # 4 modify axis
    # extends the pdb structure
    monoTest = changeChain(monoTest, string.ascii_uppercase[i % 26])
    final = final + monoTest
    if seq:
        print(final.print_pdb())
    i += 1
    for j in xrange(nb - 1):
        monoTest.rotate(O, O + axe, hp.angle)
        monoTest.translate(axe * hp.normtranslation)
        monoTest = changeChain(monoTest, string.ascii_uppercase[i % 26])
        if seq:
            print(monoTest.print_pdb())
        else:
            final = final + monoTest
        i += 1
    return final


def heliAnalyze(mono1, mono2, doprint=True):
    """ Calculate and return the screw transformation from mono1 to mono2."""
    def coord3d_to_str(v):
        return '{:6.2f}{:8.2f}{:8.2f}'.format(v.x, v.y, v.z)

    hp = ptools.mat44_to_screw(ptools.superpose(mono2, mono1).matrix)

    if doprint:
        dmin, dmax = distAxis(mono1, hp)
        rotation_angle_degrees = math.degrees(hp.angle)
        pitch = abs(hp.normtranslation * (360. / abs(rotation_angle_degrees)))
        direction = "right-handed" if hp.angle * hp.normtranslation > 0 else "left-handed"

        s = HELI_ANALYZE_TEMPLATE % {
            'axis_point': coord3d_to_str(hp.point),
            'axis_unit_vector': coord3d_to_str(hp.unitVector),
            'angle': hp.angle,
            'angle_deg': rotation_angle_degrees,
            'normtranslation': hp.normtranslation,
            'monomers_per_turn': 360. / abs(rotation_angle_degrees),
            'pitch': pitch,
            'dist_to_axis_min': dmin,
            'dist_to_axis_max': dmax,
            'direction': direction
        }

        print(s, file=sys.stderr)
    return hp


def heliConstruct(mono1, hp, N, Z=False, seq=False, writefile=None):
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


def run(args):
    check_args(args)
    monomer1 = getattr(args, 'monomer1.pdb')
    monomer2 = getattr(args, 'monomer2.pdb')

    N = args.number_of_new_monomers

    mono1 = ptools.Rigidbody(monomer1)
    mono2 = ptools.Rigidbody(monomer2)
    hp = heliAnalyze(mono1, mono2, True)

    if N > 0:
        # Construct and output PDB to screen
        heliConstruct(mono1, hp, N, args.align_on_z, args.seq, args.output)

    if args.groove:
        groove_width_calculation(hp, mono1)
