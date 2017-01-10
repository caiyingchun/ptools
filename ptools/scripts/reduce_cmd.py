
"""PTools reduce command."""

from __future__ import print_function

import itertools
import os
import sys

import yaml

import ptools


DEFAULT_ATTRACT1_PROT_REDUCTION_YML = os.path.join(ptools.DATA_DIR, 'at2cg_attract1_prot.yml')
DEFAULT_ATTRACT1_DNA_REDUCTION_YML = os.path.join(ptools.DATA_DIR, 'at2cg.dna.dat')
DEFAULT_CONVERSION_YML = os.path.join(ptools.DATA_DIR, 'name_conversion.yml')
DEFAULT_ATTRACT2_REDUCTION_YML = os.path.join(ptools.DATA_DIR, 'at2cg_attract2.yml')
DEFAULT_SCORPION_REDUCTION_YML = os.path.join(ptools.DATA_DIR, 'at2cg_scorpion.yml')


class Bead(ptools.Atomproperty):
    def __init__(self, atoms, parameters):
        self.atoms = atoms
        self.weights = [atom_parameters.get('weight', 1.0)
                        for atom_parameters in parameters['atoms'].values()]
        self.atomType = parameters.get('name', 'X')
        self.atomCharge = parameters.get('charge', 0.0)
        self.chainId = self.atoms[0].chainId

        typeid = parameters.get('typeid', 0)
        self.extra = '{:5d}{:8.3f} 0 0'.format(typeid, self.atomCharge)

        # List of atom names that should be part of the bead.
        self.atom_names = parameters['atoms']

    @property
    def coords(self):
        """Bead coordinates, i.e. the center of mass of the atoms
        constituting the bead.
        """
        x = ptools.Coord3D()
        for i, atom in enumerate(self.atoms):
            x += atom.coords * self.weights[i]
        n = 1. / len(self.atoms)
        return x * n

    def toatom(self):
        """Return a ptools.Atom instance with current bead properties and
        coordinates."""
        return ptools.Atom(self, self.coords)

    def topdb(self):
        return self.toatom().ToPdbString()


class CoarseResidue:
    """Create a residue coarse grain model from an atomistic model."""
    def __init__(self, resname, resid, resatoms, parameters):
        self.resname = resname
        self._resid = resid
        self.beads = []

        for bead_param in parameters:
            atoms = [a for a in resatoms if a.atomType in bead_param['atoms']]
            rc = self._compare_expected_and_found_atoms(bead_param, atoms)
            if rc != 2:
                b = Bead(atoms, bead_param)
                b.residType = self.resname
                b.residId = self.resid
                self.beads.append(b)
            else:
                msg = "skipping residue {}:{}".format(resname, resid)
                ptools.io.warning(msg)
        self._check_all_atoms_in_model(parameters)

    def _check_all_atoms_in_model(self, parameters):
        """Check that every atoms from atomistic model have been taken
        into account for creating the coarse grain model.

        Print a warning message if it is not the case.
        """
        bead_atom_names = [atom.atomType
                           for bead in self.beads
                           for atom in bead.atoms]
        bead_atom_name_parameters = [name
                                     for bead_param in parameters
                                     for name in bead_param['atoms']]

        diff = set(bead_atom_names) - set(bead_atom_name_parameters)
        for atom_name in diff:
            msg = "{}:{}: atom '{}' unused during coarse grain modelling"
            msg = msg.format(self.resname, self.resid, atom_name)

    def _compare_expected_and_found_atoms(self, bead_param, atoms):
        """Compare expected atoms from bead parameters to atoms actually found
        in the residue.

        Returns:
            int: 0 if expected atoms are the same as found atoms
                 1 if they differ
                 2 if no expected atom has been found
        """
        if not atoms:
            err = 'no atom found for bead {} (atoms={}) of residue {}:{}'
            err = err.format(bead_param['name'], bead_param['atoms'],
                             self.resname, self.resid)
            ptools.io.warning(err)
            return 2
        elif len(atoms) != len(bead_param['atoms']):
            msg = 'residue %(resname)s:%(resid)d, bead %(bead_name)s: '\
                  'expected atoms %(expected_atoms)s, '\
                  'found %(found_atoms)s' % {
                      'resname': self.resname,
                      'resid': self.resid,
                      'bead_name': bead_param['name'],
                      'expected_atoms': sorted(bead_param['atoms']),
                      'found_atoms': sorted(a.atomType for a in atoms)
                  }
            ptools.io.warning(msg)
            return 1
        return 0

    @property
    def resid(self):
        return self._resid

    @resid.setter
    def resid(self, value):
        for b in self.beads:
            b.residId = value
        self._resid = value

    def topdb(self):
        return '\n'.join(b.topdb() for b in self.beads)


