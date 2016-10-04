
Protein-DNA complex: 1K79
=========================

The 1K79 complex [#1K79]_ has two partners,

- the ETS protein: chain A, 104 residues, 873 atoms (defined in the following as the receptor),
- a DNA molecule: chain B and C, 30 bases, 607 atoms (defined in the following as the ligand).

.. [#1K79] ``http://www.rcsb.org/pdb/cgi/explore.cgi?pdbId=1K79``

Extraction of the docking partners
----------------------------------

Both partners are extracted automatically with PTools from the Python interpreter::

    from ptools import *
    pdb = Rigidbody("1K79.pdb")
    selA = pdb.SelectChainId("A")
    selB = pdb.SelectChainId("B")
    selC = pdb.SelectChainId("C")
    WritePDB(selA.CreateRigid(), "receptor.pdb")
    WritePDB((selB | selC).CreateRigid(), "ligand.pdb")
    exit()


Coarse grain reduction
----------------------

All-atom molecules are then translated into coarse grain (reduced) molecule for further docking. 

For the receptor (protein)::

    reduce.py --ff attract1 --warnonly receptor.pdb > receptor.red


This command generates few warnings due to missing atoms in the Lys436 residue.
When an atom is missing, the corresponding bead is not created.
You will have to check if this is an important issue for your system and fix
your PDB with your favourite tool.
Please also note that the ``reduce`` script doesn't report anything you if
a complete residue is missing (this frequently occurs in loops)::

    ./at2cg.prot.dat: found the definition of residues ARG GLU GLN LYS TRP MET PHE TYR HIS GLY ASN ALA ASP CYS ILE LEU PRO SER THR VAL 
    ./at2cg.prot.dat: created the partition for residues ARG(3 beads) GLU(3 beads) GLN(3 beads) LYS(3 beads) TRP(3 beads) MET(3 beads) PHE(3 beads) TYR(3 beads) HIS(3 beads) GLY(1 beads) ASN(2 beads) ALA(2 beads) ASP(2 beads) CYS(2 beads) ILE(2 beads) LEU(2 beads) PRO(2 beads) SER(2 beads) THR(2 beads) VAL(2 beads) 
    ./ff_param.dat: reading force field parameters for bead 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 
    Load atomic file receptor.pdb with 873 atoms 
    Number of residues: 104
    Reading all atoms and filling beads:
    Coarse graining:
    ERROR: missing atom CG in bead CB 16 for residue LYS 436. Please fix your PDB!
    Continue execution as required ...
    ERROR: missing atom CE in bead CE 17 for residue LYS 436. Please fix your PDB!
    Continue execution as required ...
    Coarse grain (reduced) output: 246 beads 


The reduced protein, ``receptor.red``, contains 246 beads.

For the ligand (DNA), do not forget the ``--dna`` option::

    reduce.py --ff attract1 --dna --warnonly ligand.pdb  > ligand.red

This also generates few warnings due to incomplete bases::

    ./at2cg.dna.dat: found the definition of residues A G C T 
    ./at2cg.dna.dat: created the partition for residues A(6 beads) G(6 beads) C(5 beads) T(5 beads) 
    ./ff_param.dat: reading force field parameters for bead 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 
    Load atomic file ligand.pdb with 607 atoms 
    Number of residues: 30
    Reading all atoms and filling beads:
    Coarse graining:
    ERROR: missing atom O1P in bead GP1 30 for residue T 1. Please fix your PDB!
    Continue execution as required ...
    ERROR: missing atom O2P in bead GP1 30 for residue T 1. Please fix your PDB!
    Continue execution as required ...
    ERROR: missing atom P in bead GP1 30 for residue T 1. Please fix your PDB!
    Continue execution as required ...
    ERROR: missing atom O1P in bead GP1 30 for residue C 1. Please fix your PDB!
    Continue execution as required ...
    ERROR: missing atom O2P in bead GP1 30 for residue C 1. Please fix your PDB!
    Continue execution as required ...
    ERROR: missing atom P in bead GP1 30 for residue C 1. Please fix your PDB!
    Continue execution as required ...
    Coarse grain (reduced) output: 162 beads

The reduced DNA, ``ligand.red``, ends up with 162 beads.

As previously said, the reduced files generated are PDB-like structure files 
that can be read by most visualization programs (Rasmol, Pymol, VMD). 
Always visualize both all-atom and coarse grain structures to check the 
reduction worked properly (see Fig.~\ref{1K79_at_cg} for 1K79).

.. \begin{figure}[htbp]
.. \center
.. {\textbf A}
.. \includegraphics*[width=0.35\textwidth]{img/1K79_receptor.png}
.. \hspace*{2cm}
.. {\textbf B}
.. \includegraphics*[width=0.20\textwidth]{img/1K79_ligand.png}
.. \caption{All-atom (green sticks) and reduced (red spheres) representation 
.. of both partners in 1K79. Receptor, protein (A) and ligand, DNA (B).}
.. \label{1K79_at_cg}
.. \end{figure}


ATTRACT parameters
------------------

The content of the ``attract.inp`` parameters file is identical to the one
previously used for protein--protein docking.


Simple optimization
-------------------

An ATTRACT single optimization is done with::

    attract.py -r receptor.red -l ligand.red --ref=ligand.red -s > single.att

Here, the final energy is -38.4 RT unit and the RMSD is 1.3 Å which is very
close from the initial position.

Please note, that the RMSD is not computed here on C:sub:``α`` atoms since
the ligand is a DNA molecule.
The RMSD is calculated with all DNA beads. 


Initial ligand positions for systematic docking
-----------------------------------------------

::
    translate.py receptor.red ligand.red > translation.dat

In the present case, the ``translation.dat`` file contains 179 starting points.


Systematic docking simulation
-----------------------------

A systematic docking simulation is then::

    attract.py -r receptor.red -l ligand.red --ref=ligand.red > docking.att &

The output file ``docking.att`` contains all informations on the docking 
simulation. It contains the ouput of all series of minimizations 
(with the specification of translation and rotation numbers).

For the 1K79 complex, the systematic docking took roughly 11 hours on a
single processor of a 64 bit Intel Xeon 1.86 GHz 2 Go RAM computer.
The size of the output file ``docking.att`` is about 67 Mo.


Systematic docking output analysis
----------------------------------

The 10 best geometries found during the docking simulation can be listed with::

    cat docking.att | egrep -e "^==" | sort -n -k4 | head

This gives::

    ==       30    157   -38.4463924 1.25369709657
    ==      169     51   -38.4463903 1.25534808001
    ==      148    234   -38.4463875 1.25581284912
    ==       87    257   -38.4463867 1.25409925951
    ==      109    231   -38.4463855 1.25469537295
    ==      104    236   -38.4463848 1.25571565339
    ==      144     27   -38.4463848 1.25495212761
    ==      164    255   -38.4463819 1.25410121719
    ==      163     27   -38.4463817 1.25446355377
    ==       87    241   -38.4463806  1.2554586922


We can then extract the best structure obtained (translation number 30 
and rotation number 157, illustrated Fig.~\ref{1K79_dock})::

    extract.py docking.att ligand.red 30 157 > ligand_1.red

.. \begin{figure}[htbp]
.. \center
.. {\textbf A}
.. \includegraphics*[width=0.30\textwidth]{img/1K79_dock1_front.png}
.. \hspace*{2cm}
.. {\textbf B}
.. \includegraphics*[width=0.30\textwidth]{img/1K79_dock1_top.png}
.. \caption{Reduced representations of receptor (green), ligand at reference 
.. position (red) and ligand from the best solution (lowest energy) of the 
.. docking (blue). Front (A) and top (B) views. Beads have exact van der Waals 
.. radii. With a RMSD of 1.6~\AA\ between the reference and the simulated ligand 
.. structures, the docking simulation found very well the initial complex 
.. structure.}
.. \label{1K79_dock}
.. \end{figure}

As for protein-protein example, one can compute the native fraction (fnat)::

    fnat.py receptor.red ligand.red ligand_1.red

That gives ``0.824561403509`` in this example. However, the interface 
RMSD (iRMSD) calculation is not yet implemented for DNA.

Our clustering algorithm implemented in ``cluster.py`` can rapidly group
near identical solutions without requiring a preselected number of desired clusters.
The algorithm is based on RMSD comparison and an additional energy criterion can 
be included (see script options, by default RMSD and energy criterions are 
1 Å and 1 RT unit respectively)::

    cluster.py docking.att ligand.red > docking.clust

The first lines of the output cluster file are:

.. code-block:: bat
   :linenos:

          Trans    Rot          Ener    RmsdCA_ref   Rank   Weight
    ==       30    157   -38.4463924     1.2536971      1       46
    ==      152    180   -36.8164268    29.0984166      2       17
    ==       97    155   -36.3644447    28.7048437      3       21
    ==       98     56   -36.0763672     6.3710149      4       22
    ==       32    244   -35.1526795    28.8685938      5       31
    ==       24      9   -34.8754859    12.7403727      6       13
    ==      146     15   -34.3673609    20.3370509      7       13
    ==      150    210   -33.6537513    17.1449536      8       17

The large weight of the best solution shows the very good convergence of the
docking simulation.


