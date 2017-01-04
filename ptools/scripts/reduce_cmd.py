
"""PTools reduce command."""

from __future__ import print_function

import copy
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

    def FillAtom(self, at_name, x, y, z):
        """Fill an atom from bead with coordinates"""
        # quickly check atom in atom list
        # 1: browse beads
        for bead in self.listOfBeads:
            # 2: browse atoms in bead
            if at_name in bead.listOfAtomNames:
                # then find exactly where this atom is present
                for atom in bead.listOfAtoms:
                    if at_name == atom.name:
                        atom.x = x
                        atom.y = y
                        atom.z = z
                        atom.found = 1

    def Reduce(self, infoResName, infoResId, fail_on_error=True):
        """Reduce a bead with atoms present in bead"""
        output = []
        # reduce all beads in a residue
        # for each bead in the residue
        for bead in self.listOfBeads:
            reduce_size = 0
            reduce_x = 0.0
            reduce_y = 0.0
            reduce_z = 0.0
            sum_wgt = 0.0
            # for each atom of a bead
            for atom in bead.listOfAtoms:
                if atom.found == 1:
                    reduce_size += 1
                    reduce_x += atom.x * atom.weight
                    reduce_y += atom.y * atom.weight
                    reduce_z += atom.z * atom.weight
                    sum_wgt += atom.weight
                else:
                    message = "missing atom %(atomname)s "\
                              "in bead %(beadname)s %(beadid)2d "\
                              "for residue %(resname)s:%(resid)d. "\
                              "Please fix your PDB!\n" % {'atomname': atom.name,
                                                          'beadname': bead.name,
                                                          'beadid': bead.id,
                                                          'resname': infoResName,
                                                          'resid': infoResId}
                    if fail_on_error:
                        raise Exception(message)
                    else:
                        ptools.io.warning(message)
                        ptools.io.warning("Continue execution as required...")
            if reduce_size == bead.size:
                x = reduce_x / sum_wgt
                y = reduce_y / sum_wgt
                z = reduce_z / sum_wgt
                coord = ptools.Coord3D(x, y, z)
                output.append([coord, bead.name, bead.id])
        return output

    def Show(self):
        for bead in self.listOfBeads:
            print(bead.name, bead.id, bead.size, bead.atomIdList)


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

    Returns:
        str: path to reduction parameter file.
    """
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


def atomtag(resname, atomname):
    """Return a string in the format <residue_name>-<atom_name>."""
    return '{}-{}'.format(resname, atomname)


def residuetag(resname, resid, chain):
    """Return a string in the format <residue_name>-<residue_id>-<chain_id>."""
    return '{}-{}-{}'.format(resname, resid, chain)


def read_reduction_parameters(path):
    """Read file that contains parameters for correspondance between atoms
    and beads.

    Args:
        path (str): path to parameter file.

    Returns:
        dict[str]->CoarseRes: a dictionary mapping a residue name with a
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

    # Sort items in reverse order ensure that '*' lines are at the start of
    # the list (and also is sorting is required for itertools.groupby)
    allitems.sort(key=lambda items: items[0], reverse=False)

    # Construct the output structure in two steps.
    
    # 1. Create empty coarse residues.
    resBeadAtomModel = {}
    for res, residue in itertools.groupby(allitems, lambda items: items[0]):
        if res != '*':
            resBeadAtomModel[res] = CoarseRes()

    # 2. Add beads to residues.
    for res, residue in itertools.groupby(allitems, lambda items: items[0]):
        residue = list(residue)
        if res == '*':
            # Atoms named '*' have to be added to all residues.
            for bead in resBeadAtomModel.values():
                bead.Add(residue)
        else:
            resBeadAtomModel[res].Add(residue)

    # NOTE: the construction could be done in a single step.
    # It is done this way because doing it in a single step would change
    # beads order in output file (see diff with ad64a4a).

    return resBeadAtomModel


def read_forcefield_parameters(path):
    """Read force field parameter file.

    Args:
        path (str): path to parameter file.

    Returns:
        dict[int]->float: dictionary mapping the bead id with its charge.
    """
    charge_dict = {}
    with open(path, 'rt') as f:
        for lineid, line in enumerate(f):
            if not ptools.io.is_comment(line):
                items = line.split()
                # Dies if less that 5 columns on the line.
                if len(items) < 5:
                    msg = 'expected at least 5 items (found {})'.format(len(items))
                    raise ptools.io.FileParsingError(path, msg, line, lineid + 1)
                bead_id = int(items[0])
                bead_charge = float(items[3])
                charge_dict[bead_id] = bead_charge
    return charge_dict


def read_type_conversion_parameters(path):
    """Read atom and residue type conversion parameter file.

    Args:
        path (str): path to parameter file.

    Returns:
        dict[str]->str: dictionary mapping old residue names with new ones
        dict[str]->str: dictionary mapping old atom names with new ones
    """
    def raise_invalid_number_of_tokens(path, tokens, line, lineid):
        msg = 'expected 2 tokens for residue type conversion and '\
              '3 tokens for atom typeconversion '\
              '(found {})'.format(len(tokens))
        raise ptools.io.FileParsingError(path, msg, line, lineid)

    def warn_duplicate_entry(entry, lineid):
        msg = 'duplicate entry {} at line {}'.format(entry, lineid)
        ptools.io.warning(msg)

    def parse_residue_conversion():
        res_old, res_new = items
        if res_old in res_conv:
            warn_duplicate_entry(res_old, lineid + 1)
        else:
            res_conv[res_old] = res_new

    def parse_atom_conversion():
        res, atom_old, atom_new = items
        entry_old = atomtag(res, atom_old)
        entry_new = atomtag(res, atom_new)
        if entry_old in atom_conv:
            warn_duplicate_entry(entry_old, lineid + 1)
        else:
            atom_conv[entry_old] = entry_new

    res_conv = {}
    atom_conv = {}
    with open(path, 'rt') as f:
        for lineid, line in enumerate(f):
            if not ptools.io.is_comment(line):
                items = line.split()
                if len(items) == 2:
                    parse_residue_conversion()
                elif len(items) == 3:
                    parse_atom_conversion()
                else:
                    raise_invalid_number_of_tokens(path, items, line, lineid + 1)

    return res_conv, atom_conv


