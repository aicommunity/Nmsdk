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
  AvgInterval("AvgInterval",this),

  PulseCounter("PulseCounter",this),
  RandomFrequency("RandomFrequency",this),
  AvgFrequencyCounter("AvgFrequencyCounter",this)
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
bool NPulseGenerator::SetFrequency(const real &value)
{
 if(value <0)
  return false;

// return Reset();
 return true;
}

// Устанавливает длительность импульса
bool NPulseGenerator::SetPulseLength(const real &value)
{
 if(value <= 0)
  return false;

 return true;
}

// Устанавливает амплитуду импульсов
bool NPulseGenerator::SetAmplitude(const real &value)
{
 return true;
}

// Устанавливает отклонение частоты
// (Задает диапазон, не является стандартным отклонением!)
bool NPulseGenerator::SetFrequencyDeviation(const real &value)
{
 if(value<0)
  return false;

 return true;
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
bool NPulseGenerator::CheckComponentType(UEPtr<UContainer> comp) const
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
 SetNumOutputs(4);
 SetOutputDataSize(0,1);
 SetOutputDataSize(1,1);
 Frequency=0.0;
 PulseLength=0.001;
 Amplitude=1.0;
 FrequencyDeviation=0;
 AvgInterval=5;
 PulseCounter=0;
 return NSource::ADefault();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NPulseGenerator::ABuild(void)
{
 AvgFrequencyCounter->clear();
 return true;
}

// Сброс процесса счета.
bool NPulseGenerator::AReset(void)
{
 time_t tm;
 time(&tm);
 srand(static_cast<unsigned>(tm));

// PulseCounter=static_cast<RDK::UTime>(PulseLength.v*TimeStep);
 if(Frequency.v > 0 && PulseCounter.v<-TimeStep/Frequency.v)
  PulseCounter.v=-TimeStep/Frequency.v;
 else
  PulseCounter.v=0;
 RandomFrequency=Frequency;
 //AvgFrequencyCounter->clear();
 return NSource::AReset();
}

// Выполняет расчет этого объекта
bool NPulseGenerator::ACalculate(void)
{
 if(!Frequency)
 {
  FillOutputData();
  AvgFrequencyCounter->clear();
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
	FillOutputData(1);
   }
  }
  else
  {
   ++PulseCounter.v;
   if(PulseCounter >= 0) // Включаем импульс
   {
	PulseCounter=static_cast<RDK::UTime>(PulseLength.v*TimeStep);
	FillOutputData(0,&Amplitude.v);
	FillOutputData(1,&Amplitude.v);
	AvgFrequencyCounter->push_back(Environment->GetTime().GetDoubleTime());
   }
  }
  FillOutputData(2,&Frequency.v);
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
	FillOutputData(1);
   }
  }
  else
  {
   ++PulseCounter.v;
   if(PulseCounter >= 0) // Включаем импульс
   {
	PulseCounter=static_cast<RDK::UTime>(PulseLength.v*TimeStep);
	FillOutputData(0,&Amplitude.v);
	FillOutputData(1,&Amplitude.v);
	AvgFrequencyCounter->push_back(Environment->GetTime().GetDoubleTime());
   }
  }
  FillOutputData(2,&RandomFrequency.v);
 }

 list<double>::iterator I,J,K;
 I=AvgFrequencyCounter->begin();
 J=AvgFrequencyCounter->end();

 if(AvgFrequencyCounter->size()>1)
 {
  while(I != J)
  {
   if(Environment->GetTime().GetDoubleTime()-*I>AvgInterval)// && AvgFrequencyCounter->size()>3)
   {
	K=I;
	++I;
	AvgFrequencyCounter->erase(K);
   }
   else
	++I;
  }
 }

 I=AvgFrequencyCounter->begin();
 J=AvgFrequencyCounter->end();
 SetOutputDataSize(3,AvgFrequencyCounter->size(),true);
 for(int i=0;i<POutputData[3].GetSize();i++,++I)
  POutputData[3].Double[i]=*I;

 return true;//NSource::ACalculate();
}
// --------------------------
}
#endif
