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

#include "NReceiverLibrary.h"

#include "NReceptor.cpp"
#include "NFrequencyReceiver.cpp"
#include "NManipulatorInput.cpp"
#include "NManipulatorInputEmulator.cpp"
#include "NSimpleStatistic.cpp"
#include "NNetworkLinksStatistic.cpp"

namespace NMSDK {    

NReceiverLibrary ReceiverLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NReceiverLibrary::NReceiverLibrary(void)
 : NLibrary("ReceiverLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NReceiverLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NReceptor;
 cont->SetName("Receptor");
 cont->Default();
 UploadClass("NReceptor",cont);

 cont=new NFrequencyReceiver;
 cont->SetName("FrequencyReceiver");
 cont->Default();
 UploadClass("NFrequencyReceiver",cont);

 cont=new NManipulatorInput;
 cont->SetName("ManipulatorInput");
 cont->Default();
 UploadClass("NManipulatorInput",cont);

 cont=new NManipulatorInputEmulator;
 cont->SetName("ManipulatorInputEmulator");
 cont->Default();
 UploadClass("NManipulatorInputEmulator",cont);

 cont=new NSimpleStatistic;
 cont->SetName("SimpleStatistic");
 cont->Default();
 UploadClass("NSimpleStatistic",cont);

 cont=new NNetworkLinksStatistic;
 cont->SetName("NetworkLinksStatistic");
 cont->Default();
 UploadClass("NNetworkLinksStatistic",cont);
}
// --------------------------


}
