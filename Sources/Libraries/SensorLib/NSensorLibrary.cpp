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

#include "NSensorLibrary.h"

#include "../../Kernel/NStorage.h"
#include "NIntervalSeparator.cpp"
#include "NSignumSeparator.cpp"

namespace NMSDK {
                                  
NSensorLibrary SensorLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NSensorLibrary::NSensorLibrary(void)
 : NLibrary("SensorLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NSensorLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NSignumSeparator;
 cont->SetName("SignumSeparator");
 cont->Default();
 UploadClass("NSignumSeparator",cont);

 cont=new NIntervalSeparator;
 cont->SetName("IntervalSeparator");
 cont->Default();
 UploadClass("NIntervalSeparator",cont);


 // Разделители аналогового сигнала на положительную и отрицательную части
 cont=storage->TakeObject("NSignumSeparator");
 cont->SetName("PosSignumSeparator");
 Real signum;
 signum.assign(1,1.0);
// signum.assign(1,1.0/(2*M_PI));
 cont->Default();
 ((NSignumSeparator*)cont)->Sign=signum;
 UploadClass("NPosSignumSeparator",cont);

 cont=storage->TakeObject("NSignumSeparator");
 cont->SetName("NegSignumSeparator");
 signum.assign(1,-1.0);
// signum.assign(1,-1.0/(2*M_PI));
 cont->Default();
 ((NSignumSeparator*)cont)->Sign=signum;
 UploadClass("NNegSignumSeparator",cont);
}
// --------------------------


}
