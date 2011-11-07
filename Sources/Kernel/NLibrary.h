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
#ifndef NLibraryH
#define NLibraryH

#include "rdk.h"
#include "NBios.h"

namespace NMSDK {

class NLibrary: public RDK::UALibrary
{
protected: // Параметры

protected: // Данные загрузки

private: // Внутренние данные

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NLibrary(const string &name, const string &version);
~NLibrary(void);
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
// Методы управления
// --------------------------
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
protected:
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
virtual void CreateClassSamples(RDK::UAStorage *storage);
virtual void ACreateClassSamples(NStorage *storage)=0;
// --------------------------
};

}

#endif
