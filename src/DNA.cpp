#include "rigidbody.h"
#include "pdbio.h"
#include "superpose.h"
#include "atomselection.h"
#include "DNA.h"
#include "Movement.h"
#include "Parameter.h"

#include <iostream>
#include <fstream>
#include <limits>
#include <limits.h>
#include <numeric>
#include <stdexcept>


using namespace std;
using namespace PTools;


//constructor/destructor
DNA::DNA(const string& dataBaseFile, const string& seq, const Movement& mov)
{
    //if we want to build the dna from a model
    if(IsPdbFile (seq))
    {
        BuildDNAfromPDB ( dataBaseFile, seq );
    }
    else
    {
        AssembleSeq (dataBaseFile,seq);
        ApplyInitialMov(mov);
    }
}

DNA::DNA( const DNA& model )
{
    unsigned int modelSize  = model.Size();
    for (uint i =0; i< modelSize; i++)
    {
        strand.push_back(model[i]);
    }
}

DNA::DNA( string dataBaseFile, Rigidbody model)
{
    BuildDNAfromModel(dataBaseFile,model);
}

DNA::DNA()
{

}
void DNA::BuildDNAfromPDB (string dataBaseFile, string pdbFile )
{
    Rigidbody model = Rigidbody(pdbFile);
    BuildDNAfromModel(dataBaseFile,model);
}

void DNA::BuildDNAfromModel(string dataBaseFile,Rigidbody model)
{
    RenumberModel (model);
    model = DelSingleBase (model);
    string seq = GetSeq(model);
    AssembleSeq (dataBaseFile,seq);

    PlaceBasePairs(model);
}

DNA::~DNA()
{

}

void DNA::PlaceBasePairs( Rigidbody& model)
{
    unsigned int DNASize  = (strand.size()*2)-1;
    unsigned int strandSize  = strand.size();
    Parameter param =Parameter();
    for ( unsigned int i = 0; i < strandSize; i++ )// strandSize
    {
        Rigidbody modelOfBasePair = GetModelOfBasePair( model, i, DNASize-i);
        strand[i].apply(GetMatBetwenBasePair ( modelOfBasePair,i ));
    }
}


Matrix DNA::GetMatBetwenBasePair( Rigidbody& modelOfBasePair,int pos)
{
    Parameter param =Parameter();
    Rigidbody secondAxis = strand[pos].GetRigidBody();
    Superpose_t sup =superpose (param.BuildAxisCentered(modelOfBasePair), param.BuildAxisCentered( secondAxis ) );
    return sup.matrix;
}


void DNA::RenumberModel (Rigidbody& model)
{

  unsigned int tempId = model.GetAtomProperty(0).residId;
  string chain;
  unsigned int nbRes=0;
  unsigned int second = 0;

    unsigned int strandSize = 0;
    if ((model.SelectAtomType("C1'").Size() / 2) > 0) {
        strandSize = model.SelectAtomType("C1'").Size() / 2;
    } else if ((model.SelectAtomType("C1*").Size() / 2) > 0) {
        strandSize = model.SelectAtomType("C1*").Size() / 2;
    } else if((model.SelectAtomType("GS1").Size() / 2) > 0) {
        strandSize = model.SelectAtomType("GS1").Size() / 2;
    }

  bool isjumna = IsJumna(model);
  unsigned int modelSize=model.Size();
  chain = "A";
  for (unsigned int i =0; i < modelSize; i++ )
  {
    Atomproperty ap=model.GetAtomProperty(i);
    unsigned int Id = ap.residId;
    if ( tempId != Id )
    {

        if (nbRes >= strandSize -1){
            chain = "B";
            if (isjumna)
            {
                if (second == 0)
                {
                    second=nbRes*2 +1;
                }
                nbRes= second--;
                tempId =Id;
            }
            else
            {
                tempId =Id;
                nbRes++;
            }
        }
        else
        {
            tempId =Id;
            nbRes++;
        }
    }
    ap.residId = nbRes;
    ap.chainId = chain;
    model.SetAtomProperty(i,ap);
  }
}

