// ===========================================================
// Version:        3.0.2
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:        alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NMANIPULATOR_SOURCE_EMULATOR_CPP
#define NMANIPULATOR_SOURCE_EMULATOR_CPP

#include "NManipulatorSourceEmulator.h"

namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NManipulatorSourceEmulator::NManipulatorSourceEmulator(void)
: NManipulatorSource()
{
}

NManipulatorSourceEmulator::~NManipulatorSourceEmulator(void)
{
}
// --------------------------

// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NManipulatorSourceEmulator* NManipulatorSourceEmulator::New(void)
{
 return new NManipulatorSourceEmulator;
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NManipulatorSourceEmulator::ADefault(void)
{
 Angle=2;
 Speed=0;
 Force=5;   
 
 SetNumOutputs(3);
 SetOutputDataSize(0,1);
 SetOutputDataSize(1,1);
 SetOutputDataSize(2,1);

 return NManipulatorSource::ADefault();
}


// ����� �������� �����.
bool NManipulatorSourceEmulator::AReset(void)
{
 UpdateOutputFlag=true;
 return NManipulatorSource::AReset();
}

// ��������� ������ ����� �������
bool NManipulatorSourceEmulator::ACalculate(void)
{
 size_t numout=NumOutputs;
 if(NumInputs >0 && PInputDataSize[0]>0)
  POutputData[0].Double[0]=PInputData[0]->Double[0];

 if(NumInputs >1 && PInputDataSize[1]>0)
  POutputData[1].Double[0]=PInputData[1]->Double[0];

 if(NumInputs >2 && PInputDataSize[2]>0)
  POutputData[2].Double[0]=PInputData[2]->Double[0];
 return true;//NManipulatorSource::ACalculate();
}
// --------------------------
}
#endif
