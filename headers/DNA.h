#ifndef DNA_H
#define DNA_H

#include <vector>
#include "BasePair.h"
#include "Movement.h"
#include "Parameter.h"
#include "rigidbody.h"

namespace PTools
{

  class DNA
  {

    public:
    ///initialize a new object with a sequence and a database of pdb to pick from. an initial movement for the construction of the dna can be precised.
    DNA(const std::string& dataBaseFile , const std::string& seq , const Movement & mov = BDNA());
    ///initialize a dna from another dna.
    DNA( const DNA& model );
    ///initialize a dna from dna in a rigidbody
    DNA( std::string dataBaseFile,Rigidbody model);
    ///initialize a hollow dna (no BasePair in the strand)
    DNA();
    ~DNA();


    ///return the number of BasePair
    unsigned int Size() const;

    ///return the number of Atom
    unsigned int AtomSize() const;

    ///return a string containing the atoms data following the PDB format
    std::string print_pdb() ;

    ///return a string containing the atoms data following the PDB format
    std::string print_pdbofStrand( std::string chain );

    ///return a string containing all the local parameter formated
    std::string print_param();

    ///write in a file the atoms data following the PDB format
    void WritePDB(std::string);

    ///change the database use for the BasePair. the new database must contain the same names for pdb that the old one.
    void change_representation(std::string);

    ///apply a Matrix/Movement to a specified BasePair. you can specify an anchor
    void apply_local(const Matrix&,int posMov, int posAnchor = 0);
    void apply_local(const Movement&,int posMov, int posAnchor = 0);

    ///apply a Matrix/Movement to all the BasePairs and reposition the DNA according to the anchor
    void applyGlobal(const Matrix&,int posAnchor);
    void applyGlobal(const Movement&,int posAnchor);
    
    ///apply a Matrix/Movement to the DNA as a rigidbody
    void apply(const Matrix&);
    void apply(const Movement&);
    

    ///apply a vector to the DNA as a rigidbody
    void Translate(Coord3D coord);

    ///return the local Matrix of the specified BasePair (for the position i the Matrix to go from i-1 to i)
    Matrix GetLocalMatrix(int pos)const;
    ///return the local Parameter of the specified BasePair (for the position i the Matrix to go from i-1 to i)
    Parameter GetLocalParameter(int pos);

    ///return a Rigidbody of the DNA()
    Rigidbody create_rigid();
    ///return a Rigidbody of the strand
    Rigidbody create_rigidOfStrand(std::string chain);


    //replace the base pair at the indicated position by the new base pair
    void ChangeBasePair(const BasePair& bp, int pos);


    /// return the RMSD between two DNA (not aligning them and assuming they are comparable)
    double rmsd(const DNA&)const;

    ///------edition functions------

    /// return the i-th BasePair of the strand
    BasePair operator[] (uint i) const {
          if (i>=this->Size()) throw std::range_error("DNA: array out of bounds");
          return strand[i];};

    /// add the basePairs of a DNA to the strand of this DNA. the specified movement do the liason betwen the two strand
    void add(const DNA & d, const Movement & mov = BDNA());
    /// add a basepair at the end of the strand of this DNA
    void add(BasePair bp, const Movement & mov = BDNA());

    ///return the specified subDNA
    DNA SubDNA(uint start, uint end)const;

    ///replace the basePair of this DNA by the basePair of a given DNA starting from a given position to the end of one of the DNAs
    void Replace(const DNA & d,int start);

    ///change the type of the base pair at position pos to the indicated type using the coresponding structure in the designed database of pdb.
    void change_type(int pos, std::string type, std::string filename );




    private:

    //attribut
    std::vector<BasePair> strand;

    //methods
    ///return a string with the seq of all the diferent chain ID of a Rigidbody.
    std::string GetChainIDs(const Rigidbody&)const;
    ///construct the strand from the sequence, the  chain Ids and a corresponding vector of Rigidbody
    void BuildStrand(std::string,std::string,const std::vector<Rigidbody> &);
    /// apply an initial Movement during the initialisation of the DNA
    void applyInitialMov(const Movement&);
    ///rebuild the DNA from a specified position. useful for taking into account a change in a base.
    Matrix Reconstruct(int pos,const Matrix&);
    ///give the BasePair a correct number according to they rank in the strand
    void ChangeFormat();
    ///apply a Movement to a specified BasePair.
    void applylocalMov(const Movement&,int pos);
    ///apply a Movement to all the BasePairs
    void applyglobalMov(const Movement& );
    ///reposition the DNA according to the anchor
    void Relocate(const BasePair& anchor,int posAnchor);

    ///initialize a new object from a PDB file
    void BuildDNAfromPDB ( std::string database, std::string pdbfile);
    void BuildDNAfromModel(std::string dataBaseFile,Rigidbody model  );
    ///check if a file have a pdb extension
    bool IsPdbFile (std::string)const;
    ///return the sequence of a DNA model
    std::string GetSeq ( Rigidbody& model);
    ///return a vector with an example of each base
    std::vector<Rigidbody> BuildVbase(std::string chainIDs, Rigidbody& dataBase)const;

    ///create the different base in strand following the seq order.
    void AssembleSeq (const std::string & dataBaseFile, const std::string& seq);

    ///change the numerotation of the base in the model to conform to the following order
    ///A 1 2 3
    ///B 6 5 4
    void RenumberModel (Rigidbody& model);


    // test if the model follow the jumna convention
    //A 1 2 3
    //B 4 5 6
    bool IsJumna ( Rigidbody& model);

    //detect and delete single base at extremeties of DNA
    Rigidbody DelSingleBase (Rigidbody& model);

    //use by delsinglebase
    int CalcPart (int solution [] , int pos1, int pos2, int l )const;

    //detect if two string are aligned. a shift can be precised
    bool IsAlign(std::string s1,std::string s2,int shift = 0)const;

    ///place the base in the same position as the model
    void PlaceBasePairs( Rigidbody& model);

    ///return the base pair composed of the base on posA in the strand A of model and the base on posB in the strand B of model
    Rigidbody GetModelOfBasePair( Rigidbody& model,int posA,int posB);

    ///return the matrix betwen a model base pair and the basepair on pos in strand
    Matrix GetMatBetwenBasePair(Rigidbody& modelOfBasePair,int pos);


  };

}//end namespace

#endif // DNA_H