bool DNA::IsJumna ( Rigidbody& model)
{
   //jumna have an inversed numerotation so on a 10 base dna (strand A: 0,1,2,3,4 and strand B:5,6,7,8,9)
   //the base 0 is associated with 5 instead of 9.
   //to check wich convention is followed, I'm gonna test the distance between 0-5 and 0-9, the shorter being the correct coupling
    AtomSelection sel = model.SelectAtomType("C1'");
    if (sel.Size() == 0) sel = model.SelectAtomType("C1*");
    if (sel.Size() == 0) sel = model.SelectAtomType("GS1");


    double d1 = Dist(sel[0],sel[sel.Size()-1]);
    double d2 = Dist(sel[0],sel[sel.Size()/2]);

    return (d1>d2);
}

Rigidbody DNA::DelSingleBase (Rigidbody& model)
{
    string seq;
    unsigned int strandSize;
    Rigidbody newModel = Rigidbody();

    if ((model.SelectAtomType("C1'").Size()) >0)
    {
        strandSize = model.SelectAtomType("C1'").Size();
    }else if ((model.SelectAtomType("C1*").Size()) >0)
    {
        strandSize = model.SelectAtomType("C1*").Size();
    }else if ((model.SelectAtomType("GS1").Size()) >0)
    {
        strandSize = model.SelectAtomType("GS1").Size();
    }else {return model;}
    for ( unsigned int i=0 ; i< strandSize ; i++ )
    {
         string type = model.SelectResRange( i, i)[0].residType;
         // /!\ the order of the check is important! somme pdb use a CYT description for C, a wrong order could detect this as a T
         if      ( type.find ('G') != string::npos || type.find ('g') != string::npos) seq+='G';
         else if ( type.find ('C') != string::npos || type.find ('c') != string::npos) seq+='C';
         else if ( type.find ('A') != string::npos || type.find ('a') != string::npos) seq+='A';
         else if ( type.find ('T') != string::npos || type.find ('t') != string::npos) seq+='T';
         else {
            cerr <<"unrecognised resid type for base "<< i+1 <<" : "<<type<< endl;
            exit(0);
         };

    }
    int l = seq.length();

    int solution[l];
    for (int i=0; i<l;i++){solution[i]=0;}

    string rseq = seq;
    for (int i = 0; i<l;i++){
        if      (seq[l-i-1]=='A')  rseq[i]='T';
        else if (seq[l-i-1]=='T')  rseq[i]='A';
        else if (seq[l-i-1]=='G')  rseq[i]='C';
        else if (seq[l-i-1]=='C')  rseq[i]='G';
    }
    //cout << seq << " " << rseq.length() << endl;
    if (IsAlign(seq,rseq))
    {
        return model;
    }
    else
    {
        //build matrix
	int mat [l][l];
        for (int i =0; i<l; i++){
            for(int j =0; j<l; j++){
                mat[i][j] = 0;
            }
        }
	//fill it
        for (int i=l-1; i>=0;i--)
        {
            for(int j =0; j<l; j++)
            {
                if ((i == j) || (i-1 == j)|| (i>j))
                {
                    mat[i][j] = 0;
                }
                else
                {
                    int one =0;
                    if ((seq[i]=='A' && seq[j]=='T') || (seq[i]=='T' && seq[j]=='A') || (seq[i]=='G' && seq[j]=='C') || (seq[i]=='C' && seq[j]=='G'))
                    {
                         one = mat[i+1][j-1] +1;
                    }
                    int two = mat[i+1][j];
		    int three=mat[i][j-1];
		    mat[i][j] = max(max(one, two),three);

                }
            }
        }
	//go trougth it to find aligned part

        int i = 0;
        int j= l-1;
        int current =mat[i][j];
        while (current !=0)
        {
            int pair = mat[i+1][j-1];
            if(pair < mat[i+1][j])
            {
                current=mat[i+1][j];
                i++;
            }
            else if (pair< mat[i][j-1])
            {
                current=mat[i][j-1];
		j--;
            }
            else
            {
                if ((seq[i]=='A' && seq[j]=='T') || (seq[i]=='T' && seq[j]=='A') || (seq[i]=='G' && seq[j]=='C') || (seq[i]=='C' && seq[j]=='G'))
                {
			solution[i]=1;
			solution[j]=1;
                }
		i++;
		j--;
		current = pair;
            }
        }


        //print matrix
      /*  for (int i =0; i<l; i++){
            for(int j =0; j<l; j++){
                cout << mat[i][j];
            }
            cout << endl;
        }
    cout <<  endl;
    cout <<  endl;
    */
    //check ambiguity
    for (int i =0; i<l; i++)
    {
        if(solution[i]==0)
        {
            char c = seq[i];
            int start = i;
            int end = i;
            //find the start
            while (seq[start]==c) start--;
            start++;
            while (seq[end]==c) end++;
            end--;
            if ((start-end) == 0) continue;
            int diff [end-start];
            for (int j =start;j<end;j++)
            {
                diff[j-start]= CalcPart (solution,j,i,l );
            }
            int min = diff[0];
            int idx = start;
            for (int j =1; j<end; j ++)
            {
                if (diff[j]<min)
                {
                    min = diff[j];
                    idx = j+start;
                }
            }
            solution[i] = 1;
            solution[idx] = 0;

        }
    }
    //for (int i =0; i<l; i++)
    //{
    //    cout << solution[i];
    //}
    //cout << endl;



    for (int i =0; i<l; i++)
    {
        if ( solution[i]==1)
        {
              newModel= newModel + model.SelectResRange(i,i).CreateRigid();
        }
    }
    //cout << newModel.PrintPDB()<< endl;
    RenumberModel (newModel);


    return newModel;
    }
}

