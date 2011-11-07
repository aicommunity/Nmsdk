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

#include "NBCLLibrary.h"

#include "NConnector.cpp"
#include "NItem.cpp"
#include "NModel.cpp"
#include "NNet.cpp"
#include "NNeuron.cpp"
#include "NReceiver.cpp"
#include "NSource.cpp"


namespace NMSDK {

NBCLLibrary BCLLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NBCLLibrary::NBCLLibrary(void)
 : NLibrary("BCLLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NBCLLibrary::ACreateClassSamples(NStorage *storage)
{
 RDK::UAContainer *cont;

 cont=new NConnector;
 cont->SetName("Input");
 cont->Default();
 UploadClass("NConnector",cont);

 cont=new NNet;
 cont->SetName("Net");
 cont->Default();
 UploadClass("NNet",cont);

 cont=new NModel;
 cont->SetName("Model");
 cont->Default();
 UploadClass("NModel",cont);

 cont=new NNeuron;
 cont->SetName("Neuron");
 cont->Default();
 UploadClass("NNeuron",cont);

 cont=new NSource;
 cont->SetName("Source");
 cont->Default();
 UploadClass("NSource",cont);

 cont=new NReceiver;
 cont->SetName("Receiver");
 cont->Default();
 UploadClass("NReceiver",cont);

 cont=new NItem;
 cont->SetName("Item");
 cont->Default();
 UploadClass("NItem",cont);
}
// --------------------------


}