def read_atomic(path, res_conv, atom_conv):
    """Read all atom topology file.

    Convert residue and atom names on the fly.

    Args:
        path (str): path to topology file.
        res_conv (dict[str]->str): map old residue names with new ones.
        atom_conv (dict[str]->str): map old atom names with new ones

    Returns:
        list[]: atoms read from input file.
    """
    rb = ptools.Rigidbody(path)
    atomlist = []
    for i in xrange(len(rb)):
        atom = rb.CopyAtom(i)

        # Residue name conversion.
        resname = atom.residType
        if resname in res_conv:
            atom.residType = res_conv[resname]

        # Atom name conversion.
        atomname = atomtag(atom.residType, atom.atomType)
        if atomname in atom_conv:
            name = atom_conv[atomname].split('-')[1]
            atom.atomType = name

        atomlist.append(atom)
    return atomlist


def count_residues(atomlist, residue_to_cg):
    """Create the list of residue tags and residue beads.

    Args:
        atomlist (list[ptools.Atom]): list of all atoms read from topology.
        residue_to_cg (dict[str]->CoarseRes): map the residue name with a
            coarse grain representation.

    Returns:
        list[str]: list of residue tags (one per residue).
        list[CoarseRes]: list of beads (one per residue).
    """
    restaglist = []
    beadlist = []
    for atom in atomlist:
        resname = atom.residType
        restag = residuetag(resname, atom.residId, atom.chainId)
        if restag not in restaglist:
            if resname in residue_to_cg:
                restaglist.append(restag)
                beadlist.append(copy.deepcopy(residue_to_cg[resname]))
            else:
                msg = 'residue {} is unknown the residues <-> beads <-> atoms '\
                      'list!! It will not be reduced into coarse grain'.format(resname)
                ptools.io.warning(msg)
    return restaglist, beadlist


def fill_beads(atomlist, restaglist, beadlist):
    """
    Args:
        atomlist (list[ptools.Atom]): list of all atoms read from topology.
        restaglist (list[str]): list of residue tags (one per residue).
        beadlist (list[CoarseRes]): list of beads (one per residue).
    """
    for atom in atomlist:
        restag = residuetag(atom.residType, atom.residId, atom.chainId)
        if restag in restaglist:
            index = restaglist.index(restag)
            beadlist[index].FillAtom(atom.atomType,
                                     atom.coords.x,
                                     atom.coords.y,
                                     atom.coords.z)


def reduce_beads(restaglist, beadlist, bead_charge_map):
    """Reduction to coarse grain model.

    Args:
        restaglist (list[str]): list of residue tags (one per residue).
        beadlist (list[CoarseRes]): list of beads (one per residue).
        bead_charge_map (dict[int]->float): dictionary mapping the bead id with
            its charge.
        keep_original_order (bool): sort beads as in older version of PTools.

    Returns:
        list[ptools.Atom]: coarse grain model as an atom list.
    """
    cgmodel = []
    atom_count = 0
    for i, restag in enumerate(restaglist):
        tag = restag.split('-')
        resname = tag[0]
        resid = int(tag[1])
        resbead = beadlist[i].Reduce(resname, resid)
        for bead in resbead:
            coord = bead[0]
            atomname = bead[1]
            atomtypeid = bead[2]
            atomcharge = 0.0
            if atomtypeid in bead_charge_map:
                atomcharge = bead_charge_map[atomtypeid]
            else:
                msg = "cannot find charge for bead {} {:2d}... defaults to 0.0"
                ptools.io.warning(msg.format(atomname, atomtypeid))
            atom_count += 1

            prop = ptools.Atomproperty()
            prop.atomType = atomname
            prop.atomId = atom_count
            prop.residId = resid
            prop.residType = resname
            prop.chainId = ' '
            prop.extra = '{:5d}{:8.3f}{:2d}{:2d}'.format(atomtypeid,
                                                         atomcharge, 0, 0)
            newatom = ptools.Atom(prop, coord)

            cgmodel.append(newatom)
    return cgmodel


def print_red_output(cgmodel):
    """Print coarse grain model to stdout as a reduced PDB file.

    Args:
        cgmodel (list[ptools.Atom]): coarse grain atom list.
    """
    print("HEADER    ATTRACT1 REDUCED PDB FILE")
    print('\n'.join(atom.ToPdbString() for atom in cgmodel))


def run(args):
    redname = get_reduction_data_path(args)
    ffname = args.ffName
    convname = args.convName
    atomicname = args.pdb

    ptools.io.check_file_exists(redname)
    ptools.io.check_file_exists(ffname)
    ptools.io.check_file_exists(convname)
    ptools.io.check_file_exists(atomicname)

    resBeadAtomModel = read_reduction_parameters(redname)
    beadChargeDict = read_forcefield_parameters(ffname)
    resConv, atomConv = read_type_conversion_parameters(convname)

    atomList = read_atomic(atomicname, resConv, atomConv)
    residueTagList, coarseResList = count_residues(atomList, resBeadAtomModel)
    fill_beads(atomList, residueTagList, coarseResList)
    cgmodel = reduce_beads(residueTagList, coarseResList, beadChargeDict)
    print_red_output(cgmodel)