int DNA::CalcPart (int solution[],int pos0, int pos1, int l )const
{
    int alt[l];
    for (int j =0; j<l; j++)
    {
        alt[j] = solution[j];
    }
    alt [pos1] = 1;
    alt [pos0] = 0;


    int firstAlt = 0;
    int secondAlt = -1;

    for(int j =0; j<l; j++)
    {
       if (alt[j] == 1 && secondAlt == -1)
       {
           firstAlt ++;
       }
       if (alt[j] ==0 && firstAlt != 0)
       {
           secondAlt = 0;
       }
       if (alt[j] == 1 && secondAlt != -1)
       {
           secondAlt +=1;
       }
    }
    return abs(firstAlt-secondAlt);
}

bool DNA::IsAlign(std::string s1,std::string s2,int shift)const
{
    return (s1.compare(shift,s1.length(), s2, 0,s2.length()-shift)==0);
}

Rigidbody DNA::GetModelOfBasePair( Rigidbody& model,int posA,int posB)
{
        return (model.SelectResRange(posA, posA)|model.SelectResRange(posB, posB)).CreateRigid();


}


void DNA::AssembleSeq (const std::string &dataBaseFile, const std::string& seq)
{
      Rigidbody dataBase = Rigidbody(dataBaseFile);
      string chainIDs = GetChainIDs(dataBase);

      //"map" for the rigidbody, an iD corespond to its rigidbody
      vector<Rigidbody> vbase = BuildVbase(chainIDs,dataBase);
      //build the strand from the seq
      BuildStrand(seq, chainIDs, vbase);
      //make sure that every BasePaire have a different id
      ChangeFormat();
}

string DNA::GetSeq (  Rigidbody& model)
{
    string seq;
    unsigned int strandSize;
    if ((model.SelectAtomType("C1'").Size()/2) >0)
    {
        strandSize = model.SelectAtomType("C1'").Size()/2;
    }else if ((model.SelectAtomType("C1*").Size()/2) >0)
    {
        strandSize = model.SelectAtomType("C1*").Size()/2;
    }else if ((model.SelectAtomType("GS1").Size()/2) >0)
    {
        strandSize = model.SelectAtomType("GS1").Size()/2;
    }else {return "";}
    for ( unsigned int i=0 ; i< strandSize ; i++ )
    {
         string type = model.SelectResRange( i, i)[0].residType;
         // /!\ the order of the check is important! somme pdb use a CYT description for C, a wrong order could detect this as a T
         if      ( type.find ('G') != string::npos || type.find ('g') != string::npos) seq+='G';
         else if ( type.find ('C') != string::npos || type.find ('c') != string::npos) seq+='C';
         else if ( type.find ('A') != string::npos || type.find ('a') != string::npos) seq+='A';
         else if ( type.find ('T') != string::npos || type.find ('t') != string::npos) seq+='T';

    }
    return seq;
}


