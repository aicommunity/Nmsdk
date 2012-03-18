// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NAPC_CPP
#define NAPC_CPP

#include "NSignumSeparator.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NSignumSeparator::NSignumSeparator(void)
//: NADItem(name),
: Sign("Sign",this,&NSignumSeparator::SetSign),
Gain("Gain",this,&NSignumSeparator::SetGain)
{
}

NSignumSeparator::~NSignumSeparator(void)
{
}
// --------------------------


// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Выделяемый знак
bool NSignumSeparator::SetSign(real value)
{
 return true;
}

// Множитель
bool NSignumSeparator::SetGain(real value)
{
 return true;
}
// --------------------------


// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NSignumSeparator* NSignumSeparator::New(void)
{
 return new NSignumSeparator;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NSignumSeparator::ADefault(void)
{
// AutoNumInputs=true;

 // Начальные значения всем параметрам
 // Амплитуда входных импульсов
 Real values;

 values.assign(1,1);

 Sign=values;

 Gain=values;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NSignumSeparator::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NSignumSeparator::AReset(void)
{
 // Сброс временных переменных
 return true;
}

// Выполняет расчет этого объекта
bool NSignumSeparator::ACalculate(void)
{
 real input;

 int numoutputs=NumOutputs;
 int numios=(NumInputs<numoutputs)?NumInputs:numoutputs;
 for(int i=0;i<numios;i++)
 {
  size_t size=(MinInputDataSize<GetOutputDataSize(i))?MinInputDataSize:GetOutputDataSize(i);
  for(size_t j=0;j<size;j++)
  {
   input=GetInputData(i)->Double[j];

   if((input<0 && Sign[j] >0) || (input>0 && Sign[j] <0))
	POutputData[i].Double[j]=0;
   else
	POutputData[i].Double[j]=input*Sign[j]*Gain[j];
  }
 }

 return true;
}
// --------------------------
}
#endif
