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
#ifndef NPULSE_LIBRARY_CPP
#define NPULSE_LIBRARY_CPP

#include "NPulseLibrary.h"

#include "NAfferentNeuron.cpp"
#include "NEyeMuscle.cpp"
#include "NMuscle.cpp"
#include "NPulseChannel.cpp"
#include "NPulseSynChannel.cpp"
#include "NPulseHebbSynapse.cpp"
#include "NPulseLTZone.cpp"
#include "NPulseMembrane.cpp"
#include "NPulseNeuron.cpp"
#include "NPulseSynapse.cpp"


namespace NMSDK {   

NPulseLibrary PulseLibrary;


// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseLibrary::NPulseLibrary(void)
 : NLibrary("PulseLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NPulseLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NPulseNeuron;
 cont->SetName("PNeuron");
 cont->Default();
 UploadClass("NPNeuron",cont);

/* cont=new NPulseLifeNeuron("PLifeNeuron");
 cont->Default();
 UploadClass("NPLifeNeuron",cont);
  */
 cont=new NAfferentNeuron;
 cont->SetName("AfferentNeuron");
 cont->Default();
 UploadClass("NAfferentNeuron",cont);

 cont=new NPulseLTZone;
 cont->SetName("PLTZone");
 cont->Default();
 UploadClass("NPLTZone",cont);

 cont=new NPulseMembrane;
 cont->SetName("PMembrane");
 cont->Default();
 UploadClass("NPMembrane",cont);

 cont=new NPulseChannel;
 cont->SetName("PChannel");
 cont->Default();
 UploadClass("NPChannel",cont);

 cont=new NPulseSynapse;
 cont->SetName("PSynapse");
 cont->Default();
 UploadClass("NPSynapse",cont);

 cont=new NPulseSynChannel;
 cont->SetName("PChannel");
 cont->Default();
 UploadClass("NPSynChannel",cont);

 cont=new NPulseHebbSynapse;
 cont->SetName("PHebbSynapse");
 cont->Default();
 UploadClass("NPHebbSynapse",cont);

 cont=new NEyeMuscle;
 cont->SetName("EyeMuscle");
 cont->Default();
 UploadClass("NEyeMuscle",cont);

 cont=new NMuscle;
 cont->SetName("Muscle");
 cont->Default();
 UploadClass("NMuscle",cont);
/*
 cont=new NNeuronLife("NeuronLife");
 cont->Default();
 UploadClass("NNeuronLife",cont);

 cont=new NLifeNet("LifeNet");
 cont->Default();
 UploadClass("NLifeNet",cont);
 */
}
// --------------------------


}

#endif

