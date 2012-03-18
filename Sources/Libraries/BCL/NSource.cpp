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

#ifndef NSOURCE_CPP
#define NSOURCE_CPP

#include "NSource.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NSource::NSource(void)
//: NADItem(name),
 : ActionPeriod("ActionPeriod",this,&NSource::SetActionPeriod),
  ActionCounter("ActionCounter",this)
{
}

NSource::~NSource(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Длительность работы с момента включения
bool NSource::SetActionPeriod(RDK::UTime value)
{
 if(value < 0)
  return false;

 return true;
}
// --------------------------


// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NSource* NSource::New(void)
{
 return new NSource;
}
// --------------------------


// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NSource::ADefault(void)
{
 ActionPeriod=0;

 return true;
}

// Сброс процесса счета.
bool NSource::AReset(void)
{
 ActionCounter=ActionPeriod;
 return true;
}

// Выполняет расчет этого объекта
/*bool NSource::ACalculate(void)
{
 if(ActionCounter.v>0)
 {
  ActionCounter-=TimeStep.v;
  if(ActionCounter.v <= 0) // Выключаем импульс и включаем ожидание
  {
   ActionCounter=0;
   Activity=false;
  }
 }

 return true;
}      */
// --------------------------
}
#endif


