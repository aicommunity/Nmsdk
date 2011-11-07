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

#ifndef NMODEL_CPP
#define NMODEL_CPP

#include "NModel.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NModel::NModel(void)
//: NANet(name)
{
}

NModel::~NModel(void)
{
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NModel* NModel::New(void)
{
 return new NModel;
}
// --------------------------



}
#endif


