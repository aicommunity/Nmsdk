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

#include "NActLibrary.h"
#include "NDCEngine.cpp"
#include "NPac.cpp"

namespace NMSDK {
                   
NActLibrary ActLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NActLibrary::NActLibrary(void)
 : NLibrary("ActLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NActLibrary::ACreateClassSamples(NStorage *storage)
{
 RDK::UAContainer *cont;

 cont=new NDCEngine;
 cont->SetName("DCEngine");
 cont->Default();
 UploadClass("NDCEngine",cont);

 cont=new NPac;
 cont->SetName("Pac");
 cont->Default();
 UploadClass("NPac",cont);
}
// --------------------------


}
