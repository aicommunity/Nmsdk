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

#include "NPhysLibrary.h"

#include "NManipulator.cpp"

namespace NMSDK {      

NPhysLibrary PhysLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPhysLibrary::NPhysLibrary(void)
 : NLibrary("PhysLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NPhysLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NManipulator;
 cont->SetName("Manipulator");
 cont->Default();
 UploadClass("NManipulator",cont);
}
// --------------------------


}
