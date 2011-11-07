// ===========================================================
// Version:        3.0.4
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:		alexab@ailab.ru
url:        http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NCRFUSION_CPP
#define NCRFUSION_CPP

#include "NCRFusion.h"
#include <algorithm>
#include <fstream>
//#include "CRFeatureSelectorCorrelation.h"


namespace NMSDK {

using namespace std;

// ������� ������� ����������
unsigned int fact(unsigned int n)
{
 unsigned int res=1;

 for(unsigned int i=2;i<=n;i++)
  res*=i;

 return res;
}

// --------------------------
// ������������ � �����������
// --------------------------
NCRFusion::NCRFusion(void)
//: NACRClassifier(name),
 : FusionMode("FusionMode",this,&NCRFusion::SetFusionMode),
  NumAttempts("NumAttempts",this),
  AccumulateMode("AccumulateMode",this),
  PreResultsWeigths("PreResultsWeigths",this)
{
}

NCRFusion::~NCRFusion(void)
{
}
// --------------------------

// -----------------------------
// ������ ���������� �������������� ����������
// -----------------------------
bool NCRFusion::SetFusionMode(int value)
{
// if(value == 0 || value == 1)
//  return true;
 return true;
}
// -----------------------------

// -----------------------------
// ������ ���������� �����������
// -----------------------------
// -----------------------------

// -----------------------------
// ������ ������� � ������ ������
// -----------------------------
// ������� �������� ����������
int NCRFusion::GetCurrentAttempt(void) const
{
 return CurrentAttempt;
}
// -----------------------------

// ------------------------
// ������ �����
// ------------------------
// ��������� ��������� �� �����
bool NCRFusion::AFileLoad(fstream &file)
{
 return true;
}

// ��������� ��������� � ����
bool NCRFusion::AFileSave(fstream &file)
{
 return true;
}
// ------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NAContainer* NCRFusion::New(void)
{
 return new NCRFusion;
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NCRFusion::ACRDefault(void)
{
 SetOutputDataSize(0,2);
 SetNumInputs(100);

 Real minrate,maxrate;
 minrate.assign(GetOutputDataSize(0),0);
 maxrate.assign(GetOutputDataSize(0),100);

 MinQualityRate=minrate;
 MaxQualityRate=maxrate;

 AutoQualityRate=true;

 MaxInputValue=100;
 MinInputValue=0;
 MinOutputValue=0;
 MaxOutputValue=100;

 FusionMode=2;
 NumAttempts=10;
 AccumulateMode=3;

 return true;
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NCRFusion::ACRBuild(void)
{
 return true;
}


// ����� �������� �����.
bool NCRFusion::ACRReset(void)
{
 AccumOutput.resize(0);
 CurrentAttempt=-1;

 return true;
}

bool NCRFusion::ACRCalculate(void)
{
 switch(FusionMode)
 {
 case 0:
  if(!AverageQualityCalculate())
   return false;
 break;

 case 1:
  if(!PairCalculate())
   return false;
 break;

 case 2:
  if(!AverageInputCalculate())
   return false;
 break;

 case 3:
  if(!RecognitionCounterCalculate())
   return false;
 break;

 case 4:
  if(!SumInputCalculate())
   return false;
 break;

 case 5:
  if(!InputRecognitionCounterCalculate())
   return false;
 break;

 case 6:
  if(!SumInputRecognitionCounterCalculate())
   return false;
 break;

 default:
  return false;
 }

 if(NumAttempts == 1)
  return true;

 size_t size=GetOutputDataSize(0);

 bool key=false;
 for(size_t j=0;j<size;j++)
  if(POutputData[0].Double[j])
   key=true;

 if(key)
 {
  AccumOutput.push_back(POutputData[0]);
  ++CurrentAttempt;
  if(AccumOutput.size()>static_cast<size_t>(NumAttempts) && NumAttempts != 0)
  {
   AccumOutput.erase(AccumOutput.begin());
   --CurrentAttempt;
  }
 }

 int maxindex;
 real maxresult;
 vector<int> maxcounter;

 for(size_t j=0;j<size;j++)
  POutputData[0].Double[j]=0;

 int accumsize=AccumOutput.size();
 switch(AccumulateMode)
 {
 case 1:
   for(size_t i=0;i<AccumOutput.size();i++)
   {
	for(size_t j=0;j<size;j++)
	 POutputData[0].Double[j]+=AccumOutput[i].Double[j];
   }

   if(accumsize)
	for(size_t j=0;j<size;j++)
	 POutputData[0].Double[j]/=accumsize;
 break;

 case 2:
  for(size_t i=0;i<AccumOutput.size();i++)
  {
   maxindex=-1;
   maxresult=0;
   maxcounter.assign(size,0);
   for(size_t j=0;j<size;j++)
	if(AccumOutput[i].Double[j]>maxresult)
	{
	 maxindex=j;
	 maxresult=AccumOutput[i].Double[j];
	}

   if(maxindex>=0 && maxresult>0)
   {
	POutputData[0].Double[maxindex]+=maxresult;
	++maxcounter[maxindex];
   }
  }

  for(size_t j=0;j<size;j++)
   if(maxcounter[j])
	POutputData[0].Double[j]/=maxcounter[j];
 break;

 case 3:
  for(size_t i=0;i<AccumOutput.size();i++)
  {
   maxindex=-1;
   maxresult=0;
   maxcounter.assign(size,0);
   for(size_t j=0;j<size;j++)
	if(AccumOutput[i].Double[j]>maxresult)
	{
	 maxindex=j;
	 maxresult=AccumOutput[i].Double[j];
	}

   if(maxindex>=0 && maxresult>0)
   {
	POutputData[0].Double[maxindex]+=1;
	++maxcounter[maxindex];
   }
  }

/*  for(size_t j=0;j<size;j++)
   if(maxcounter[j])
	POutputData[0].Double[j]/=maxcounter[j];
	*/
 break;
 }


 return true;
}
// --------------------------


// --------------------------
// ������� ������ �������� ����
// --------------------------
// ����� �������� �������� � �������� ���������
void NCRFusion::AResetTraining(void)
{
}

// ����������� �������� �� �������� �������
real NCRFusion::ATrain(size_t exp_class)
{
 real E=0;

 return E;
}
// --------------------------


// ------------------------
// ������� ������ �����
// ------------------------
// ���������� ���������� ��� �������� �� ���������� ��������
bool NCRFusion::AverageQualityCalculate(void)
{
 vector<NACRClassifier*> classifiers;

 for(size_t i=0;i<NumInputs;i++)
 {
  if(dynamic_cast<NACRClassifier*>(GetCItem(i).Item))
   classifiers.push_back(static_cast<NACRClassifier*>(GetCItem(i).Item));
 }

 if(classifiers.size()==0)
  return true;

 size_t minoutputsize=classifiers[0]->GetOutputDataSize(0);

 for(size_t i=1;i<classifiers.size();i++)
 {
  if(minoutputsize<classifiers[0]->GetOutputDataSize(0))
   minoutputsize=classifiers[0]->GetOutputDataSize(0);
 }

 // ������ ����� ��������� �� ������������ �����
 vector<real> classcounter;

 // ������ ���������� ���������� ��������
 vector<real> classquality;

 classcounter.assign(minoutputsize,0);
 classquality.assign(minoutputsize,0);

 for(size_t i=0;i<classifiers.size();i++)
 {
  if(classifiers[i]->QualityRate->second >= int(minoutputsize) ||
	 !classifiers[i]->GetActivity())
   continue;
  classcounter[classifiers[i]->QualityRate->second]+=1;

  classquality[classifiers[i]->QualityRate->second]+=classifiers[i]->QualityRate->first;
 }

 for(size_t i=0;i<classquality.size();i++)
  if(classcounter[i])
   classquality[i]/=classcounter[i];

real maxcounter=0;

 for(size_t i=0;i<classcounter.size();i++)
  if(maxcounter<classcounter[i])
  {
   maxcounter=classcounter[i];
  }

 SetOutputDataSize(0,minoutputsize);
 for(size_t i=0;i<classcounter.size();i++)
  POutputData[0].Double[i]=classquality[i];

 return true;
}

// ���������� ���������� ��� �������� �� ������
bool NCRFusion::AverageInputCalculate(void)
{
 vector<NACRClassifier*> classifiers;

 for(size_t i=0;i<NumInputs;i++)
 {
  if(dynamic_cast<NACRClassifier*>(GetCItem(i).Item))
   classifiers.push_back(static_cast<NACRClassifier*>(GetCItem(i).Item));
 }

 if(classifiers.size()==0)
  return true;

 size_t minoutputsize=classifiers[0]->GetOutputDataSize(0);

 for(size_t i=1;i<classifiers.size();i++)
 {
  if(minoutputsize<classifiers[0]->GetOutputDataSize(0))
   minoutputsize=classifiers[0]->GetOutputDataSize(0);
 }

 // ������ ����� ��������� �� ������������ �����
 vector<real> classcounter;

 // ������ ���������� ���������� ��������
 vector<real> classquality;

 classcounter.assign(minoutputsize,0);
 classquality.assign(minoutputsize,0);

 for(size_t i=0;i<classifiers.size();i++)
 {
  for(size_t j=0;j<minoutputsize;j++)
  {
   if(!classifiers[i]->GetActivity())
	continue;

   ++classcounter[j];
   classquality[j]+=classifiers[i]->GetOutputData(0).Double[j];
  }
 }

 for(size_t i=0;i<classquality.size();i++)
  if(classcounter[i])
   classquality[i]/=classcounter[i];

 real maxcounter=0;

 for(size_t i=0;i<classquality.size();i++)
  if(maxcounter<classquality[i])
  {
   maxcounter=classquality[i];
  }

 SetOutputDataSize(0,minoutputsize);

 for(size_t i=0;i<classcounter.size();i++)
  POutputData[0].Double[i]=classquality[i];

 return true;
}

// ���������� ���������� ��� ����� �� ������
bool NCRFusion::SumInputCalculate(void)
{
 vector<NACRClassifier*> classifiers;

 for(size_t i=0;i<NumInputs;i++)
 {
  if(dynamic_cast<NACRClassifier*>(GetCItem(i).Item))
   classifiers.push_back(static_cast<NACRClassifier*>(GetCItem(i).Item));
 }

 if(classifiers.size()==0)
  return true;

 size_t minoutputsize=classifiers[0]->GetOutputDataSize(0);

 for(size_t i=1;i<classifiers.size();i++)
 {
  if(minoutputsize<classifiers[0]->GetOutputDataSize(0))
   minoutputsize=classifiers[0]->GetOutputDataSize(0);
 }

 // ������ ���������� ���������� ��������
 vector<real> classquality;

 classquality.assign(minoutputsize,0);

 for(size_t i=0;i<classifiers.size();i++)
 {
  if(!classifiers[i]->GetActivity())
   continue;

  for(size_t j=0;j<minoutputsize;j++)
   classquality[j]+=classifiers[i]->GetOutputData(0).Double[j];
 }

 SetOutputDataSize(0,minoutputsize);

 for(size_t i=0;i<classquality.size();i++)
  POutputData[0].Double[i]=classquality[i];

 return true;
}


// ���������� ���������� ����� �������� ���������
bool NCRFusion::PairCalculate(void)
{
/* int classindex;
 int classindex2;
 real maxresult=-1,maxresult2=-1;

 real mininput,maxinput;

 vector<NACRClassifier*> classifiers;
 vector<CRFeatureSelectorCorr*> attributemodules;

 for(size_t i=0;i<NumInputs;i++)
 {
  if(dynamic_cast<NACRClassifier*>(GetCItem(i).Item))
   classifiers.push_back(static_cast<NACRClassifier*>(GetCItem(i).Item));
 }

 if(classifiers.size()==0)
  return true;

 attributemodules.resize(classifiers.size());
 for(size_t i=1;i<classifiers.size();i++)
 {
  attributemodules[i]=dynamic_cast<CRFeatureSelectorCorr*>(classifiers[i]->GetCItem(0).Item);
 }


 int minoutputsize=classifiers[0]->GetOutputDataSize(0);

 for(size_t i=1;i<classifiers.size();i++)
 {
  if(minoutputsize<classifiers[0]->GetOutputDataSize(0))
   minoutputsize=classifiers[0]->GetOutputDataSize(0);
 }

 // ������ ����� ��������� �� ������������ �����
 vector<real> classcounter;

 // ������ ���������� ���������� ��������
 vector<real> classquality;

 // ������ ����������� ��������������� �������� �������������
 vector<NCRFPreResult> preresults;

 // ����� ��������� ��������������� ������������� (����� ���������)
 int numpreresults=fact(minoutputsize)/(fact(2)*fact(minoutputsize-2));

 preresults.resize(numpreresults);

 PreResultsWeigths->resize(classifiers.size());

 for(size_t k=0;k<PreResultsWeigths->size();k++)
 {
//  PreResultsWeigths[i].assign(numpreresults,1);
  PreResultsWeigths[k].resize(numpreresults);
  if(attributemodules[k])
  {
   int n=0;
   for(size_t j=0;j<minoutputsize;j++)
	for(size_t i=j+1;i<minoutputsize;i++)
	{
	 PreResultsWeigths[k][n]=(1.0-attributemodules[k]->GetTrainCorrTable()[j][0][i][0]);
	 ++n;
	}
  }
 }



 classcounter.assign(minoutputsize,0);
 classquality.assign(minoutputsize,0);

 int n=0;
 for(size_t j=0;j<minoutputsize;j++)
  for(size_t i=j+1;i<minoutputsize;i++)
  {
   preresults[n].Ix1=j;
   preresults[n].Ix2=i;
   for(size_t k=0;k<classifiers.size();k++)
   {
	if(classifiers[i]->QualityRate->second >= minoutputsize ||
	 !classifiers[i]->Activity)
	 continue;

	preresults[n].Res1+=classifiers[k]->GetOutputData(0).Double[j]*PreResultsWeigths[k][n];
	preresults[n].Res2+=classifiers[k]->GetOutputData(0).Double[i]*PreResultsWeigths[k][n];
   }
   ++n;
  }

 for(size_t n=0;n<numpreresults;n++)
 {
 // if(classquality[preresults[n].Ix1]<preresults[n].Res1)
   classquality[preresults[n].Ix1]+=preresults[n].Res1;
 // if(classquality[preresults[n].Ix2]<preresults[n].Res2)
   classquality[preresults[n].Ix2]+=preresults[n].Res2;
 }

 SetOutputDataSize(0,minoutputsize);

 for(size_t i=0;i<classcounter.size();i++)
  POutputData[0].Double[i]=classquality[i];
              */
 return true;
}

// ���������� ���������� �� ����� ����������� ������
bool NCRFusion::RecognitionCounterCalculate(void)
{
 vector<NACRClassifier*> classifiers;

 for(size_t i=0;i<NumInputs;i++)
 {
  if(dynamic_cast<NACRClassifier*>(GetCItem(i).Item))
   classifiers.push_back(static_cast<NACRClassifier*>(GetCItem(i).Item));
 }

 if(classifiers.size()==0)
  return true;

 size_t minoutputsize=classifiers[0]->GetOutputDataSize(0);

 for(size_t i=1;i<classifiers.size();i++)
 {
  if(minoutputsize<classifiers[0]->GetOutputDataSize(0))
   minoutputsize=classifiers[0]->GetOutputDataSize(0);
 }

 // ������ ����� ��������� �� ������������ �����
 vector<real> classcounter;

 // ������ ���������� ���������� ��������
 vector<real> classquality;

 classcounter.assign(minoutputsize,0);
 classquality.assign(minoutputsize,0);

 for(size_t i=0;i<classifiers.size();i++)
 {
  if(classifiers[i]->QualityRate->second >= int(minoutputsize) ||
	 !classifiers[i]->GetActivity())
   continue;
  classcounter[classifiers[i]->QualityRate->second]+=1;

  classquality[classifiers[i]->QualityRate->second]+=1;//classifiers[i]->QualityRate->first;
 }

/* for(size_t i=0;i<classquality.size();i++)
  if(classcounter[i])
   classquality[i]/=classcounter[i];
  */
real maxcounter=0;

 for(size_t i=0;i<classcounter.size();i++)
  if(maxcounter<classcounter[i])
  {
   maxcounter=classcounter[i];
  }

 SetOutputDataSize(0,minoutputsize);
 for(size_t i=0;i<classcounter.size();i++)
  POutputData[0].Double[i]=classcounter[i];

 return true;
}

// ���������� ���������� �� ����� ����������� ������ �� ������
bool NCRFusion::InputRecognitionCounterCalculate(void)
{
 vector<NACRClassifier*> classifiers;

 for(size_t i=0;i<NumInputs;i++)
 {
  if(dynamic_cast<NACRClassifier*>(GetCItem(i).Item))
   classifiers.push_back(static_cast<NACRClassifier*>(GetCItem(i).Item));
 }

 if(classifiers.size()==0)
  return true;

 size_t minoutputsize=classifiers[0]->GetOutputDataSize(0);

 for(size_t i=1;i<classifiers.size();i++)
 {
  if(minoutputsize<classifiers[0]->GetOutputDataSize(0))
   minoutputsize=classifiers[0]->GetOutputDataSize(0);
 }

 // ������ ����� ��������� �� ������������ �����
 vector<real> classcounter;

 // ������ ���������� ���������� ��������
 vector<real> classquality;

 classcounter.assign(minoutputsize,0);
 classquality.assign(minoutputsize,0);

 real maxout;
 int maxindex;

 for(size_t i=0;i<classifiers.size();i++)
 {
  if(!classifiers[i]->GetActivity())
   continue;

  maxout=0;
  maxindex=0;
  for(size_t j=0;j<minoutputsize;j++)
  {
   if(maxout<classifiers[i]->GetOutputData(0).Double[j])
   {
	maxout=classifiers[i]->GetOutputData(0).Double[j];
	maxindex=j;
   }
  }

  if(maxout>0)
  {
   classcounter[maxindex]+=1;

   classquality[maxindex]+=1;//classifiers[i]->QualityRate->first;
  }
 }

 SetOutputDataSize(0,minoutputsize);
 for(size_t i=0;i<classcounter.size();i++)
  POutputData[0].Double[i]=classcounter[i];

 return true;
}

// ���������� ���������� �� ����� ������-�����������
bool NCRFusion::SumInputRecognitionCounterCalculate(void)
{
 vector<NACRClassifier*> classifiers;

 for(size_t i=0;i<NumInputs;i++)
 {
  if(dynamic_cast<NACRClassifier*>(GetCItem(i).Item))
   classifiers.push_back(static_cast<NACRClassifier*>(GetCItem(i).Item));
 }

 if(classifiers.size()==0)
  return true;

 size_t minoutputsize=classifiers[0]->GetOutputDataSize(0);

 for(size_t i=1;i<classifiers.size();i++)
 {
  if(minoutputsize<classifiers[0]->GetOutputDataSize(0))
   minoutputsize=classifiers[0]->GetOutputDataSize(0);
 }

 // ������ ����� ��������� �� ������������ �����
 vector<real> classcounter;

 // ������ ���������� ���������� ��������
 vector<real> classquality;

 classcounter.assign(minoutputsize,0);
 classquality.assign(minoutputsize,0);

 real maxout;
 int maxindex;

 for(size_t i=0;i<classifiers.size();i++)
 {
  if(!classifiers[i]->GetActivity())
   continue;

  maxout=0;
  maxindex=0;
  for(size_t j=0;j<minoutputsize;j++)
  {
   if(maxout<classifiers[i]->GetOutputData(0).Double[j])
   {
	maxout=classifiers[i]->GetOutputData(0).Double[j];
	maxindex=j;
   }
  }

  if(maxout>0)
  {
   classcounter[maxindex]+=1;

   classquality[maxindex]+=maxout;
  }
 }

 SetOutputDataSize(0,minoutputsize);
 for(size_t i=0;i<classquality.size();i++)
  POutputData[0].Double[i]=classquality[i];

 return true;
}

// ������������� �������� �������� ������� ��� �������������
bool NCRFusion::SetInput(const Real &input)
{

 return true;
}
// ------------------------


}
//---------------------------------------------------------------------------
#endif
