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

#ifndef NRECEIVER_CPP
#define NRECEIVER_CPP

#include "NReceiver.h"

namespace NMSDK {


// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NReceiver::NReceiver(void)
//: NADItem(name)//NAConnector(name)
{
}

NReceiver::~NReceiver(void)
{
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NReceiver* NReceiver::New(void)
{
 return new NReceiver;
}
// --------------------------


}
#endif


