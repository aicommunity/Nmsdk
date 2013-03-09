/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NSourceLibraryH
#define NSourceLibraryH

#include "../../Kernel/NSupport.h"

#include "NConstGenerator.h"
#include "NPulseGenerator.h"
#include "NSinusGenerator.h"
#include "NFileGenerator.h"
#include "NManipulatorSourceEmulator.h"
#include "NManipulatorSource.h"

namespace NMSDK {

class NSourceLibrary: public ULibrary
{
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NSourceLibrary(void);
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
virtual void CreateClassSamples(UStorage *storage);
// --------------------------
};    

extern NSourceLibrary SourceLibrary;

}


#endif
