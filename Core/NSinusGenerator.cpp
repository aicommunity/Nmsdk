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

#ifndef NSINUS_GENERATOR_CPP
#define NSINUS_GENERATOR_CPP

#include "NSinusGenerator.h"
#include "rdk.h"


namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NSinusGenerator::NSinusGenerator(void)
//: NSource(name),
 : Amplitude("Amplitude",this,&NSinusGenerator::SetAmplitude),
  Frequency("Frequency",this,&NSinusGenerator::SetFrequency),

  TimeCounter("TimeCounter",this)
{
 // Устанавливаем новые параметры
// AddLookupParameter("Amplitude",Amplitude);
// AddLookupParameter("Frequency",Frequency);
}

NSinusGenerator::~NSinusGenerator(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду синуса
bool NSinusGenerator::SetAmplitude(const double &value)
{
 return true;
}

// Устанавливает частоту
bool NSinusGenerator::SetFrequency(const double &value)
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
NSinusGenerator* NSinusGenerator::New(void)
{
 return new NSinusGenerator;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NSinusGenerator::ADefault(void)
{
 Amplitude=1.0;
 Frequency=1;
 return NSource::ADefault();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NSinusGenerator::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NSinusGenerator::AReset(void)
{
 TimeCounter=0;
 return NSource::AReset();
}

// Выполняет расчет этого объекта
bool NSinusGenerator::ACalculate(void)
{
 TimeCounter.v+=1.0/TimeStep;
 double tmp=Amplitude*sin(2.0*M_PI*TimeCounter*Frequency);
 for(int i=0;i<GetOutputDataSize(0)[1];i++)
  POutputData[0].Double[i]=tmp;
 return true;//NSource::ACalculate();
}
// --------------------------
}
#endif
