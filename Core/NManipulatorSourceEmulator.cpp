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

// Методы
// --------------------------
// Конструкторы и деструкторы
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
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NManipulatorSourceEmulator* NManipulatorSourceEmulator::New(void)
{
 return new NManipulatorSourceEmulator;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NManipulatorSourceEmulator::ADefault(void)
{
 Angle=2;
 Speed=0;
 Force=5;   
 
 SetNumOutputs(3);
 SetOutputDataSize(0,MMatrixSize(1,1));
 SetOutputDataSize(1,MMatrixSize(1,1));
 SetOutputDataSize(2,MMatrixSize(1,1));

 return NManipulatorSource::ADefault();
}


// Сброс процесса счета.
bool NManipulatorSourceEmulator::AReset(void)
{
 UpdateOutputFlag=true;
 return NManipulatorSource::AReset();
}

// Выполняет расчет этого объекта
bool NManipulatorSourceEmulator::ACalculate(void)
{
 if(NumInputs >0 && GetInputDataSize(0)[1]>0)
  POutputData[0].Double[0]=GetInputData(0)->Double[0];

 if(NumInputs >1 && GetInputDataSize(1)[1]>0)
  POutputData[1].Double[0]=GetInputData(1)->Double[0];

 if(NumInputs >2 && GetInputDataSize(2)[1]>0)
  POutputData[2].Double[0]=GetInputData(2)->Double[0];
 return true;//NManipulatorSource::ACalculate();
}
// --------------------------
}
#endif
