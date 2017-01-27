
"""PTools attract command."""


from __future__ import print_function

import base64
import bz2
import datetime
import math

import ptools


class Rotation:

    class _Rot:
        ssi = 0.0
        phi = 0.0
        rot = 0.0

        def __init__(self, ssii, phii, roti):
            self.ssi = ssii
            self.phi = phii
            self.rot = roti

    def read_rotdat(self):
        self.zwopi = 2.0 * 3.14159265
        self.NbRotByTrans = 0
        self.theta = []
        self.nphi = []
        # read theta,phi,rot data
        rotdat = open('rotation.dat', 'r')
        line = rotdat.readline().split()
        self.ntheta = int(line[0])
        self.nrot = int(line[1])
        print("ntheta, nrot: {} {}".format(self.ntheta, self.nrot))
        for i in range(self.ntheta):
            line = rotdat.readline().split()
            self.theta.append(float(line[0]))
            self.nphi.append(int(line[1]))
            self.NbRotByTrans = self.NbRotByTrans + self.nphi[i] * self.nrot
            self.theta[i] = self.zwopi * self.theta[i] / 360.0
            print(self.theta[i], self.nphi[i])
        rotdat.close()
        self._rot = []

        print("{} rotations by translation".format(self.NbRotByTrans))

        for kkk in range(self.ntheta):
            ssii = self.theta[kkk]
            phii = self.zwopi / self.nphi[kkk]
            for jjj in range(self.nphi[kkk]):
                phiii = (jjj + 1) * phii
                for iii in range(self.nrot):
                    roti = (iii + 1) * self.zwopi / self.nrot
                    self._rot.append((phiii, ssii, roti))

    def __init__(self):
        self.read_rotdat()

    def __iter__(self):
        return self._rot.__iter__()


class Translation:
    def __init__(self):
        self.translation_dat = ptools.Rigidbody("translation.dat")
        print("Reading {} translations from translation.dat".format(len(self.translation_dat)))

    def __iter__(self):
        self.i = 0
        return self

    def next(self):
        if (self.i == len(self.translation_dat)):
            raise StopIteration
        coord = self.translation_dat.getCoords(self.i)
        self.i += 1
        return [self.i, coord]


def compress_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    compressed = bz2.compress(content)
    encoded = base64.b64encode(compressed)
    return "compressed {} : \"{}\"".format(filename, encoded)


def surreal(i):
    return i


def rmsdca(l1, l2):
    """Return the RMSD between the alpha-carbone atom of two RigidBody
    instances."""
    return ptools.Rmsd(l1.CA().CreateRigid(), l2.CA().CreateRigid())


def create_subparser(parent):
    parser = parent.add_parser('attract', help=__doc__)
    parser.set_defaults(func=run)
    parser.add_argument('-r', '--receptor', dest='receptor_name', required=True,
                        help="name of the receptor file")
    parser.add_argument('-l', '--ligand', dest='ligand_name', required=True,
                        help="name of the ligand file")
    parser.add_argument('--ref', dest='reffile',
                        help="reference ligand for rmsd")
    parser.add_argument('--start1', action='store_true',
                        help="(only useful with -t), use 1 for the first "
                             "translation point")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--single', action='store_true',
                       help="single minimization mode")
    group.add_argument('-t', '--translation', type=int, dest='transnb',
                       default=0,
                       help="translation number (distributed mode) starting "
                            "from 0 for the first one!")


