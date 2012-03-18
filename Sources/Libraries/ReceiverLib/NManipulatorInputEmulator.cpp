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

#ifndef NMANIPULATOR_INPUT_EMULATOR_CPP
#define NMANIPULATOR_INPUT_EMULATOR_CPP

#include "NManipulatorInputEmulator.h"

namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NManipulatorInputEmulator::NManipulatorInputEmulator(void)
: NManipulatorInput()
{
}

NManipulatorInputEmulator::~NManipulatorInputEmulator(void)
{
}
// --------------------------


// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NManipulatorInputEmulator* NManipulatorInputEmulator::New(void)
{
 return new NManipulatorInputEmulator;
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NManipulatorInputEmulator::ADefault(void)
{
 Voltage=0;   
 
 SetNumOutputs(1);
 SetOutputDataSize(0,1);

 return NManipulatorInput::ADefault();
}


// ����� �������� �����.
bool NManipulatorInputEmulator::AReset(void)
{
 UpdateOutputFlag=true;
 return NManipulatorInput::AReset();
}

// ��������� ������ ����� �������
bool NManipulatorInputEmulator::ACalculate(void)
{
 if(NumInputs >0 && GetInputDataSize(0)>0)
 {
  Voltage=GetInputData(0)->Double[0];
  POutputData[0].Double[0]=Voltage;
 }

 return true;//NManipulatorInput::ACalculate();
}
// --------------------------

}
#endif
