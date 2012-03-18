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

#ifndef NPULSE_GENERATOR_CPP
#define NPULSE_GENERATOR_CPP

#include <cstdlib>
#include <cstdio>
#include "NPulseGenerator.h"
//#include "NPulseChannel.h"



namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseGenerator::NPulseGenerator(void)
//: NSource(name),
 : Frequency("Frequency",this,&NPulseGenerator::SetFrequency),
  PulseLength("PulseLength",this,&NPulseGenerator::SetPulseLength),
  Amplitude("Amplitude",this,&NPulseGenerator::SetAmplitude),
  FrequencyDeviation("FrequencyDeviation",this,&NPulseGenerator::SetFrequencyDeviation),

  PulseCounter("PulseCounter",this),
  RandomFrequency("RandomFrequency",this)
{
}

NPulseGenerator::~NPulseGenerator(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает частоту импульсов
bool NPulseGenerator::SetFrequency(real value)
{
 if(value <0)
  return false;

 return Reset();
// return true;
}

// Устанавливает длительность импульса
bool NPulseGenerator::SetPulseLength(real value)
{
 if(value <= 0)
  return false;

 return true;
}

// Устанавливает амплитуду импульсов
bool NPulseGenerator::SetAmplitude(real value)
{
 return true;
}

// Устанавливает отклонение частоты
// (Задает диапазон, не является стандартным отклонением!)
bool NPulseGenerator::SetFrequencyDeviation(real value)
{
 if(value<0)
  return false;

 return Reset();
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NPulseGenerator* NPulseGenerator::New(void)
{
 return new NPulseGenerator;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NPulseGenerator::CheckComponentType(UEPtr<NAContainer> comp) const
{
// if(dynamic_cast<const NPulseChannel*>(comp))
//  return true;

 return false;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NPulseGenerator::ADefault(void)
{
 SetNumOutputs(2);
 SetOutputDataSize(0,1);
 SetOutputDataSize(1,1);
 Frequency=0.0;
 PulseLength=0.001;
 Amplitude=1.0;
 FrequencyDeviation=0;
 return NSource::ADefault();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NPulseGenerator::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NPulseGenerator::AReset(void)
{
 time_t tm;
 time(&tm);
 srand(static_cast<unsigned>(tm));

 PulseCounter=static_cast<RDK::UTime>(PulseLength.v*TimeStep);
 RandomFrequency=Frequency;
 return NSource::AReset();
}

// Выполняет расчет этого объекта
bool NPulseGenerator::ACalculate(void)
{
 if(!Frequency)
 {
  FillOutputData();
  return NSource::ACalculate();
 }

 if(FrequencyDeviation.v == 0)
 {
  if(PulseCounter>0) // Если импульс идет
  {
   --PulseCounter.v;
   if(PulseCounter <= 0) // Выключаем импульс и включаем ожидание
   {
	PulseCounter=static_cast<RDK::UTime>(-TimeStep/Frequency.v);
	FillOutputData(0);
   }
  }
  else
  {
   ++PulseCounter.v;
   if(PulseCounter >= 0) // Включаем импульс
   {
	PulseCounter=static_cast<RDK::UTime>(PulseLength.v*TimeStep);
	FillOutputData(0,&Amplitude.v);
   }
  }
  FillOutputData(1,&Frequency.v);
 }
 else
 {
  if(PulseCounter>0) // Если импульс идет
  {
   --PulseCounter.v;
   if(PulseCounter <= 0) // Выключаем импульс и включаем ожидание
   {
	RandomFrequency=real(rand()*FrequencyDeviation*2.0)/real(RAND_MAX)+
							Frequency.v-FrequencyDeviation.v;
	if(RandomFrequency.v>0)
	 PulseCounter=static_cast<RDK::UTime>(-TimeStep/RandomFrequency.v);
	else
	 PulseCounter=0;
	FillOutputData(0);
   }
  }
  else
  {
   ++PulseCounter.v;
   if(PulseCounter >= 0) // Включаем импульс
   {
	PulseCounter=static_cast<RDK::UTime>(PulseLength.v*TimeStep);
	FillOutputData(0,&Amplitude.v);
   }
  }
  FillOutputData(1,&RandomFrequency.v);
 }

 return true;//NSource::ACalculate();
}
// --------------------------
}
#endif
