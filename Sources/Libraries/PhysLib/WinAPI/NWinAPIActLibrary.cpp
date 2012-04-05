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

#include "NWinAPIActLibrary.h"
#include "NWPhysicalManipulator.cpp"

namespace NMSDK {
                   
NWinAPIActLibrary WinAPIActLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NWinAPIActLibrary::NWinAPIActLibrary(void)
 : NLibrary("WinAPIActLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NWinAPIActLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NWPhysicalManipulator;
 cont->SetName("WPhysicalManipulator");
 cont->Default();
 UploadClass("NWPhysicalManipulator",cont);
}
// --------------------------


}