vector<Rigidbody> DNA::BuildVbase(string chainIDs, Rigidbody& dataBase)const
{
  vector<Rigidbody> vbase;
  unsigned int chainIDsSize = chainIDs.size();
  for (unsigned int i = 0; i < chainIDsSize ; i++)
  {

    vbase.push_back(dataBase.SelectChainId(chainIDs.substr(i,1)).CreateRigid());
  }
  return vbase;
}


string DNA::GetChainIDs(const Rigidbody& rb)const
{
  string chainIDs;
  AtomSelection selection = rb.SelectAllAtoms ();
  string tmp = "";
  unsigned int selectionSize = selection.Size();

  for (unsigned int i=0; i < selectionSize ;i++)
  {
    string id = selection[i].chainId;
    if(id !=tmp)
    {
      tmp=id;
      chainIDs += id;
    }
  }
  return chainIDs;
}

bool DNA::IsPdbFile (std::string seq) const
{
    return ( (seq.size() >=3) && ((seq.substr(seq.size()-3,seq.size())=="pdb") ||(seq.substr(seq.size()-3,seq.size())=="red")) );
}

void DNA::BuildStrand(std::string seq, std::string chainIDs, const std::vector<Rigidbody>& vbase)
{
    unsigned int seqSize = seq.size();
    unsigned int chainIDsSize = chainIDs.size();

    for (unsigned int i =0; i < seqSize; i++ )
    {
        for (unsigned int j =0; j < chainIDsSize; j++ )
        {
            if (seq[i] == chainIDs[j])
            {
                strand.push_back(BasePair(vbase[j]));
            }
        }
    }
}


void DNA::ChangeFormat()
{
  unsigned int nbAtom = 0;
  unsigned int strandSize  = strand.size();
  for (unsigned int i =0; i < strandSize; i++ )
  {
    //corect ID chain
    strand[i].SetChainID();
    //numerotation residu
    strand[i].SetResID(i,(strandSize + strandSize-1)-i);
    //numerotation atom (first part)
    nbAtom = strand[i].SetAtomNumberOfBase("A",nbAtom);

  }
  for (unsigned int i = strandSize-1; i > 0 ; i-- )
  {
    //numerotation atom (second part)
    nbAtom = strand[i].SetAtomNumberOfBase("B",nbAtom);
  }
  //last part of atom numerotation (because of error with decreasing unsigned int)
  strand[0].SetAtomNumberOfBase("B",nbAtom);
}


void DNA::ApplyInitialMov(const Movement& mov)
{
  unsigned int strandSize  = strand.size();
  for (unsigned int i=1; i <strandSize; i++)
  {
    strand[i].apply(strand[i-1].GetMovement());
    strand[i].apply(mov);
  }
}


unsigned int DNA::Size()const
{
  return strand.size();
}

unsigned int DNA::AtomSize() const
{
    uint tot=0;
    uint strandSize= this->Size();
    for (uint i=0; i<strandSize;i++)
    {
        tot+=strand[i].Size();
    }
    return tot;
}


string DNA::PrintPDB()
{
  string strandA, strandB;
  unsigned int strandSize  = strand.size();
  for ( unsigned int i =0; i < strandSize ; i++ )
  {
    strandA += strand[i].PrintPDBofBase("A") + "\n";
    strandB += strand[strandSize-1-i].PrintPDBofBase("B") + "\n";
  }
  string out= strandA + strandB;
  return out.substr(0,out.size()-1);
}

std::string DNA::PrintPDBofStrand( std::string chain )
{
  string out;
  unsigned int strandSize  = strand.size();
  for ( unsigned int i =0; i < strandSize ; i++ )
  {
    out += strand[i].PrintPDBofBase( chain );
  }
  return out.substr(0,out.size()-1);
}

string DNA::PrintParam()
{
  stringstream ss;
  unsigned int strandSize  = strand.size();
  for ( unsigned int i =1; i < strandSize ; i++ )
  {
    ss << "BasePair "<< i-1 <<"->"<<i<< " : "<<GetLocalParameter(i).ToFormatedString()+"\n";
  }
  return ss.str().substr(0,ss.str().size()-1);
}


void DNA::WritePDB(std::string fileName)
{
  ofstream myfile;
  myfile.open(fileName.c_str());
  myfile << PrintPDB();
  myfile.close();
}

