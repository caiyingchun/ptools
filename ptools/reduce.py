
"""ptools.reduce - Transform an all-atom topology to a coarse grain model."""

from __future__ import print_function

import os
import itertools
import sys

import yaml

import ptools
from .exceptions import (NoResidueReductionRulesFoundError,
                         IncompleteBeadError,
                         DuplicateAtomInBeadError)


DEFAULT_ATTRACT1_PROT_REDUCTION_YML = os.path.join(ptools.DATA_DIR, 'at2cg_attract1_prot.yml')
DEFAULT_ATTRACT1_DNA_REDUCTION_YML = os.path.join(ptools.DATA_DIR, 'at2cg_attract1_dna.yml')
DEFAULT_NAME_CONVERSION_YML = os.path.join(ptools.DATA_DIR, 'name_conversion.yml')
DEFAULT_ATTRACT2_REDUCTION_YML = os.path.join(ptools.DATA_DIR, 'at2cg_attract2.yml')
DEFAULT_SCORPION_REDUCTION_YML = os.path.join(ptools.DATA_DIR, 'at2cg_scorpion.yml')


class Bead(ptools.Atomproperty):
    def __init__(self, atoms, resname, resid, parameters):
        super(Bead, self).__init__()
        self.atoms = atoms
        self.residType = resname
        self.residId = resid
        self.atomType = parameters.get('name', 'X')
        self.atomCharge = parameters.get('charge', 0.0)
        self.typeid = parameters.get('typeid', 0)

        # Set bead attributes with attributes coming from reduction
        # parameters.
        for attr, value in parameters.items():
            if attr not in ('typeid', 'name', 'charge', 'atoms'):
                setattr(self, attr, value)

        # List of atom names that should be part of the bead.
        self.atom_reduction_parameters = parameters['atoms']
        self.extra = '{:5d}{:8.3f} 0 0'.format(self.typeid, self.atomCharge)

        self.chainId = ''
        if len(self.atoms) > 0:
            self.chainId = self.atoms[0].chainId

    @property
    def charge(self):
        return self.atomCharge

    @charge.setter
    def charge(self, value):
        """Use this setter to set `atomCharge` and update `extra` on the fly."""
        self.atomCharge = value
        self.extra = '{:5d}{:8.3f} 0 0'.format(self.typeid, self.atomCharge)

    @property
    def coords(self):
        """Bead coordinates, i.e. the center of mass of the atoms
        constituting the bead.
        """
        weights = [atom_parameters.get('weight', 1.0)
                   for atom_parameters in self.atom_reduction_parameters.values()]
        x = ptools.Coord3D()
        for i, atom in enumerate(self.atoms):
            x += atom.coords * weights[i]
        n = 1. / len(self.atoms)
        return x * n

    @property
    def name(self):
        """Get bead name."""
        return self.atomType

    @name.setter
    def name(self, value):
        """Set bead name."""
        self.atomType = value

    def toatom(self):
        """Return a ptools.Atom instance with current bead properties and
        coordinates."""
        return ptools.Atom(self, self.coords)

    def topdb(self):
        """Return the bead description as a PDB formatted string."""
        return self.toatom().ToPdbString()

    def is_incomplete(self):
        """Return True if the number of atoms found to build the bead is
        different from the number of atoms expected."""
        return len(self.atom_reduction_parameters) > len(self.atoms)

    def has_duplicate_atoms(self):
        """Return True if two atoms with the same name have been found."""
        return len(self.atom_reduction_parameters) < len(self.atoms)

    def check_composition(self):
        """Check if some atoms were unused or duplicated when creating
        the bead.

        Raises:
            IncompleteBeadError: if an atom is missing.
            DuplicateAtomInBeadError: if the same atom has been found twice.
        """
        if self.is_incomplete():
            raise IncompleteBeadError(self)
        elif self.has_duplicate_atoms():
            raise DuplicateAtomInBeadError(self)


