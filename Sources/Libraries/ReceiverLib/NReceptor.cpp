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

#ifndef NRECEPTOR_CPP
#define NRECEPTOR_CPP

#include "NReceptor.h"



namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NReceptor::NReceptor(void)
//: NSource(name),
 : Gain("Gain",this,&NReceptor::SetGain),
  MinInputRange("MinInputRange",this),
  MaxInputRange("MaxInputRange",this),
  MinOutputRange("MinOutputRange",this),
  MaxOutputRange("MaxOutputRange",this),
  InputAdaptationMode("InputAdaptationMode",this),
  ExpCoeff("ExpCoeff",this),
  OutputAdaptationMode("OutputAdaptationMode",this),
  SumCoeff("SumCoeff",this),
  InputAdaptationArrestingTC("InputAdaptationArrestingTC",this)
{
}

NReceptor::~NReceptor(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Коэффициент усиления входного сигнала
bool NReceptor::SetGain(real value)
{
 if(value <=0)
  return false;

 return true;
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NReceptor* NReceptor::New(void)
{
 return new NReceptor;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NReceptor::ADefault(void)
{
 Gain=1;
 MinOutputRange=0.0;
 MaxOutputRange=0.01;//0.1;
 MinInputRange=0;
 MaxInputRange=10;
 InputAdaptationMode=1;
 OutputAdaptationMode=1;
 ExpCoeff=1;
 SumCoeff=2;
 InputAdaptationArrestingTC=1;
 return NSource::ADefault();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NReceptor::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NReceptor::AReset(void)
{
 return NSource::AReset();
}

// Выполняет расчет этого объекта
bool NReceptor::ACalculate(void)
{
 OutputRange=MaxOutputRange.v-MinOutputRange.v;

 size_t k=0;
 for(int i=0;i<NumInputs;i++)
  for(size_t j=0;j<PInputDataSize[i];j++)
  {
   real input=PInputData[i]->Double[j];
   if(k >= GetOutputDataSize(0))
	break;

   switch(InputAdaptationMode.v)
   {
   case 1:
	if(input<MinInputRange.v)
	 MinInputRange=input;
	if(input>MaxInputRange.v)
	 MaxInputRange=input;
   break;

   case 2:
	if(input<MinInputRange.v)
	 MinInputRange=input;
	else // забывание
	{
	 MinInputRange.v-=MinInputRange.v/(InputAdaptationArrestingTC*TimeStep);
	}

	if(input>MaxInputRange.v)
	 MaxInputRange=input;
	else // забывание
	{
     MaxInputRange.v-=MaxInputRange.v/(InputAdaptationArrestingTC*TimeStep);
	}
   break;
   }

   InputRange=MaxInputRange.v-MinInputRange.v;
   if(!InputRange)
	return true;

   // Преобразовываем сигнал к заданному диапазону
   input=(input-MinInputRange.v)*OutputRange/InputRange+MinOutputRange.v;  
   real exp_coeff;

   switch(OutputAdaptationMode.v)
   {
   case 0:
	POutputData[0].Double[k]=Gain*input;
   break;

   case 1:
	// Преобразовываем сигнал к заданному диапазону
	POutputData[0].Double[k]=Gain*(SumCoeff.v-exp(-ExpCoeff.v*input));
   break;

   case 2:
	// Преобразовываем сигнал к заданному диапазону
	POutputData[0].Double[k]=Gain*exp(-ExpCoeff.v*input);
   break;

   case 3:
	// Преобразовываем сигнал к автодиапазону
	exp_coeff=-log(0.9)/InputRange;
	POutputData[0].Double[k]=Gain*(SumCoeff.v-exp(-exp_coeff*input));
   break;

   case 4:
	POutputData[0].Double[k]=Gain*(1.0+input);
   break;
   }

   ++k;
  }
 return NSource::ACalculate();
}
// --------------------------
}
#endif
