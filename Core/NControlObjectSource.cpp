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
  DataMul("DataMul",this),
  Input("Input",this),
  Output("Output",this)
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
bool NControlObjectSource::SetDataShift(const MDMatrix<double> &value)
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
/* SetNumOutputs(5);
 SetOutputDataSize(0,MMatrixSize(1,1));
 SetOutputDataSize(1,MMatrixSize(1,1));
 SetOutputDataSize(2,MMatrixSize(1,1));
 SetOutputDataSize(3,MMatrixSize(1,1));
 SetOutputDataSize(4,MMatrixSize(1,1));
  */
 return NSource::ADefault();
}


// Сброс процесса счета.
bool NControlObjectSource::AReset(void)
{
 UpdateOutputFlag=true;
 DataShift.Assign(Input.GetMatrixSize(),0.0);
 DataIndexes.Assign(Input.GetRows(),0.0);
 DataMul.Assign(Input.GetMatrixSize(),1.0);
 Output.Assign(Input.GetMatrixSize(),0.0);
 return NSource::AReset();
}

// Выполняет расчет этого объекта
bool NControlObjectSource::ACalculate(void)
{
 UpdateOutputFlag=true;
 DataShift.Resize(Input.GetMatrixSize());
 DataIndexes.Resize(Input.GetRows());
 DataMul.Resize(Input.GetMatrixSize());
 Output.Resize(Input.GetMatrixSize());

 for(int i=0;i<Input.GetRows();i++)
 {
  for(int j=0;j<Input.GetCols();j++)
   Output(i,j)=DataMul(i,j)*(Input(DataIndexes(i),j)-DataShift(i,j));
 }
 return true;
}
// --------------------------
}
#endif
