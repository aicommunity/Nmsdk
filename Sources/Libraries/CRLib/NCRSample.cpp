// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:        http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NCR_SAMPLE_CPP
#define NCR_SAMPLE_CPP

#include "NCRSample.h"

namespace NMSDK {
//---------------------------------------------------------------------------
// --------------------------
// ������������ � �����������
// --------------------------
NCRSample::NCRSample(void)
// : NADItem(name),
// SampleData("SampleData",this),
: VectorSize("VectorSize",this,&NCRSample::SetVectorSize),
 SampleSize("SampleSize",this,&NCRSample::SetSampleSize),
 Mode("Mode",this),
 CurrentSample("CurrentSample",this,&NCRSample::SetCurrentSample)
{
}

NCRSample::~NCRSample(void)
{
}
// --------------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������� ������� �������
bool NCRSample::SetCurrentSample(int value)
{
 if(value<-1 || size_t(value) >= SampleSize)
  return false;

 return true;
}

// ��������� ������� �������
bool NCRSample::SetSampleSize(size_t value)
{
 if(value < SampleSize)
 {
  SampleData.resize(value);
  return true;
 }

 return false;
}

// ��������� ������� ������� �������
bool NCRSample::SetVectorSize(size_t value)
{
 SetOutputDataSize(0,value);
 return true;
}
// --------------------------

// --------------------------
// ������ ���������� ��������
// --------------------------
// ��������� ������� ������� �������� ������
bool NCRSample::Add(int class_index)
{
 if(!NumInputs)
  return false;

 ++SampleSize.v;
 SampleData.resize(SampleSize);

 SampleData[SampleSize-1].first.Resize(0);
 for(size_t i=0;i<NumInputs;i++)
 {
  if(PInputDataSize[i]<=0)
   continue;
  SampleData[SampleSize-1].first+=*PInputData[i];
 }

 if(SampleData[SampleSize-1].first.GetSize() != VectorSize)
 {
  --SampleSize.v;
  SampleData.resize(SampleSize);
  return false;
 }

 SampleData[SampleSize-1].second=class_index;
 return true;
}

// ������� �������� ������� ������� ������ �� �������
bool NCRSample::Del(size_t index)
{
 return true;
}

// ������� �������
void NCRSample::Clear(void)
{
 SampleSize=0;
 SampleData.resize(SampleSize);
}

// ���������� ������ ������ �������� ������� ��������� �������
int NCRSample::GetCurrentClassIndex(void) const
{
 if(CurrentSample.v<0 || size_t(CurrentSample.v)>=SampleSize)
  return -1;

 return SampleData[CurrentSample].second;
}

// ���������� ������ ��������� �������
const vector<pair<RDK::UItemData,int> >& NCRSample::GetSampleData(void) const
{
 return SampleData;
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NAContainer* NCRSample::New(void)
{
 return new NCRSample;
}
// --------------------------


// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NCRSample::ADefault(void)
{
 SetNumOutputs(1);
 SampleSize=1;
 VectorSize=1;
 Mode=0;

 return true;
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NCRSample::ABuild(void)
{

 return true;
}

// ����� �������� �����
bool NCRSample::AReset(void)
{
 CurrentSample=-1;

 return true;
}

// ��������� ������ ����� ������� �� ������� ����
bool NCRSample::ACalculate(void)
{
 size_t k=0;
 switch(Mode)
 {
 case 0:
  if(!NumInputs)
   return false;

  for(size_t i=0;i<NumInputs;i++)
  {
   for(size_t j=0;j<PInputDataSize[i];j++,k++)
	POutputData[0].Double[k]=PInputData[i]->Double[j];
  }
 break;

 case 1:
  ++CurrentSample.v;
  if(CurrentSample>=int(SampleSize.v))
   CurrentSample=0;

  SetOutputDataSize(0,VectorSize.v);
  const RDK::UItemData &data=SampleData[CurrentSample].first;

  for(size_t i=0;i<VectorSize.v;i++)
   POutputData[0].Double[i]=data.Double[i];
 break;
 }
 return true;
}
// --------------------------

//---------------------------------------------------------------------------
}
#endif