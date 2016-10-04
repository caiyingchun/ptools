
Protein-DNA complex: 1K79
=========================

The 1K79 complex [#1K79]_ has two partners,

- the ETS protein: chain A, 104 residues, 873 atoms (defined in the following as the receptor),
- a DNA molecule: chain B and C, 30 bases, 607 atoms (defined in the following as the ligand).

.. [#1K79] ``http://www.rcsb.org/pdb/cgi/explore.cgi?pdbId=1K79``

.. \subsubsection{Extraction of the docking partners}
.. Both partners are extracted automatically with PTools from the Python interpreter:
.. \begin{verbatim}
.. from ptools import *
.. pdb=Rigidbody("1K79.pdb")
.. selA=pdb.SelectChainId("A")
.. selB=pdb.SelectChainId("B")
.. selC=pdb.SelectChainId("C")
.. WritePDB(selA.CreateRigid(), "receptor.pdb")
.. WritePDB( (selB | selC).CreateRigid(), "ligand.pdb")
.. exit()
.. \end{verbatim}

.. \subsubsection{Coarse grain reduction}
.. All-atom molecules are then translated into coarse grain (reduced) molecule for further docking. 

.. For the receptor (protein): 
.. \begin{verbatim}
.. reduce.py --ff attract1 --warnonly receptor.pdb > receptor.red
.. \end{verbatim}

.. This command generates few warnings due to missing atoms in the Lys436 residue. When an atom is missing, the corresponding bead is not created. You will have to check if this is an important issue for your system and fix your PDB with your favourite tool. Please also note that the \verb!reduce! script doesn't report anything you if a complete residue is missing (this frequently occurs in loops).

.. \begin{verbatim}
.. ./at2cg.prot.dat: found the definition of residues ARG GLU GLN LYS TRP MET PHE TYR HIS GLY ASN ALA ASP CYS ILE LEU PRO SER THR VAL 
.. ./at2cg.prot.dat: created the partition for residues ARG(3 beads) GLU(3 beads) GLN(3 beads) LYS(3 beads) TRP(3 beads) MET(3 beads) PHE(3 beads) TYR(3 beads) HIS(3 beads) GLY(1 beads) ASN(2 beads) ALA(2 beads) ASP(2 beads) CYS(2 beads) ILE(2 beads) LEU(2 beads) PRO(2 beads) SER(2 beads) THR(2 beads) VAL(2 beads) 
.. ./ff_param.dat: reading force field parameters for bead 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 
.. Load atomic file receptor.pdb with 873 atoms 
.. Number of residues: 104
.. Reading all atoms and filling beads:
.. Coarse graining:
.. ERROR: missing atom CG in bead CB 16 for residue LYS 436. Please fix your PDB!
.. Continue execution as required ...
.. ERROR: missing atom CE in bead CE 17 for residue LYS 436. Please fix your PDB!
.. Continue execution as required ...
.. Coarse grain (reduced) output: 246 beads 
.. \end{verbatim}

.. The reduced protein, {\tt receptor.red}, contains 246 beads.\\

.. For the ligand (DNA), do not forget the \verb@--dna@ option:
.. \begin{verbatim}
.. reduce.py --ff attract1 --dna --warnonly ligand.pdb  > ligand.red
.. \end{verbatim}
.. This also generates few warnings due to incomplete bases:
.. \begin{verbatim}
.. ./at2cg.dna.dat: found the definition of residues A G C T 
.. ./at2cg.dna.dat: created the partition for residues A(6 beads) G(6 beads) C(5 beads) T(5 beads) 
.. ./ff_param.dat: reading force field parameters for bead 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 
.. Load atomic file ligand.pdb with 607 atoms 
.. Number of residues: 30
.. Reading all atoms and filling beads:
.. Coarse graining:
.. ERROR: missing atom O1P in bead GP1 30 for residue T 1. Please fix your PDB!
.. Continue execution as required ...
.. ERROR: missing atom O2P in bead GP1 30 for residue T 1. Please fix your PDB!
.. Continue execution as required ...
.. ERROR: missing atom P in bead GP1 30 for residue T 1. Please fix your PDB!
.. Continue execution as required ...
.. ERROR: missing atom O1P in bead GP1 30 for residue C 1. Please fix your PDB!
.. Continue execution as required ...
.. ERROR: missing atom O2P in bead GP1 30 for residue C 1. Please fix your PDB!
.. Continue execution as required ...
.. ERROR: missing atom P in bead GP1 30 for residue C 1. Please fix your PDB!
.. Continue execution as required ...
.. Coarse grain (reduced) output: 162 beads
.. \end{verbatim}

.. The reduced DNA, {\tt ligand.red}, ends up with 162 beads. \\

.. As previously said, the reduced files generated are PDB-like structure files 
.. that can be read by most visualization programs (Rasmol, Pymol, VMD). 
.. Always visualize both all-atom and coarse grain structures to check the 
.. reduction worked properly (see Fig.~\ref{1K79_at_cg} for 1K79).

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

