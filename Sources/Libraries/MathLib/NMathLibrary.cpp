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

#include "NMathLibrary.h"


#include "NMExtrapolator.cpp"
#include "NSum.cpp"


namespace NMSDK {
                    
NMathLibrary MathLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NMathLibrary::NMathLibrary(void)
 : NLibrary("MathLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NMathLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NMExtrapolator;
 cont->SetName("MExtrapolator");
 cont->Default();
 UploadClass("NMExtrapolator",cont);

 cont=new NSum;
 cont->SetName("Sum");
 cont->Default();
 UploadClass("NSum",cont);
}
// --------------------------


}
