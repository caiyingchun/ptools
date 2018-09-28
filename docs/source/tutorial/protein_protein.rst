
Protein-protein complex: 1CGI
=============================

The 1CGI complex [#]_ has two partners:

- the bovine chymotrypsinogen A: chain E, 245 residues, 1799 atoms,
- a variant of the human pancreatic secretory trypsin inhibitor: chain I, 56 residues, 440 atoms.


Extraction of the docking partners
----------------------------------

Before docking, one has to separate both partners.
This is possible with vizualisation software such as Pymol [#]_ or VMD [#]_, 
and also directly with PTools.

.. code-block:: python

    # Load the PTools library.
    import ptools

    # Read the PDB file of the complex.
    pdb = ptools.Rigidbody("1CGI.pdb")

    # The chain selection allows the separation between chain E and I.
    selectE = pdb.select_chain_id("E")
    selectI = pdb.select_chain_id("I")

    # Create both chains as independant Rigidbody objects and save them in PDB files. 
    # The largest protein is defined as the receptor (chain E) and the smallest 
    # as the ligand (chain I).
    protE = selectE.create_rigid()
    protI = selectI.create_rigid()
    ptools.write_pdb(protE, "receptor.pdb")
    ptools.write_pdb(protI, "ligand.pdb")

    # Or more quickly:
    # ptools.write_pdb(selectE.create_rigid(), "receptor.pdb")
    # ptools.write_pdb(selectI.create_rigid(), "ligand.pdb")


.. [#] http://www.rcsb.org/pdb/cgi/explore.cgi?pdbId=1CGI
.. [#] http://pymol.sourceforge.net
.. [#] http://www.ks.uiuc.edu/Research/vmd


Coarse-grain reduction
----------------------

This step translates the all-atom receptor and ligand molecules into
coarse-grained (reduced) molecules for docking.

The following commands should be typed in a terminal.

.. code-block:: bash

    ptools reduce --prot receptor.pdb -o receptor.red
    ptools reduce --prot ligand.pdb -o ligand.red

In which ``--prot`` specifies that the molecule is a protein.

In this example, ``receptor.red`` contains 522 beads and
``ligand.red`` contains 126 beads, whereas the original PDBs contained
1799 and 440 atoms, respectively.

The complete ``reduce`` command usage can be obtained by typing::

  ptools reduce -h

The reduced files generated are PDB-like structure files that can be read by
many visualization programs (Pymol, VMD, Chimera, ...). 
Always visualize both all-atom and coarse grain structures to check that the
reduction worked properly (see :numref:`fig_1CGI_at_cg_receptor` and 
:numref:`fig_1CGI_at_cg_ligand` for 1CGI).

.. _fig_1CGI_at_cg_receptor:
.. figure:: figures/1CGI_receptor.png
   :align: center

   All-atom (green sticks) and reduced (red spheres) representations of 
   the receptor protein.


.. _fig_1CGI_at_cg_ligand:
.. figure:: figures/1CGI_ligand.png
   :align: center

   Same as previous for ligand.


.. [#Basdevant2007] Basdevant, N., Borgis, D. & Ha-Duong, T. A coarse-grained protein-protein potential derived from an all-atom force field. *Journal of Physical Chemistry B* **111**, 9390-9399 (2007).


ATTRACT parameters
------------------

.. important::

  **This section is not yet finished.**


The parameters required for running an ATTRACT calculation are found in the
file ``attract.inp``, which typical content is:

.. literalinclude:: attract.inp
    :linenos:

Line 1 indicates the number of minimisations performed by ATTRACT
for each starting position (six in the present case).

Line 2 is used for internal development purposes and should not be modified.

The following 6 lines are the characteristics of each minimization:

- the first column is the number of steps in the minimization
- the last column is the square of the cutoff distance for calculating the interaction energy

Trailing lines are ignored.

In the present case, the simulation starts with a very large cutoff value of
9900 Å\ :sup:`2` (≈ 99 Å) and is gradually decreased to end with
500 Å\ :sup:`2` (≈ 22 Å).


Simple optimization
-------------------

Before running a systematic docking simulation which could take several hours,
a simple optimization (energy minimization) may be performed in order to verify
the functioning of the energy minimization process. PTools will thus
minimize the interaction energy of the complex starting from the provided
receptor and ligand positions, and will not perform a systematic search of
the rotational and translational degrees of freedom (which are discussed in the next
section).

The simple optimization procedure is also useful in re-docking studies,
to find if the receptor-ligand interaction energy
in a protein-protein complex whose structure is known is at or near a minimum.

Single mode optimizations are also useful if the user wishes to make a movie
of an minimization process (see section **REF::video**).

A single optimization with ATTRACT requires

- a coarse-grained receptor (fixed) file (``receptor.red``)
- a coarse-grained (mobile) file (``ligand.red``)
- docking parameters file (``attract.inp``)

The single optimization may thus be obtained by::

    ptools attract -r receptor.red -l ligand.red --ref=ligand.red -s > single.att

As with the ``reduce`` command, the attract1 forcefield is chosen by default. The
other options here are:

- ``-r`` or ``--receptor`` defines the receptor file.
- ``-l`` or ``--ligand`` defines the ligand file.
- ``-s`` specifies that a single series of minimizations (*simple*) will be performed
  starting with the ligand in its provided position.
- ``--ref`` defines a ligand PDB file (in the reduced representation) as a reference.
  After optimization, the RMSD is calculated between this reference structure and
  the simulated ligand.

The complete ``reduce`` command usage can be obtained by typing::

    ptools attract -h

The content of the output file ``single.att`` is the following:

.. literalinclude:: single.att_ref
    :linenos:

- **lines 22-41**: intermediate minimization results.
- **lines 42--43:** final results.
  With a single series of minimization, the default translation (``Trans``)
  is 0 and the default rotation (``Rot``) is 0. 
  Energy (``Ener``) is given in RT unit and the C\ :sub:`α`-RMSD 
  (``RmsdCA_ref``) in Å if the ``--ref`` option is specified.
- **lines 44--49:** rotation/translation matrix of the ligand compared to its initial position.


In this complex the final energy is -58.4 RT unit and the RMSD is 1.2 Å, which is pretty
close to the ligand's position in the experimental structure (in a *perfect* simulation, RMSD would be 0.0 Å).


.. _my_dummy_label:

Initial ligand positions for systematic docking
-----------------------------------------------

Rigid body movements in translational and rotational space can be described
with 3 variables or degrees of freedom (`x`, `y` and `z`) in translation 
and 3 variables (φ,  ψ and θ) in rotation. The rigid body 
transformation is illustrated in :numref:`fig_rigidbody`.

.. _fig_rigidbody:

.. figure:: figures/rigid_body_freedom.png
   :align: center

   Rigid body transformation in translational and rotational space.



Translations
^^^^^^^^^^^^

For the purpose of a systematic docking simulation, (translational) 
starting points are placed  all around the receptor.
The Python script ``translate.py`` employs a slightly modified Shrake and Rupley [#Shrake1973]_
method to define starting positions from the receptor surface.
The surface generation functions are implemented in the PTools library.
The script first reads the coarse grain (reduced) receptor and ligand files,
then generates a grid of points at a certain distance from the receptor and outputs
the grid with a given density.

.. note:: a density option (``-d``) controls the minimum distance between starting 
          points (in Å).
          The default value is 10.0 Å. 

In the present case::

    translate.py receptor.red ligand.red > translation.dat


Vizualization of the starting points may be obtained with any vizualisation 
software by renaming ``translation.dat`` in ``translation.pdb`` and then
by removing the first line of ``translation.pdb`` (that indicates the total 
number of starting points).
In this example, :numref:`fig_1CGI_translation` shows the receptor surounded by
the 204 starting points.

.. _fig_1CGI_translation:
.. figure:: figures/1CGI_translation.png
   :align: center

   Coarse grain receptor in green spheres and starting points as orange spheres.


.. [#Shrake1973] Shrake, A. & Rupley, J.A. Environment and exposure to solvent of protein atoms. Lysozyme and insulin. Journal of Molecular Biology 79, (1973).


Rotations
^^^^^^^^^

Each position in translation (*i.e.* each ``ATOM`` line of the file ``translation.dat``)
is associated with a certain number of rotations corresponding to the three (φ,  ψ and θ)
rotational degrees of freedom.
The rotation distribution is detailed in the file ``rotation.dat``,
which has the following format:

.. code-block:: bat
   :linenos:
    
          7   6
        0.0   1
       30.0   5
       60.0   9
       90.0  13
      120.0   9
      150.0   5
      180.0   1

First item of line 1 indicates the number of φ angles (7) that are listed underneath 
(0.0, 30.0, 60.0, 90.0, 120.0, 150.0 and 180.0°).
In the second column, the item on line 1 is the number of θ angles (here 6).
Figures underneath are the number of ψ angles associated to each φ angle.

For instance, with φ = 30°, there are 5 ψ angles (equally distributed on a
circle, *i.e.* 72, 144, 216, 288 and 360°) and 6 θ angles.
In total, there are 1 + 5 + 9 + 13 + 9 + 5 + 1) × 6 = 258 rotations per
translation.

Ultimately, there are in this example a total of 204 starting points × 258 rotations 
which gives 52,632 starting geometries for the ligand.

Systematic docking simulation
-----------------------------

For a full systematic docking in the translational and rotational space
(using both ``translation.dat`` and ``rotation.dat`` files), the command line is::

    attract.py -r receptor.red -l ligand.red --ref=ligand.red > docking.att &

In addition to the required files for a single optimization, a systematic docking with ATTRACT requires also:

- the translation starting points (``translation.dat``),
- the rotations performed for each translation starting point (``rotation.dat``)

The output file ``docking.att`` contains all informations on the docking
simulation.
It contains the ouput of all series of minimizations (with the specification
of translation and rotation number).

For the 1CGI complex, the systematic docking took 19 hours on a single
processor of a 64~bit Intel Xeon 1.86 GHz 2 Go RAM computer.
The size of the output file ``docking.att`` is roughly 77 Mo.

Systematic docking output analysis
----------------------------------

The 10 best geometries found during the docking simulation can be listed with::

    cat docking.att | egrep -e "^==" | sort -n -k4 | head


For the previsous docking simulation of 1CGI, this gives::

    ==      133     92   -58.3541443 1.19429783478
    ==       73    229   -58.3541441 1.19413397471
    ==      133     21   -58.3541437 1.19566121232
    ==       73    235   -58.3541436 1.19394986862
    ==      136     21   -58.3541424 1.19584401069
    ==      130    141   -58.3541411  1.1930478392
    ==      194    219   -58.3541410  1.1961246513
    ==       73      7   -58.3541406 1.19314844151
    ==      136    155   -58.3541400 1.19273140092
    ==      163     70   -58.3541387 1.19596166869


With each column meaning:

1. tag characters (``==``) to quickly find the result of each set of minimizations
2. translation number (starts at 1)
3. rotation number (starts at 1)
4. final energy of the complex in RT unit
5. final RMSD in Å, if the ``--ref`` option is provided.


Any simulated ligand structure can be extracted with the script ``extract.py``::

    extract.py docking.att ligand.red 133 92 > ligand_1.red

with the parameters:

- the ouput file of the docking simulation (``docking.att``)
- the initial ligand file (``ligand.red``)
- a translation number (``133``)
- a rotation number (``92``)
- an output ligand file (``ligand_1.red``)


:numref:`fig_1CGI_dock_front` and :numref:`fig_1CGI_dock_top` show the best
solution of the docking simulation and the reference complex.
With a RMSD of 1.2 Å between both structures, the docking simulation found very
well the initial complex structure.


.. _fig_1CGI_dock_front:
.. figure:: figures/1CGI_dock1_front.png
   :align: center

   Reduced representations of receptor (green), ligand at reference 
   position (red) and ligand from the best solution (lowest energy) of the 
   docking (blue). Beads have exact van der Waals radii.
   Front view.

.. _fig_1CGI_dock_top:
.. figure:: figures/1CGI_dock1_top.png
   :align: center

   Same as above. Top view.


In case an experimental structure of the system is known (as in this example), 
it is possible to calculate the interface RMSD (iRMSD) and the native fraction 
(fnat) as defined by the CAPRI contest [#capri]_
using the following scripts::

    irmsd.py receptor.red ligand.red ligand_1.red
    fnat.py receptor.red ligand.red ligand_1.red

For iRMSD, output is in Å and fnat is given as a proportion (between 0.0 and 1.0).
Parameters are defined as:

- the receptor file (``receptor.red``)
- the initial ligand file (``ligand.red``)
- the output ligand file (``ligand_1.red``)

Our clustering algorithm implemented in ``cluster.py`` can rapidly filter near identical solutions 
without requiring a preselected number of desired clusters.
The algorithm is based on RMSD comparison and an additional energy criterion
can be included (see script options, by default RMSD and energy criterions are
1 Å and 1 RT unit respectively)::

    cluster.py docking.att ligand.red > docking.clust

with the parameters:

- an ouput of the docking simulation (``docking.att``)
- the initial ligand file (``ligand.red``)
- an output cluster file (``docking.clust``)

The first lines of the output cluster file are:

.. code-block:: bat
   :linenos:

          Trans    Rot          Ener    RmsdCA_ref   Rank   Weight
    ==      133     92   -58.3541443     1.1942978      1       55
    ==      196    132   -40.3704483    48.8195971      2        1
    ==      164    212   -39.3828793     6.4968451      3        2
    ==       71    102   -38.7843145    14.7084754      4       14
    ==       73    126   -38.5826662    11.5175880      5        3
    ==      129    223   -38.3872389    12.3477797      6        3
    ==      132    245   -38.3429828    14.0028863      7       10
    ==      133    131   -38.1570360    16.0382603      8       17

Line 1 is a comment line, next lines are clusters. For each cluster (line)
is specified:

- a representative structure with the corresponding translation and rotation
  numbers (column 2, ``Trans``, and 3, ``Rot``), interaction energy 
  (column 4, ``Ener``) and RMSD (column 5, ``RmsdCA_ref``) 
  from the reference ligand structure
- the number of the cluster (column 6, ``Rank``)
- the number of structures (docking solutions) in this cluster (column
  7, ``Weight``)


The large weight of the best solution shows the very good convergence of the
docking simulation.

.. [#capri] ``http://capri.ebi.ac.uk``
