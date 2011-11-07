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

#ifndef NAFFERENT_NEURON_CPP
#define NAFFERENT_NEURON_CPP

#include "NAfferentNeuron.h"
#include "NPulseMembrane.h"
#include "NPulseLTZone.h"
#include "../ReceiverLib/NReceptor.h"
#include "../SourceLib/NConstGenerator.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NAfferentNeuron::NAfferentNeuron(void)
//: NPulseNeuron(name)
{
}

NAfferentNeuron::~NAfferentNeuron(void)
{
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NAfferentNeuron* NAfferentNeuron::New(void)
{
 return new NAfferentNeuron;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NAfferentNeuron::CheckComponentType(const NAContainer* comp) const
{
 if(dynamic_cast<const NPulseMembrane*>(comp) ||
	dynamic_cast<const NPulseLTZone*>(comp) ||
	dynamic_cast<const NReceptor*>(comp) ||
	dynamic_cast<const NConstGenerator*>(comp))
  return true;

 return false;
}
// --------------------------
}
#endif