Rigidbody DNA::CreateRigid()
{
  //we use the method createRigidOfStrand() to make sure that the rigidbody returned follow the established format
  Rigidbody chainA = CreateRigidOfStrand("A");
  Rigidbody chainB = CreateRigidOfStrand("B");

  //we add the atoms of the chain B to the chainA
  unsigned int chainBsize  = chainB.Size();
  for ( unsigned int i =0; i < chainBsize ; i++ )
  {
      chainA.AddAtom(chainB.CopyAtom(i));
  }
  return chainA;
}

Rigidbody DNA::CreateRigidOfStrand(std::string chain)
{
      Rigidbody dna;
  unsigned int strandSize  = strand.size();


  for ( unsigned int i =0; i < strandSize ; i++ )
  {
      Rigidbody basePair;
      if (chain == "B" || chain == "b")
      {
          basePair = strand[strandSize-1-i].GetRigidBodyOfBase(chain);
      }
      else
      {
          basePair = strand[i].GetRigidBodyOfBase(chain);
      }
      unsigned int basePairSize  = basePair.Size();
      for (unsigned int j=0; j <basePairSize ; j++)
      {
          Atom a =basePair.CopyAtom(j);
          dna.AddAtom(a);
      }
  }
  return dna;
}

void DNA::ChangeRepresentation(std::string dataBaseFile)
{
  Rigidbody dataBase = Rigidbody(dataBaseFile);
  string chainIDs = GetChainIDs(dataBase);

  //"map" for the rigidbody, an iD corespond to its rigidbody
  vector<Rigidbody> vbase = BuildVbase(chainIDs,dataBase);

    unsigned int chainIDsSize = chainIDs.size();

  unsigned int strandSize  = strand.size();
  for (unsigned int i = 0; i < strandSize ; i++)
  {
    Movement mov = Movement(strand[i].GetMatrix());

    for (unsigned int j =0; j < chainIDsSize; j++ )
    {
      if ( strand[i].GetType()[0] == chainIDs[j])
      {
	strand[i]=BasePair(vbase[j]);
	strand[i].apply(mov);
      }
    }
  }

  ChangeFormat();
}


Matrix DNA::GetLocalMatrix(int pos)const
{
   if (pos == 0) return strand[0].GetMatrix();

   Matrix mtot = strand[pos].GetMatrix();
   Matrix prec = inverseMatrix44(strand[pos-1].GetMatrix());

   return matrixMultiply( prec, mtot );

}

Parameter DNA::GetLocalParameter(int pos)
{
  Parameter param =Parameter();
  Rigidbody firstAxis = strand[pos-1].GetRigidBody();
  Rigidbody secondAxis = strand[pos].GetRigidBody();
  param.MeasureParameters(param.BuildAxisCentered(firstAxis),param.BuildAxisCentered(secondAxis));
  return param;

}

void DNA::ApplylocalMov(const Movement& mov,int pos)
{
  Matrix nextlocal = GetLocalMatrix(pos+1);
  strand[pos].apply(mov);

  unsigned int strandSize  = strand.size();
  for (unsigned int i=pos+1; i <strandSize; i++)
  {
    nextlocal = Reconstruct(i,nextlocal);
  }
}


void DNA::ApplyglobalMov(const Movement& mov)
{
  Matrix nextlocal;
  unsigned int strandSize  = strand.size();
  if (strandSize>1){
    nextlocal = GetLocalMatrix(1);
  }
  strand[0].apply(mov);

  for (unsigned int i=1; i <strandSize; i++)
  {
    nextlocal = Reconstruct(i,nextlocal);
    strand[i].apply(mov);
  }

}


void DNA::ApplyLocal(const Movement& mov,int posMov, int posAnchor)
{
  BasePair anchor = strand[posAnchor];
  ApplylocalMov(mov,posMov);
  Relocate(anchor,posAnchor);
}


void DNA::ApplyLocal(const Matrix&  m,int posMov, int posAnchor)
{
  ApplyLocal ( Movement(m), posMov, posAnchor);
}


void DNA::ApplyGlobal(const Movement& mov ,int posAnchor)
{
  BasePair anchor = strand[posAnchor];
  ApplyglobalMov(mov);
  Relocate(anchor,posAnchor);
}


