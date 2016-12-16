
"""PTools reduce command."""

from __future__ import print_function

import argparse
import itertools
import os
import sys

import ptools


DEFAULT_PROT_REDUCTION_DATA = os.path.join(ptools.DATA_DIR, 'at2cg.prot.dat')
DEFAULT_DNA_REDUCTION_DATA = os.path.join(ptools.DATA_DIR, 'at2cg.dna.dat')
DEFAULT_FF_PARAM_DATA = os.path.join(ptools.DATA_DIR, 'ff_param.dat')
DEFAULT_CONVERSION_DATA = os.path.join(ptools.DATA_DIR, 'type_conversion.dat')


class AtomInBead:
    """Class definition for an atom in a bead"""
    def __init__(self, name, wgt):
        self.name = name    # atom name
        self.x = 0.0        # x coordinate
        self.y = 0.0        # y coordiante
        self.z = 0.0        # z coordinate
        self.weight = wgt   # atom weight (within a bead)
        self.found = 0      # atom found or not (not found by default)

    def Show(self):
        return "%s %8.3f %8.3f %8.3f %3.1f %d" % (self.name, self.x, self.y, self.z, self.weight, self.found)


class Bead:
    """Class definition for a bead"""
    def __init__(self, name, id):
        self.name = name        # bead name
        self.id = id            # bead id
        self.size = 0           # bead size (number of atoms inside)
        self.listOfAtomNames = []  # list of all atom names
        self.listOfAtoms = []  # list of all atoms (AtomInBead)

    def Show(self):
        return "%s %d %d" % (self.name, self.id, self.size)


class CoarseRes:
    """Class definition for coarse grain (reduced) protein residue (or DNA base)"""
    def __init__(self):
        self.listOfBeadId = []      # list of bead id in res
        self.listOfBeads = []       # list of beads in res

    def __repr__(self):
        name = self.__class__.__name__
        nbeads = len(self.listOfBeads)
        return '{}({} beads)'.format(name, nbeads)

    def Add(self, residue):
        """Add in a residue atoms from bead"""
        for at in residue:
            at_name = at[1]
            at_wgt = float(at[2])
            bd_id = int(at[3])
            bd_name = at[4]
            if at_name != 'EMPTY':  # EMPTY is a special tag to deal with glycine
                # in bead not in residue than create it
                if bd_id not in self.listOfBeadId:
                    self.listOfBeadId.append(bd_id)
                    self.listOfBeads.append(Bead(bd_name, bd_id))
                # add atom in bead in residue
                bead_position = self.listOfBeadId.index(bd_id)
                bead = self.listOfBeads[bead_position]
                bead.listOfAtomNames.append(at_name)
                atInBd = AtomInBead(at_name, at_wgt)
                bead.listOfAtoms.append(atInBd)
                bead.size += 1
                # update bead in residue
                self.listOfBeads[bead_position] = bead
        # return the number of bead per residue
        return len(self.listOfBeadId)

    # def FillAtom(self, at_name, x, y, z):
    #     """Fill an atom from bead with coordinates"""
    #     # quickly check atom in atom list
    #     # 1: browse beads
    #     for bead in self.listOfBeads:
    #         # 2: browse atoms in bead
    #         if at_name in bead.listOfAtomNames:
    #             # then find exactly where this atom is present
    #             for atom in bead.listOfAtoms:
    #                 if at_name == atom.name:
    #                     atom.x = x
    #                     atom.y = y
    #                     atom.z = z
    #                     atom.found = 1

    # def Reduce(self, infoResName, infoResId):
    #     """Reduce a bead with atoms present in bead"""
    #     output = []
    #     # reduce all beads in a residue
    #     # for each bead in the residue
    #     for bead in self.listOfBeads:
    #         reduce_size = 0
    #         reduce_x = 0.0
    #         reduce_y = 0.0
    #         reduce_z = 0.0
    #         sum_wgt = 0.0
    #         # for each atom of a bead
    #         for atom in bead.listOfAtoms:
    #             if atom.found == 1:
    #                 reduce_size += 1
    #                 reduce_x += atom.x * atom.weight
    #                 reduce_y += atom.y * atom.weight
    #                 reduce_z += atom.z * atom.weight
    #                 sum_wgt += atom.weight
    #             else:
    #                 message = "ERROR: missing atom %s in bead %s %2d for residue %s %d. Please fix your PDB!\n" \
    #                           % (atom.name, bead.name, bead.id, infoResName, infoResId)
    #                 if options.warning:
    #                     sys.stderr.write(message)
    #                     sys.stderr.write("Continue execution as required ...\n")
    #                 else:
    #                     raise Exception(message)
    #         if reduce_size == bead.size:
    #             coord = Coord3D(reduce_x / sum_wgt, reduce_y / sum_wgt, reduce_z / sum_wgt)
    #             output.append([coord, bead.name, bead.id])
    #     return output

    # def Show(self):
    #     for bead in self.listOfBeads:
    #         print bead.name, bead.id, bead.size, bead.atomIdList