class CoarseResidue:
    """Create a residue coarse grain model from an atomistic model."""
    def __init__(self, resname, resid, resatoms, parameters):
        self.all_atoms = resatoms
        self.resname = resname
        self._resid = resid
        self.beads = []

        for bead_param in parameters:
            atoms = [a for a in resatoms if a.atomType in bead_param['atoms']]
            b = Bead(atoms, self.resname, self.resid, bead_param)
            self.beads.append(b)

    def check_composition(self):
        """Check residue composition and each bead composition."""
        for bead in self.beads:
            bead.check_composition()

    @property
    def number_of_atoms(self):
        """Return the number of atoms in the residue beads."""
        return sum(len(bead.atoms) for bead in self.beads)

    def number_of_beads(self):
        """Return the number of beads in the residue."""
        return len(self.beads)

    @property
    def resid(self):
        """Get the residue identifier."""
        return self._resid

    @resid.setter
    def resid(self, value):
        """Set the residue identifier and update residue identifier for each
        bead in the residue."""
        for b in self.beads:
            b.residId = value
        self._resid = value

    def topdb(self):
        """Return a PDB formatted string representing the residue."""
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
        foreach bead_parameter in parameters[residue]
            atoms <- find atoms in residue that belong to current bead
            create a bead from atoms and parameters:
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
    def number_of_atoms(self):
        """Return the number of atoms in the all-atom input topology."""
        return len(self.atoms)

    @property
    def number_of_beads(self):
        """Return the number of beads in the coarse grain model."""
        return len(self.beads)

    @property
    def name_conversion_file(self):
        """Return the path to the name conversion file used."""
        return self._name_conversion_file

    @name_conversion_file.setter
    def name_conversion_file(self, value):
        """Set the path to the name conversion file and read it."""
        self._name_conversion_file = value
        self.read_name_conversion_file()

    def get_atom_radii_map(self):
        """Return atom radius map contructed from data in reduction file.

        Return:
            dict[str]->dict[str]->float: each atom of each residue radius.
        """
        radii_map = {}
        for resname, bead_parameters in self.reduction_parameters.items():
            atom_names = []
            atom_radii = []
            for bead in bead_parameters:
                for atom_name, atom in bead['atoms'].items():
                    atom_names.append(atom_name)
                    atom_radii.append(atom.get('radius', 0.0))
            radii_map[resname] = dict(zip(atom_names, atom_radii))
        return radii_map

    def get_atom_charges_map(self):
        """Return atom charge map contructed from data in reduction file.

        Return:
            dict[str]->dict[str]->float: each atom of each residue charge.
        """
        charges_map = {}
        for resname, bead_parameters in self.reduction_parameters.items():
            atom_names = []
            atom_charges = []
            for bead in bead_parameters:
                for atom_name, atom in bead['atoms'].items():
                    atom_names.append(atom_name)
                    atom_charges.append(atom.get('charge', 0.0))
            charges_map[resname] = dict(zip(atom_names, atom_charges))
        return charges_map

    def get_bead_radii_map(self):
        """Return bead radius map contructed from data in reduction file.

        Return:
            dict[str]->dict[str]->float: each bead of each residue radius.
        """
        radii_map = {}
        for resname, bead_parameters in self.reduction_parameters.items():
            bead_names = [bead['name'] for bead in bead_parameters]
            bead_radii = [bead.get('radius', 0.0) for bead in bead_parameters]
            radii_map[resname] = dict(zip(bead_names, bead_radii))
        return radii_map

    def get_bead_charges_map(self):
        """Return bead charge map contructed from data in reduction file.

        Return:
            dict[str]->dict[str]->float: each bead of each residue charge.
        """
        charges_map = {}
        for resname, bead_parameters in self.reduction_parameters.items():
            bead_names = [bead['name'] for bead in bead_parameters]
            bead_charges = [bead.get('charge', 0.0) for bead in bead_parameters]
            charges_map[resname] = dict(zip(bead_names, bead_charges))
        return charges_map

    def read_reduction_parameters(self):
        """Read YAML reduction parameter file."""
        with open(self.reduction_file, 'rt') as f:
            data = yaml.load(f)
        self.forcefield = data['forcefield']
        self.reduction_parameters = data['beads']

    def read_topology(self):
        """Read PDB topology file."""
        rb = ptools.Rigidbody(self.allatom_file)
        self.atoms = [rb.copy_atom(i) for i in xrange(len(rb))]

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

    def reduce(self, ignore_exceptions):
        """Actual reduction method.

        Group atoms by residue then iterate over those residues to create
        coarse grain residues.

        Different kinds of exception can be raised but a simple warning is
        printed if the exception is listed in `ignore_exceptions`.

        Args:
            ignore_exception (list[class]): list of exceptions that should
                be ignored when it occurs during reduction.

        Raises:
            NoResidueReductionRulesFoundError: if a residue from topology is
                not found in reduction parameters. This happens typically with
                exotic residue names.

            IncompleteBeadError: when an atom needed to create a residue
                is not found in the input all-atom topology.

            DuplicateAtomInBeadError: when an atom from input all-atom topology
                is present several type. This is typically a bad error, has
                it means that several atoms SER:1:N have been read from
                topology (e.g).
        """
        def check_has_rule_for_residue_reduction():
            if resname not in self.reduction_parameters:
                if NoResidueReductionRulesFoundError in ignore_exceptions:
                    msg = "don't know how to handle residue {} "\
                          "(no reduction rule found for this residue)..."\
                          "skipping this residue".format(resname)
                    ptools.io.warning(msg)
                else:
                    raise NoResidueReductionRulesFoundError(resname, resid)
                return False
            return True

        def check_exception_ignored(exception):
            if type(exception) in ignore_exceptions:
                    msg = "This exception was raised while reducing all-atom model:\n{}"
                    ptools.io.warning(msg.format(exception.report()))
                    ptools.io.warning("Ignoring this exception as requested.")
            else:
                raise exception

        # Rename atoms and residues so that they will match reduction
        # parameters.
        self.rename_atoms_and_residues()

        # Set chain id to ' '.
        self._reset_chain_id()

        # Residue list: group atoms by residue tag.
        # A residue is two items: (<residue tag>, <atom list iterator>).
        residue_list = itertools.groupby(self.atoms,
                                         key=lambda atom: atom.residuetag())

        # Reduction: iterate over residues and create beads according to
        # parameters in self.reduction_parameters.
        tag_delimiter = ptools.Atomproperty.get_tag_delimiter()
        for restag, resatoms in residue_list:
            resname, resid, chain = restag.split(tag_delimiter)

            check_has_rule_for_residue_reduction()

            coarse_res = CoarseResidue(resname, int(resid),
                                       list(resatoms),
                                       self.reduction_parameters[resname])
            try:
                coarse_res.check_composition()
            except IncompleteBeadError as e:
                msg = 'An incomplete bead was found: {}.\n'.format(e.report())
                msg += 'Ignoring this bead as requested.'
                ptools.io.warning(msg)
                coarse_res.beads = [bead for bead in coarse_res.beads
                                    if not bead.is_incomplete()]
            except Exception as e:
                check_exception_ignored(e)
            self.beads += coarse_res.beads

        # Update the atom id for each bead.
        for i, bead in enumerate(self.beads):
            bead.atomId = i + 1

    def _reset_chain_id(self):
        """Set the chain identifier of all atoms from input topology to ''."""
        for atom in self.atoms:
            atom.chainId = ''

    def optimize_charges(self, delgrid):
        """Use cgopt to optimize bead charges.

        Args:
            delgrid (float): grid spacing (A).
        """
        import ptools.cgopt as cgopt

        cg_coords_x = []
        cg_coords_y = []
        cg_coords_z = []
        cg_charges = []
        cg_radii = []

        aa_coords_x = []
        aa_coords_y = []
        aa_coords_z = []
        aa_charges = []
        aa_radii = []

        aa_radii_map = self.get_atom_radii_map()
        aa_charges_map = self.get_atom_charges_map()

        for atom in self.atoms:
            aa_coords_x.append(atom.coords.x)
            aa_coords_y.append(atom.coords.y)
            aa_coords_z.append(atom.coords.z)
            aa_radii.append(aa_radii_map[atom.residType][atom.atomType])
            aa_charges.append(aa_charges_map[atom.residType][atom.atomType])

        for bead in self.beads:
            cg_coords_x.append(bead.coords.x)
            cg_coords_y.append(bead.coords.y)
            cg_coords_z.append(bead.coords.z)
            cg_radii.append(bead.radius)
            cg_charges.append(bead.charge)

        cg_charges.reverse()  # why??!!

        optimized = cgopt.optimize(self.number_of_atoms,
                                   aa_charges,
                                   aa_radii,
                                   aa_coords_x, aa_coords_y, aa_coords_z,
                                   self.number_of_beads,
                                   cg_charges,
                                   cg_radii,
                                   cg_coords_x, cg_coords_y, cg_coords_z,
                                   delgrid)

        for i, charge in enumerate(optimized):
            self.beads[i].charge = charge

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
