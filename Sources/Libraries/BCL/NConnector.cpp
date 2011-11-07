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

#ifndef NCONNECTOR_CPP
#define NCONNECTOR_CPP

#include "NConnector.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NConnector::NConnector(void)
//: NADItem(name)
{
}

NConnector::~NConnector(void)
{
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NConnector* NConnector::New(void)
{
 return new NConnector;
}
// --------------------------



}
#endif


