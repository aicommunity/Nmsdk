/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NCRLibraryH
#define NCRLibraryH

#include "../../Kernel/NLibrary.h"

#include "NCRPerseptron.h"
#include "NCRDirectCompare.h"
#include "NCRDistance.h"
#include "NCRFusion.h"

namespace NMSDK {

class NCRLibrary: public NLibrary
{
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRLibrary(void);
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
virtual void ACreateClassSamples(NStorage *storage);
// --------------------------
};                   

extern NCRLibrary CRLibrary;

}


#endif