def create_attract1_subparser(parent):
    parser = parent.add_parser('attract1',
                               help='reduce using the attract1 force field')
    parser.set_defaults(forcefield='attract1')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--prot', action='store_true', dest='molProt',
                       help='reduce protein')
    group.add_argument('--dna', action='store_true', dest='molDNA',
                       help='reduce DNA')

    parser.add_argument('--red', dest='redName',
                        help="path to correspondance file between atoms and beads file")
    parser.add_argument('--ff', dest='ffName',
                        default=DEFAULT_FF_PARAM_DATA,
                        help="path to force field parameter file")
    parser.add_argument('--conv', dest='convName',
                        default=DEFAULT_CONVERSION_DATA,
                        help="path type conversion file")
    parser.add_argument('--allow_missing', action='store_true',
                        dest='warning',
                        help="don't stop program if atoms are missing, "
                             "only display a warning on stderr")


def create_subparser(parent):
    parser = parent.add_parser('reduce', help=__doc__)
    parser.set_defaults(func=run)

    parser.add_argument('pdb',
                        help="path to input PDB file (atomistic resolution)")

    subparsers = parser.add_subparsers()
    create_attract1_subparser(subparsers)

    
def get_reduction_data_path(args):
    """Return path to reduction data file.

    Reduction data file can be provided from the '--red' option.
    If it is not, 
     which depends on whether the input
    file is protein or DNA and the path to a custom parameter file was
    provided or not."""
    if not args.redName:
        if args.molProt:
            return DEFAULT_PROT_REDUCTION_DATA
        elif args.molDNA:
            return DEFAULT_DNA_REDUCTION_DATA
        else:
            err = "error: one of the arguments --prot --dna is required when "\
                  "not using --red option"
            print(err, file=sys.stderr)
            sys.exit(2)
    return args.redName


def read_reduction_parameters(path):
    """Read file that contains parameters for correspondance between atoms
    and beads.

    Args:
        path (str): path to parameter file.

    Return:
        dict[str]->CoarseRes: a dictionnary mapping a residue name with a 
            CoarseRes instance.
    """

    # Read file and store non comment lines into a list of tokens.
    allitems = []
    with open(path, 'rt') as f:
        for lineid, line in enumerate(f):
            if not ptools.io.is_comment(line):
                items = line.split()
                
                # Dies if less that 5 columns on the line.
                if len(items) < 5:
                    msg = 'expected at least 5 items (found {})'.format(len(items))
                    raise ptools.io.FileParsingError(path, msg, line, lineid + 1)
                
                allitems.append(items[:5])

    # Sort items in reverse order ensure that '*' lines are at the end of
    # the list (and also is sorting is required for itertools.groupby)
    allitems.sort(key=lambda items: items[0], reverse=True)
    
    # Construct the output structure.
    resBeadAtomModel = {}
    for res, residue in itertools.groupby(allitems, lambda items: items[0]):
        residue = list(residue)
        if res != '*':
            resBeadAtomModel[res] = CoarseRes()
            resBeadAtomModel[res].Add(residue)
        else:
            # Atoms named '*' have to be added to all residues.
            for bead in resBeadAtomModel.values():
                bead.Add(residue)

    return resBeadAtomModel



def run(args):
    print("This is reduce")

    redname = get_reduction_data_path(args)
    ffname = args.ffName
    convname = args.convName
    atomicname = args.pdb

    ptools.io.check_file_exists(redname)
    ptools.io.check_file_exists(ffname)
    ptools.io.check_file_exists(convname)
    ptools.io.check_file_exists(atomicname)

    resBeadAtomModel = read_reduction_parameters(redname)