class Reducer(object):
    """Class that handle reduction from an atomistic topology to a coarse
    grain model.

    The reduction consists of two steps, namely preprocessing and reduction
    itself.

    1 - Preprocessing
    -----------------

    Atom and residues from the all-atom topology are renamed if
    necessary to make sure they match the reduction parameter file.

    As an example, it is quite common that C-terminal oxygen atoms are named
    'OT' (or any variation). Some coarse grain models such as ATTRACT1 and
    ATTRACT2 will consider those atom in the exact same way as other oxygen
    atoms. Hence, those models require renaming OT atoms into 'O'.

    2 - Reduction
    -------------

    - top <- read all atom topology
    - foreach residue in top
          check residue is defined is reduction parameters
          CREATE_RESIDUE_BEADS(residue, reduction parameters)

    PROCEDURE CREATE_RESIDUE_BEADS (residue, parameters)
        foreach bead_parameter in parameters
            atoms <- find atoms in residu that belong to current bead
            check number of atoms found vs number that should have been found
            create a bead:
                name, type, charge, etc. are determined from parameters
                coordinates is the barycentre of atoms that belong to the bead
    """

    def __init__(self, topology_file, reduction_parameters_file):
        """Initialize Reduce from topology file and reduction parameter file.

        Args:
            topology_file (str): path to all-atom topology file (PDB format).
            reduction_parameter_file (str): path to reduction parameter file
                (YAML format).

        Attributes:
            allatom_file (str): path to all-atom topology file
            reduction_file (str): path to reduction parameter file
            atoms (list[ptools.Atom]): list of all atoms read from topology
            forcefield (str): force field name read from reduction parameter
                file
            reduction_parameters (dict[str]->list): map residue names with a
                list of bead parameter for each bead in a residue.
            beads (list[Bead]): list all coarse grain beads for this model

            name_conversion_file (str): path to residue and atom name
                conversion file.
            residue_rename (dict[str]->str): map source residue name with target
                residue name (see Preprocessing).
            atom_rename (dict[str]->dict[str]->str): map target residue name
                with map mapping source atom name with target atom name
                (see Preprocessing).
        """
        self.allatom_file = topology_file
        self.reduction_file = reduction_parameters_file
        self.atoms = []
        self.forcefield = ''
        self.reduction_parameters = {}
        self.beads = []

        self._name_conversion_file = ''
        self.residue_rename = {}
        self.atom_rename = {}

        ptools.io.check_file_exists(self.reduction_file)
        ptools.io.check_file_exists(self.allatom_file)

        self.read_reduction_parameters()
        self.read_topology()

    @property
    def name_conversion_file(self):
        return self._name_conversion_file

    @name_conversion_file.setter
    def name_conversion_file(self, value):
        self._name_conversion_file = value
        self.read_name_conversion_file()

    def read_reduction_parameters(self):
        """Read YAML reduction parameter file."""
        with open(self.reduction_file, 'rt') as f:
            data = yaml.load(f)
        self.forcefield = data['forcefield']
        self.reduction_parameters = data['beads']

    def read_topology(self):
        """Read PDB topology file."""
        rb = ptools.Rigidbody(self.allatom_file)
        self.atoms = [rb.CopyAtom(i) for i in xrange(len(rb))]

    def read_name_conversion_file(self):
        """Read YAML file containing residue and atom name conversion rules.

        Update residue_rename and atom_rename internal maps.
        """
        with open(self.name_conversion_file, 'rt') as f:
            data = yaml.load(f)
        self.residue_rename = data['residues']
        self.atom_rename = data['atoms']

    def rename_atoms_and_residues(self):
        """Rename atom and residues according to data in rename maps."""
        def should_rename_residue():
            return atom.residType in self.residue_rename

        def rename_residue():
            atom.residType = self.residue_rename[atom.residType]

        def should_rename_atom_for_every_residue():
            """If '*' is in the atom rename map, all residues are affected."""
            return '*' in self.atom_rename and atom.atomType in self.atom_rename['*']

        def should_rename_atom():
            return atom.residType in self.atom_rename and \
                atom.atomType in self.atom_rename[atom.residType]

        def rename_atom(name):
            atom.atomType = name

        for atom in self.atoms:
            if should_rename_residue():
                rename_residue()

            if should_rename_atom_for_every_residue():
                rename_atom(self.atom_rename['*'][atom.atomType])

            if should_rename_atom():
                rename_atom(self.atom_rename[atom.residType][atom.atomType])

    def reduce(self):
        """Actual reduction method.

        Group atoms by residue then iterate over those residues to create
        coarse grain residues.
        """
        def has_rule_for_residue_reduction():
            if resname not in self.reduction_parameters:
                msg = "don't know how to handle residue {0} "\
                      "(no reduction rule found for this residue)..."\
                      "skipping this residue".format(resname)
                ptools.io.warning(msg)
                return False
            return True

        # Rename atoms and residues so that they will match reduction
        # parameters.
        self.rename_atoms_and_residues()

        # Residue list: group atoms by residue tag.
        # A residue is two items: (<residue tag>, <atom list iterator>).
        residue_list = itertools.groupby(self.atoms,
                                         key=lambda atom: residuetag(atom.residType,
                                                                     atom.chainId,
                                                                     atom.residId))
        atomid = 1
        for restag, resatoms in residue_list:
            resname, chain, resid = restag.split('-')

            if has_rule_for_residue_reduction():
                coarse_res = CoarseResidue(resname, int(resid),
                                           list(resatoms),
                                           self.reduction_parameters[resname])
                # Update bead atom id.
                for bead in coarse_res.beads:
                    bead.atomId = atomid
                    atomid += 1

                self.beads += coarse_res.beads

    def print_output_model(self, path=''):
        """Print coarse grain model in reduced PDB format.

        Args:
            path (str): output file name.
                If left empty, print on stdout.
        """
        forcefield = self.forcefield
        header = 'HEADER    {} REDUCED PDB FILE'.format(forcefield)
        content = '\n'.join(bead.toatom().ToPdbString() for bead in self.beads)
        f = sys.stdout
        if path:
            f = open(path, 'wt')
        print(header, content, sep='\n', file=f)
        if path:
            f.close()


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
    parser.add_argument('--conv', dest='convName',
                        default=DEFAULT_CONVERSION_YML,
                        help="path type conversion file")
    parser.add_argument('-o', '--output',
                        help='path to output file (default=stdout)')


