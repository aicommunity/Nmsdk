/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2011.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NSIMPLE_STATISTIC_CPP
#define NSIMPLE_STATISTIC_CPP

#include <iomanip>
#include "NSimpleStatistic.h"

namespace NMSDK {

// --------------------------
// ������������ � �����������
// --------------------------
NSimpleStatistic::NSimpleStatistic(void)
{
 StatsFile=0;
 StatsNumber=0;
 Mode=0;
}

NSimpleStatistic::~NSimpleStatistic(void)
{
 if(StatsFile)
  delete StatsFile;
 StatsFile=0;
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NSimpleStatistic* NSimpleStatistic::New(void)
{
 return new NSimpleStatistic;
}
// --------------------------


// --------------------------
// Computation methods
// --------------------------
// ��������� ����� ����, �������� ����������
bool NSimpleStatistic::ReCreateFile(void)
{
// return true;// �������� !!!
 if(StatsFile)
 {
  StatsFile->close();
  delete StatsFile;
  StatsFile=0;
 }
 StatsFile=new fstream((GetName()+string("_")+RDK::sntoa(StatsNumber++,5)+".txt").c_str(), ios::out | ios::trunc);
 if(!StatsFile || !(*StatsFile))
  return false;

 // ����� ���������
 if(Mode == 0)
 {
  (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<"Time"<<"\t";
  for(size_t i=0;i<Headers.size();i++)
   (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<Headers[i]<<"\t";
  (*StatsFile)<<endl;
 }
 else
 if(Mode == 1)
 {
  (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<"Time"<<"\t";
  for(size_t i=0;i<Headers.size();i++)
   (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<Headers[i]<<"\t";
  (*StatsFile)<<endl;
 }
 else
 if(Mode == 2)
 {
  (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<"Time"<<"\t";
  for(size_t i=0;i<Headers.size();i++)
   (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<Headers[i]<<"\t";
  (*StatsFile)<<endl;
 }

 return true;
}
// --------------------------

// --------------------------
// Computation methods
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NSimpleStatistic::ADefault(void)
{
 StatsInterval=1;

 return true;
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NSimpleStatistic::ABuild(void)
{
 return true;
}

// Reset computation
bool NSimpleStatistic::AReset(void)
{
 ClearStats();
 StatsStartTime=NAContainer::GetDoubleTime();
 return true;
}

// Execute math. computations of current object on current step
bool NSimpleStatistic::ACalculate(void)
{
// return true; // �������� !!
 if(!StatsFile)
  if(!ReCreateFile())
   return false;

 if(Mode == 0)
 {
  // ���������, �������� ��� ��� ���� ��������� ����������
  if(NAContainer::GetDoubleTime()-StatsStartTime>=StatsInterval)
  {
   (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<NAContainer::GetDoubleTime()<<"\t";
   for(size_t i=0;i<StatsMin.size();i++)
   {
	for(size_t j=0;j<StatsMin[i].size();j++)
	{
	 (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<StatsMin[i][j]<<"\t"<<StatsMax[i][j]<<"\t"<<StatsAvg[i][j]<<"\t"<<StatsDelta[i][j]<<"\t";
	}
   }
   (*StatsFile)<<endl;

   ClearStats();
   StatsStartTime=NAContainer::GetDoubleTime();
  }

  ResizeStats();
  for(int i=0;i<GetNumInputs();i++)
  {
   for(size_t j=0;j<GetInputDataSize(i);j++)
   {
	if(StatsMin[i][j]>GetInputData(i)->Double[j])
	 StatsMin[i][j]=GetInputData(i)->Double[j];
	if(StatsMax[i][j]<GetInputData(i)->Double[j])
	 StatsMax[i][j]=GetInputData(i)->Double[j];

	StatsAvg[i][j]=(StatsMax[i][j]+StatsMin[i][j])/2;
	StatsDelta[i][j]=(StatsMax[i][j]-StatsMin[i][j]);
   }
  }
 }
 else
 if(Mode == 1)
 {
  if(NAContainer::GetDoubleTime()-StatsStartTime>=StatsInterval)
  {
   (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<NAContainer::GetDoubleTime()<<endl;
   for(int i=0;i<GetNumInputs();i++)
   {
	for(size_t j=0;j<GetInputDataSize(i);j++)
	{
	 (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<GetInputData(i)->Double[j]<<"\t";
	}
	(*StatsFile)<<endl;
   }
   (*StatsFile)<<endl;

   ClearStats();
   StatsStartTime=NAContainer::GetDoubleTime();
  }
 }
 else
 if(Mode == 2)
 {
  // ���������, �������� ��� ��� ���� ��������� ����������
  if(NAContainer::GetDoubleTime()-StatsStartTime>=StatsInterval)
  {
   (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<NAContainer::GetDoubleTime()<<"\t";
   for(int i=0;i<GetNumInputs();i++)
   {
	for(size_t j=0;j<GetInputDataSize(i);j++)
	{
	 (*StatsFile)<<showpoint<<internal<<fixed<<setfill(' ')<<right<<setprecision(8)<<setw(10)<<GetInputData(i)->Double[j]<<"\t";
	}
   }
   (*StatsFile)<<endl;

   ClearStats();
   StatsStartTime=NAContainer::GetDoubleTime();
  }
 }

 return true;
}
// --------------------------


// --------------------------
// ��������������� ������ ����� ����������
// --------------------------
// ���������� ������� ����������
void NSimpleStatistic::ClearStats(void)
{
 // ������ ������� ����������
 StatsMin.clear();

 StatsMax.clear();

 StatsAvg.clear();

 StatsDelta.clear();
}

// ������ ������� �������� ������ ������� ����������
void NSimpleStatistic::ResizeStats(void)
{
 StatsMin.resize(NumInputs);
 StatsMax.resize(NumInputs);
 StatsAvg.resize(NumInputs);
 StatsDelta.resize(NumInputs);
 for(int i=0;i<GetNumInputs();i++)
 {
  StatsMin[i].resize(GetInputDataSize(i));
  StatsMax[i].resize(GetInputDataSize(i));
  StatsAvg[i].resize(GetInputDataSize(i));
  StatsDelta[i].resize(GetInputDataSize(i));
 }
}
// --------------------------

}

#endif