def run(args):
    print("""
**********************************************************************
**                                                                  **
**                ATTRACT  (Python edition)                         **
**                based on the PTools library                       **
**                                                                  **
**********************************************************************
PTools revision {}

""".format(ptools.__version__))

    time_start = datetime.datetime.now()
    print("Start time:", time_start)

    print("Reading parameters file: attract.inp")
    nbminim, lignames, minimlist, rstk = ptools.io.read_attract_parameters("attract.inp")
    print("{} series of minimizations".format(nbminim))
    print("rstk = ", rstk)

    ff_name = ptools.io.check_ff_version_match(args.receptor_name, args.ligand_name)
    ff_specs = ptools.forcefield.PTOOLS_FORCEFIELDS[ff_name]

    # Load receptor and ligand.
    rec = ptools.AttractRigidbody(args.receptor_name)
    lig = ptools.AttractRigidbody(args.ligand_name)
    print("Read receptor (fixed): {} with {} particules".format(args.receptor_name, len(rec)))
    print("Read ligand (mobile): {} with {} particules".format(args.ligand_name, len(lig)))

    # Save all minimization variables to trajectory file.
    trjname = 'minimization.trj'
    if args.single:
        ftraj = open(trjname, 'wt')

    if args.reffile:
        ref = ptools.Rigidbody(args.reffile)
        print("Read reference file: {} with {} particules".format(args.reffile, len(ref)))
        refca = ref.CA()
        if len(refca) == 0:  # No C alpha atom, ligand is probably a dna
            Rmsd_alias = ptools.Rmsd
            print("No Calpha atom found for ligand (DNA?). RMSD will be "
                  "calculated on all grains")
        else:
            Rmsd_alias = rmsdca

    if not args.single:
        # Systematic docking with default translations and rotations.
        # Check for rotation.dat and translation.dat.
        ptools.io.check_file_exists('rotation.dat', "rotation file 'rotation.dat' is required.")
        ptools.io.check_file_exists('translation.dat', "translation file 'translation.dat' is required.")
        translations = Translation()
        rotations = Rotation()
    else:
        # creates dummy translation and rotation
        print("Single mode simulation")
        translations = [[1, lig.FindCenter()]]
        rotations = [(0, 0, 0)]

    printFiles = True
    # option -t used: define the selected translation
    transnb = args.transnb
    if args.transnb:
        # check for rotation.dat and translation.dat
        ptools.io.check_file_exists('rotation.dat', "rotation file 'rotation.dat' is required.")
        ptools.io.check_file_exists('translation.dat', "translation file 'translation.dat' is required.")
        trans = ptools.Rigidbody('translation.dat')

        if args.start1 is True:
            transnb -= 1

        co = trans.getCoords(transnb)
        translations = [[transnb + 1, co]]

        if transnb != len(trans) - 1:
            printFiles = False  # don't append ligand, receptor, etc. unless this is the last translation point of the simulation

    # core attract algorithm
    for trans in translations:
        transnb += 1
        print("@@@@@@@ Translation nb {} @@@@@@@".format(transnb))
        rotnb = 0
        for rot in rotations:
            rotnb += 1
            print("----- Rotation nb {} -----".format(rotnb))
            minimcounter = 0
            ligand = ptools.AttractRigidbody(lig)

            center = ligand.FindCenter()
            ligand.Translate(ptools.Coord3D() - center)  # set ligand center of mass to 0,0,0
            ligand.AttractEulerRotate(surreal(rot[0]), surreal(rot[1]), surreal(rot[2]))
            ligand.Translate(trans[1])

            for minim in minimlist:
                minimcounter += 1
                cutoff = math.sqrt(minim['squarecutoff'])
                niter = minim['maxiter']
                print("{{ " + "minimization nb {} of {} ; cutoff= {:.2f} (A) ; maxiter= {}".format(minimcounter, nbminim, cutoff, niter))

                # performs single minimization on receptor and ligand, given maxiter=niter and restraint constant rstk
                forcefield = ff_specs['ff_class'](ff_specs['ff_file'], surreal(cutoff))
                rec.setTranslation(False)
                rec.setRotation(False)

                forcefield.AddLigand(rec)
                forcefield.AddLigand(ligand)
                rstk = minim['rstk']  # restraint force
                # if rstk>0.0:
                #     forcefield.SetRestraint(rstk)
                lbfgs_minimizer = ff_specs['minimizer_class'](forcefield)
                lbfgs_minimizer.minimize(niter)
                X = lbfgs_minimizer.GetMinimizedVars()  # optimized freedom variables after minimization

                # TODO: test and use CenterToOrigin() !
                output = ptools.AttractRigidbody(ligand)
                center = output.FindCenter()
                output.Translate(ptools.Coord3D() - center)
                output.AttractEulerRotate(surreal(X[0]), surreal(X[1]), surreal(X[2]))
                output.Translate(ptools.Coord3D(surreal(X[3]), surreal(X[4]), surreal(X[5])))
                output.Translate(center)

                ligand = ptools.AttractRigidbody(output)
                if args.single:
                    ntraj = lbfgs_minimizer.GetNumberIter()
                    for iteration in range(ntraj):
                        traj = lbfgs_minimizer.GetMinimizedVarsAtIter(iteration)
                        for t in traj:
                            ftraj.write("{:.6f} ".format(t))
                        ftraj.write("\n")
                    ftraj.write("~~~~~~~~~~~~~~\n")

            # computes RMSD if reference structure available
            if args.reffile:
                rms = Rmsd_alias(ref, output)
            else:
                rms = "XXXX"

            # calculates true energy, and rmsd if possible
            # with the new ligand position
            forcefield = ff_specs['ff_class'](ff_specs['ff_file'], surreal(500))
            print("{:4s} {:6s} {:6s} {:13s} {:13s}".format(' ', 'Trans', 'Rot', 'Ener', 'RmsdCA_ref'))
            pl = ptools.AttractPairList(rec, ligand, surreal(500))
            print("{:4s} {:6d} {:6d} {:13.7f} {:13s}".format('==', transnb, rotnb, forcefield.nonbon8(rec, ligand, pl), str(rms)))
            output.PrintMatrix()

    # output compressed ligand and receptor:
    if not args.single and printFiles:
        print(compress_file(args.receptor_name))
        print(compress_file(args.ligand_name))
        print(compress_file(ff_specs['ff_file']))
        print(compress_file('translation.dat'))
        print(compress_file('rotation.dat'))
        print(compress_file('attract.inp'))

    # close trajectory file for single minimization
    if args.single:
        ftraj.close()
        print("Saved all minimization variables (translations/rotations) in {}".format(trjname))

    # print end and elapsed time
    time_end = datetime.datetime.now()
    # print "Finished at: ",now.strftime("%A %B %d %Y, %H:%M")
    print("End time:", time_end)
    print("Elapsed time:", time_end - time_start)