def create_attract2_subparser(parent):
    parser = parent.add_parser('attract2',
                               help='reduce using the attract2 force field')
    parser.set_defaults(forcefield='attract2')
    parser.add_argument('--red', dest='redName',
                        help="path to correspondance file between atoms and beads file")
    parser.add_argument('--conv', dest='convName',
                        default=DEFAULT_CONVERSION_YML,
                        help="path type conversion file")
    parser.add_argument('-o', '--output',
                        help='path to output file (default=stdout)')

def create_scorpion_subparser(parent):
    parser = parent.add_parser('scorpion',
                               help='reduce using the scorpion force field')
    parser.set_defaults(forcefield='scorpion')
    parser.add_argument('--red', dest='redName',
                        help="path to correspondance file between atoms and beads file")
    parser.add_argument('--conv', dest='convName',
                        default=DEFAULT_CONVERSION_YML,
                        help="path type conversion file")
    parser.add_argument('-o', '--output',
                        help='path to output file (default=stdout)')



def create_subparser(parent):
    parser = parent.add_parser('reduce', help=__doc__)
    parser.set_defaults(func=run)

    parser.add_argument('pdb',
                        help="path to input PDB file (atomistic resolution)")

    subparsers = parser.add_subparsers()
    create_attract1_subparser(subparsers)
    create_attract2_subparser(subparsers)
    create_scorpion_subparser(subparsers)


def get_reduction_data_path(args):
    """Return path to reduction data file.

    Reduction data file can be provided from the '--red' option.

    Returns:
        str: path to reduction parameter file.
    """
    if not args.redName:
        if args.forcefield == 'attract1':
            if args.molProt:
                return DEFAULT_ATTRACT1_PROT_REDUCTION_YML
            elif args.molDNA:
                return DEFAULT_ATTRACT1_DNA_REDUCTION_YML
            else:
                err = "error: one of the arguments --prot --dna is required when "\
                      "not using --red option"
                print(err, file=sys.stderr)
                sys.exit(2)
        elif args.forcefield == 'attract2':
            return DEFAULT_ATTRACT2_REDUCTION_YML
        elif args.forcefield == 'scorpion':
            return DEFAULT_SCORPION_REDUCTION_YML
    return args.redName


def residuetag(resname, resid, chain):
    """Return a string in the format <residue_name>-<residue_id>-<chain_id>."""
    return '{}-{}-{}'.format(resname, resid, chain)


def run(args):
    redname = get_reduction_data_path(args)
    convname = args.convName
    atomicname = args.pdb

    ptools.io.check_file_exists(redname)
    ptools.io.check_file_exists(convname)
    ptools.io.check_file_exists(atomicname)

    reducer = Reducer(atomicname, redname)
    reducer.name_conversion_file = convname

    reducer.reduce()
    reducer.print_output_model(args.output)
