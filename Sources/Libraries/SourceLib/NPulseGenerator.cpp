// ===========================================================
// Version:        3.0.2
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NPULSE_GENERATOR_CPP
#define NPULSE_GENERATOR_CPP

#include <cstdlib>
#include <cstdio>
#include "NPulseGenerator.h"
//#include "NPulseChannel.h"



namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NPulseGenerator::NPulseGenerator(void)
//: NSource(name),
 : Frequency("Frequency",this,&NPulseGenerator::SetFrequency),
  PulseLength("PulseLength",this,&NPulseGenerator::SetPulseLength),
  Amplitude("Amplitude",this,&NPulseGenerator::SetAmplitude),
  FrequencyDeviation("FrequencyDeviation",this,&NPulseGenerator::SetFrequencyDeviation),

  PulseCounter("PulseCounter",this),
  RandomFrequency("RandomFrequency",this)
{
}

NPulseGenerator::~NPulseGenerator(void)
{
}
// --------------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������� ������� ���������
bool NPulseGenerator::SetFrequency(real value)
{
 if(value <0)
  return false;

 return Reset();
// return true;
}

// ������������� ������������ ��������
bool NPulseGenerator::SetPulseLength(real value)
{
 if(value <= 0)
  return false;

 return true;
}

// ������������� ��������� ���������
bool NPulseGenerator::SetAmplitude(real value)
{
 return true;
}

// ������������� ���������� �������
// (������ ��������, �� �������� ����������� �����������!)
bool NPulseGenerator::SetFrequencyDeviation(real value)
{
 if(value<0)
  return false;

 return Reset();
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NPulseGenerator* NPulseGenerator::New(void)
{
 return new NPulseGenerator;
}
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
bool NPulseGenerator::CheckComponentType(UEPtr<NAContainer> comp) const
{
// if(dynamic_cast<const NPulseChannel*>(comp))
//  return true;

 return false;
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NPulseGenerator::ADefault(void)
{
 SetNumOutputs(2);
 SetOutputDataSize(0,1);
 SetOutputDataSize(1,1);
 Frequency=0.0;
 PulseLength=0.001;
 Amplitude=1.0;
 FrequencyDeviation=0;
 return NSource::ADefault();
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NPulseGenerator::ABuild(void)
{
 return true;
}

// ����� �������� �����.
bool NPulseGenerator::AReset(void)
{
 time_t tm;
 time(&tm);
 srand(static_cast<unsigned>(tm));

 PulseCounter=static_cast<RDK::UTime>(PulseLength.v*TimeStep);
 RandomFrequency=Frequency;
 return NSource::AReset();
}

// ��������� ������ ����� �������
bool NPulseGenerator::ACalculate(void)
{
 if(!Frequency)
 {
  FillOutputData();
  return NSource::ACalculate();
 }

 if(FrequencyDeviation.v == 0)
 {
  if(PulseCounter>0) // ���� ������� ����
  {
   --PulseCounter.v;
   if(PulseCounter <= 0) // ��������� ������� � �������� ��������
   {
	PulseCounter=static_cast<RDK::UTime>(-TimeStep/Frequency.v);
	FillOutputData(0);
   }
  }
  else
  {
   ++PulseCounter.v;
   if(PulseCounter >= 0) // �������� �������
   {
	PulseCounter=static_cast<RDK::UTime>(PulseLength.v*TimeStep);
	FillOutputData(0,&Amplitude.v);
   }
  }
  FillOutputData(1,&Frequency.v);
 }
 else
 {
  if(PulseCounter>0) // ���� ������� ����
  {
   --PulseCounter.v;
   if(PulseCounter <= 0) // ��������� ������� � �������� ��������
   {
	RandomFrequency=real(rand()*FrequencyDeviation*2.0)/real(RAND_MAX)+
							Frequency.v-FrequencyDeviation.v;
	if(RandomFrequency.v>0)
	 PulseCounter=static_cast<RDK::UTime>(-TimeStep/RandomFrequency.v);
	else
	 PulseCounter=0;
	FillOutputData(0);
   }
  }
  else
  {
   ++PulseCounter.v;
   if(PulseCounter >= 0) // �������� �������
   {
	PulseCounter=static_cast<RDK::UTime>(PulseLength.v*TimeStep);
	FillOutputData(0,&Amplitude.v);
   }
  }
  FillOutputData(1,&RandomFrequency.v);
 }

 return true;//NSource::ACalculate();
}
// --------------------------
}
#endif
