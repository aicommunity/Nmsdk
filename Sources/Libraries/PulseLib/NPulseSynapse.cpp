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

#ifndef NPULSE_SYNAPSE_CPP
#define NPULSE_SYNAPSE_CPP

#include "NPulseSynapse.h"
#include "NPulseNeuron.h"
#include "NPulseChannel.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseSynapse::NPulseSynapse(void)
 //: NConnector(name),
: PulseAmplitude("PulseAmplitude",this,&NPulseSynapse::SetPulseAmplitude),
SecretionTC("SecretionTC",this,&NPulseSynapse::SetSecretionTC),
DissociationTC("DissociationTC",this,&NPulseSynapse::SetDissociationTC),
InhibitionCoeff("InhibitionCoeff",this,&NPulseSynapse::SetInhibitionCoeff),
Resistance("Resistance",this,&NPulseSynapse::SetResistance),

PreOutput("PreOutput",this)
{
}

NPulseSynapse::~NPulseSynapse(void)
{
}
// --------------------------


// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду импульсов
bool NPulseSynapse::SetPulseAmplitude(real value)
{
 return true;
}

// Постоянная времени выделения медиатора
bool NPulseSynapse::SetSecretionTC(real value)
{
 if(value <= 0)
  return false;

 Ready=false;

 return true;
}

// Постоянная времени распада медиатора
bool NPulseSynapse::SetDissociationTC(real value)
{
 if(value <= 0)
  return false;

 Ready=false;

 return true;
}

// Коэффициент пресинаптического торможения
bool NPulseSynapse::SetInhibitionCoeff(real value)
{
 if(Resistance.v > 0)
  OutputConstData=4.0*(value+1)/Resistance.v;
 else
  OutputConstData=0;

 return true;
}

// Вес (эффективность синапса) синапса
bool NPulseSynapse::SetResistance(real value)
{
 if(value<=0)
  return false;

 OutputConstData=4.0*InhibitionCoeff.v/value;

 return true;
}
// --------------------------


// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NPulseSynapse* NPulseSynapse::New(void)
{
 return new NPulseSynapse;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NPulseSynapse::ADefault(void)
{
 // Начальные значения всем параметрам
 // Амплитуда входных импульсов
 PulseAmplitude=1;

 // Постоянная времени выделения медиатора
 SecretionTC=0.001;

 // Постоянная времени распада медиатора
 DissociationTC=0.01;

 // Коэффициент пресинаптического торможения
 InhibitionCoeff=1;

 // Вес (эффективность синапса) синапса
 Resistance=1.0e8;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NPulseSynapse::ABuild(void)
{
 VSecretionTC=SecretionTC*TimeStep;
 VDissociationTC=DissociationTC*TimeStep;

 return true;
}

// Сброс процесса счета.
bool NPulseSynapse::AReset(void)
{
 // Сброс временных переменных
 PreOutput=0;

 return true;
}

// Выполняет расчет этого объекта
bool NPulseSynapse::ACalculate(void)
{
 real input=0;

 if(NumInputs >0 && GetInputDataSize(0)>0)
 {
  input=GetInputData(0)->Double[0];
  if(MainOwner && Owner)
  {
   if(static_pointer_cast<NPulseChannel>(Owner)->Type() < 0)
	++static_pointer_cast<NPulseNeuron>(MainOwner)->NumActivePosInputs.v;
   else
	++static_pointer_cast<NPulseNeuron>(MainOwner)->NumActiveNegInputs.v;
  }
 }

 if(input>0)
  PreOutput.v+=(input/PulseAmplitude.v-PreOutput.v)/VSecretionTC;
 else
  PreOutput.v-=PreOutput.v/VDissociationTC;

 POutputData[0].Double[0]=OutputConstData*
						(1.0-InhibitionCoeff.v*PreOutput.v)*PreOutput.v;

 if(POutputData[0].Double[0]<0)
  POutputData[0].Double[0]=0;

 return true;
}
// --------------------------
}
#endif
