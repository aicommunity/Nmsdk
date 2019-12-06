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

#ifndef NCONTROL_OBJECT_SOURCE_CPP
#define NCONTROL_OBJECT_SOURCE_CPP

#include "NControlObjectSource.h"



namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NControlObjectSource::NControlObjectSource(void)
: NSource(),
  DataIndexes("DataIndexes",this),
  DataShift("DataShift",this,&NControlObjectSource::SetDataShift),
  DataMul("DataMul",this)
{
 UpdateOutputFlag=false;
}

NControlObjectSource::~NControlObjectSource(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает угол, скорость, момент 
bool NControlObjectSource::SetDataShift(const std::vector<double> &value)
{
 return true;
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NControlObjectSource* NControlObjectSource::New(void)
{
 return new NControlObjectSource;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NControlObjectSource::ADefault(void)
{
 SetNumOutputs(5);
 SetOutputDataSize(0,MMatrixSize(1,1));
 SetOutputDataSize(1,MMatrixSize(1,1));
 SetOutputDataSize(2,MMatrixSize(1,1));
 SetOutputDataSize(3,MMatrixSize(1,1));
 SetOutputDataSize(4,MMatrixSize(1,1));

 return NSource::ADefault();
}


// Сброс процесса счета.
bool NControlObjectSource::AReset(void)
{
 UpdateOutputFlag=true;
 DataShift->resize(GetNumInputs(),0.0);
 DataIndexes->resize(GetNumInputs(),0);
 DataMul->resize(GetNumInputs(),1.0);
 return NSource::AReset();
}

// Выполняет расчет этого объекта
bool NControlObjectSource::ACalculate(void)
{
 DataShift->resize(GetNumInputs(),0.0);
 DataIndexes->resize(GetNumInputs(),0);
 DataMul->resize(GetNumInputs(),1.0);
 SetNumOutputs(NumInputs);

 for(int i=0;i<NumInputs;i++)
 {
  if(GetInputDataSize((*DataIndexes)[i])[1]>0)
  {
   SetOutputDataSize(i,MMatrixSize(1,1));
   POutputData[i].Double[0]=(*DataMul)[i]*(GetInputData((*DataIndexes)[i])->Double[0]-(*DataShift)[i]);
  }
 }
 return true;
}
// --------------------------
}
#endif