void DNA::ApplyGlobal(const Matrix& m ,int posAnchor)
{
  ApplyLocal ( Movement(m), posAnchor);
}


void DNA::apply(const Movement& mov)
{
    DNA::apply(mov.GetMatrix());
}


void DNA::apply(const Matrix& m)
{
  unsigned int strandSize  = strand.size();
  for (unsigned int i=0; i <strandSize; i++)
  {
    Rigidbody rb = strand[i].GetRigidBody();
    rb.apply_matrix(m);
    strand[i].SetRigidBody(rb);
  }
}


double DNA::Rmsd(const DNA& model)const
{

    double aSize=AtomSize();
    if (model.AtomSize() != aSize)
    {
        std::cerr << "Error: trying to superpose two DNA of different sizes" << std::endl ;
        throw std::invalid_argument("RmsdSizesDiffers");
    }

    double total = 0.0;
    uint strandSize = Size();
    for (uint i = 0; i<strandSize;i++){
        uint pbSize= strand[i].Size();
        for (uint j =0; j<pbSize;j++)
        {
            Atom atom1=model[i][j];
            Atom atom2=strand[i][j];

            total+=Dist2(atom1,atom2);
        }
    }
    return sqrt(total/(dbl) aSize) ;

}

void DNA::ChangeBasePair(const BasePair& bp, int pos)
{
    strand[pos]=bp;
}

void DNA::Relocate(const BasePair& anchor,int posAnchor)
{
  apply(superpose(anchor.GetRigidBody(),strand[posAnchor].GetRigidBody(),0).matrix);
}


Matrix DNA::Reconstruct(int pos, const Matrix& local)
{
  Matrix nextlocal;
  if ((unsigned int)pos<strand.size()) nextlocal = GetLocalMatrix(pos+1);

  Matrix prec = strand[pos-1].GetMatrix();

  strand[pos].apply(inverseMatrix44(strand[pos].GetMatrix()));//erasing the old matrix

  strand[pos].apply(prec);
  strand[pos].apply(local);

  return nextlocal;
}


void DNA::Add(const DNA & d, const Movement & mov)
{
    this->Add(d[0], mov);
    for(uint i =1; i< d.Size();i++)
    {
        this->Add(d[i],Movement(d.GetLocalMatrix(i)));
    }
}

/// add a basepair at the end of the strand of this DNA
void DNA::Add(BasePair bp, const Movement & mov)
{
    Matrix oldmouvement = bp.GetMatrix ();
    bp.apply(inverseMatrix44 (oldmouvement));
    if (strand.size()>0)
    {
        bp.apply(matrixMultiply(strand[strand.size()-1].GetMatrix(),mov.GetMatrix()));
    }
    else bp.apply(mov.GetMatrix());
    strand.push_back(bp);
    this->ChangeFormat();
}

DNA DNA::SubDNA(uint start, uint end)const
{
    if (std::max(start, end) > this->Size() )
    {
        throw std::out_of_range("out of range in SubDNA");
    }
    DNA newdna = DNA();

    newdna.Add(strand[start],Movement(strand[start].GetMatrix()));
    for (uint i=start+1; i<end ;i++)
    {
        newdna.Add(strand[i],Movement(this->GetLocalMatrix(i)));
    }
    return newdna;
}

void DNA::Replace(const DNA & d,int start)
{
    DNA preDNA = this->SubDNA(0,start);
    DNA postDNA =this->SubDNA(start+d.Size(),this->Size());

    Movement initMov = Movement(strand[0].GetMatrix());
    strand.clear();


    this->Add(preDNA,initMov);
    this->Add(d);
    this->Add(postDNA);


}

void DNA::ChangeType(int pos, std::string type, std::string filename) {
    Rigidbody dataBase = Rigidbody(filename);
    Movement mov = Movement(strand[pos].GetMatrix());

    strand[pos] = BasePair(dataBase.SelectChainId(type).CreateRigid());
    strand[pos].apply(mov);

    ChangeFormat();
}

void DNA::Translate(Coord3D coord)
{
  unsigned int strandSize  = strand.size();
  for (unsigned int i=0; i <strandSize; i++)
  {
    Rigidbody rb = strand[i].GetRigidBody();
    rb.Translate(coord);
    strand[i].SetRigidBody(rb);
  }

}
