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

#ifndef NINTERVAL_SEPARATOR_CPP
#define NINTERVAL_SEPARATOR_CPP

#include "NIntervalSeparator.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NIntervalSeparator::NIntervalSeparator(void)
//: NADItem(name),
: MinRange("MinRange",this,&NIntervalSeparator::SetMinRange),
MaxRange("MaxRange",this,&NIntervalSeparator::SetMaxRange),
Mode("Mode",this,&NIntervalSeparator::SetMode),
Gain("Gain",this,&NIntervalSeparator::SetGain)
{
}

NIntervalSeparator::~NIntervalSeparator(void)
{
}
// --------------------------


// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Нижняя граница выделяемого интервала
bool NIntervalSeparator::SetMinRange(real value)
{
 return true;
}

// Верхняя граница выделяемого интервала
bool NIntervalSeparator::SetMaxRange(real value)
{
 return true;
}

// Режим разделения
bool NIntervalSeparator::SetMode(int value)
{
 if(value < 0 && value >3)
  return false;

 return true;
}

// Множитель выходного значения
bool NIntervalSeparator::SetGain(real value)
{
 return true;
}
// --------------------------


// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NIntervalSeparator* NIntervalSeparator::New(void)
{
 return new NIntervalSeparator;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NIntervalSeparator::ADefault(void)
{
 // Начальные значения всем параметрам
 // Амплитуда входных импульсов
 Real values;

 values.assign(1,0);
 MinRange=values;

 values.assign(1,1);
 MaxRange=values;

 vector<int> mode;
 mode.assign(1,2);
 Mode=mode;

 values.assign(1,1);
 Gain=values;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NIntervalSeparator::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NIntervalSeparator::AReset(void)
{
 // Сброс временных переменных
 return true;
}

// Выполняет расчет этого объекта
bool NIntervalSeparator::ACalculate(void)
{
 size_t size=(MinInputDataSize<GetOutputDataSize(0))?MinInputDataSize:GetOutputDataSize(0);
 real input;

 for(int i=0;i<NumInputs;i++)
 {
  for(size_t j=0;j<size;j++)
  {
   input=GetInputData(i)->Double[j];
   switch(Mode[j])
   {
   case 0:
	if(input<MinRange[j] || input>MaxRange[j])
	 POutputData[0].Double[j]=0;
	else
	 POutputData[0].Double[j]=input;
   break;

   case 1:
	if(input<MinRange[j] || input>MaxRange[j])
	 POutputData[0].Double[j]=0;
	else
	 POutputData[0].Double[j]=input-MinRange[j];
   break;

   case 2:
	if(input>MinRange[j])
	 POutputData[0].Double[j]=input;
   break;

   case 3:
	if(input<MaxRange[j])
	 POutputData[0].Double[j]=input;
	else
	 POutputData[0].Double[j]=0;
   break;

   case 4:
	if(input>MinRange[j])
	 POutputData[0].Double[j]=input-MinRange[j];
	else
	 POutputData[0].Double[j]=0;
   break;

   case 5:
	if(input>=0)
	{
	 if(input>MinRange[j] && input<MaxRange[j])
	  POutputData[0].Double[j]=input-MinRange[j];
	 else
	 if(input>MaxRange[j] && MaxRange[j]>0)
	  POutputData[0].Double[j]=MaxRange[j]-MinRange[j];
	 else
	  POutputData[0].Double[j]=0;
	}
	else
	{
	 if(input>MinRange[j] && input<MaxRange[j])
	  POutputData[0].Double[j]=input-MaxRange[j];
	 else
	 if(input<MinRange[j] && MinRange[j]<0)
	  POutputData[0].Double[j]=MinRange[j]-MaxRange[j];
	 else
	  POutputData[0].Double[j]=0;
	}
   break;
   }
   POutputData[0].Double[j]*=Gain[j];
//   POutputData[0].Double[j]=fabs(POutputData[0].Double[j]);
  }
  break;
 }

 return true;
}
// --------------------------
}
#endif
