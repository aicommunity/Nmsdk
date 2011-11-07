/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		1.0.0

This file - part of the project: NMSDK

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#include "NLibrary.h"

namespace NMSDK {

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NLibrary::NLibrary(const string &name, const string &version)
 : RDK::UALibrary(name,version)
{
}

NLibrary::~NLibrary(void)
{
}
// --------------------------

// --------------------------
// Методы доступа к параметрам библиотеки
// --------------------------
// --------------------------

// --------------------------
// Методы доступа к данным загрузки
// --------------------------
// --------------------------

// --------------------------
// Методы доступа к данным библиотеки
// --------------------------
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
void NLibrary::CreateClassSamples(RDK::UAStorage *storage)
{
 ACreateClassSamples(reinterpret_cast<NStorage*>(storage));
}
// --------------------------




}

//---------------------------------------------------------------------------

