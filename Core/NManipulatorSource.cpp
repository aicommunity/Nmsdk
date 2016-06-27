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

#ifndef NMANIPULATOR_SOURCE_CPP
#define NMANIPULATOR_SOURCE_CPP

#include "NManipulatorSource.h"



namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NManipulatorSource::NManipulatorSource(void)
: NSource(),
  Angle("Angle",this,&NManipulatorSource::SetAngle),
  Speed("Speed",this,&NManipulatorSource::SetSpeed),
  Force("Force",this,&NManipulatorSource::SetForce),
  Movement("Movement",this)
{
 UpdateOutputFlag=0;
}

NManipulatorSource::~NManipulatorSource(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает угол, скорость, момент 
bool NManipulatorSource::SetAngle(const double &value)
{
 return true;
}

bool NManipulatorSource::SetSpeed(const double &value)
{
 return true;
}

bool NManipulatorSource::SetForce(const double &value)
{
 return true;
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NManipulatorSource* NManipulatorSource::New(void)
{
 return new NManipulatorSource;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NManipulatorSource::ADefault(void)
{
 Angle=0;
 Speed=0;
 Force=0;
 Movement=0;
 
 SetNumOutputs(4);
 SetOutputDataSize(0,MMatrixSize(1,1));
 SetOutputDataSize(1,MMatrixSize(1,1));
 SetOutputDataSize(2,MMatrixSize(1,1));
 SetOutputDataSize(3,MMatrixSize(1,1));

 return NSource::ADefault();
}


// Сброс процесса счета.
bool NManipulatorSource::AReset(void)
{
 UpdateOutputFlag=true;
 return NSource::AReset();
}

// Выполняет расчет этого объекта
bool NManipulatorSource::ACalculate(void)
{
// POutputData[0]->Float[0]=PInputData[0]->Float[0];
/* if(UpdateOutputFlag)
 {
  FillOutputData(0,&Angle.v);
  FillOutputData(1,&Speed.v);
  FillOutputData(2,&Force.v);
  UpdateOutputFlag=false;
 }*/
 if(NumInputs >0 && GetInputDataSize(0)[1]>0)
 {
  if(NumInputs<=4)
   POutputData[0].Double[0]=GetInputData(0)->Double[0]-Movement;
  else
   POutputData[0].Double[0]=GetInputData(0)->Double[0]-GetInputData(4)->Double[0];
 }

 if(NumInputs >1 && GetInputDataSize(1)[1]>0)
 {
  if(NumInputs<=5)
   POutputData[1].Double[0]=GetInputData(1)->Double[0]-Angle;
  else
   POutputData[1].Double[0]=GetInputData(1)->Double[0]-GetInputData(5)->Double[0];
 }

 if(NumInputs >2 && GetInputDataSize(2)[1]>0)
  POutputData[2].Double[0]=GetInputData(2)->Double[0];

 if(NumInputs >3 && GetInputDataSize(3)[1]>0)
  POutputData[3].Double[0]=GetInputData(3)->Double[0];
 return true;//NManipulatorSource::ACalculate();
}
// --------------------------
}
#endif
