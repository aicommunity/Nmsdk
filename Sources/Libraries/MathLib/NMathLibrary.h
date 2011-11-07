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

#ifndef NMathLibraryH
#define NMathLibraryH

#include "../../Kernel/NLibrary.h"

#include "NMExtrapolator.h"
#include "NSum.h"

namespace NMSDK {

class NMathLibrary: public NLibrary
{
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NMathLibrary(void);
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
virtual void ACreateClassSamples(NStorage *storage);
// --------------------------
};             

extern NMathLibrary MathLibrary;

}


#endif
