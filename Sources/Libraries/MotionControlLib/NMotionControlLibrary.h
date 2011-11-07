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

#ifndef NMotionControlLibraryH
#define NMotionControlLibraryH

#include "NEngineMotionControl.h"
#include "../../Kernel/NLibrary.h"
#include "NMotionElement.h"

namespace NMSDK {

class NMotionControlLibrary: public NLibrary
{
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NMotionControlLibrary(void);
// --------------------------

// --------------------------
// Методы создания составных моделей
// --------------------------
// --------------------------


// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
virtual void ACreateClassSamples(NStorage *storage);
// --------------------------
};     

extern NMotionControlLibrary MotionControlLibrary;

}


#endif
