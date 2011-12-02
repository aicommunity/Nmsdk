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

#include "NNeuronLifeLibrary.h"

#include "NLifeNet.cpp"
#include "NNeuronLife.cpp"
#include "NPulseLifeNeuron.cpp"
#include "../../Kernel/NStorage.h"



namespace NMSDK {     

NNeuronLifeLibrary NeuronLifeLibrary;


bool CreateNeuronLifeObject(UEPtr<NNeuronLife> &life, NStorage *storage)
{
 if(life || !storage)
  return false;

 life=static_pointer_cast<NNeuronLife>(storage->TakeObject("NEmptyNeuronLife"));
 if(!life)
  return false;

 UEPtr<NSum> sum=static_pointer_cast<NSum>(storage->TakeObject("NSum"));
 if(!sum)
  return false;

 sum->SetName("ExternalEnergyBonus");

 if(life->AddComponent(sum,&life->ExternalEnergyBonus) == ForbiddenId)
  return false;

 return true;
}

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NNeuronLifeLibrary::NNeuronLifeLibrary(void)
 : NLibrary("NeuronLifeLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NNeuronLifeLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;
 cont=new NPulseLifeNeuron;
 cont->SetName("PLifeNeuron");
 cont->Default();
 UploadClass("NPLifeNeuron",cont);

 cont=new NNeuronLife;
 cont->SetName("NeuronLife");
 cont->Default();
 UploadClass("NEmptyNeuronLife",cont);

 cont=new NLifeNet;
 cont->SetName("LifeNet");
 cont->Default();
 UploadClass("NLifeNet",cont);

 UEPtr<NNeuronLife> life;
 if(CreateNeuronLifeObject(life,storage))
 {
  life->Default();
  UploadClass("NNeuronLife",life);
 }
}
// --------------------------


}
