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

#include "NSourceLibrary.h"

/*
#include "NConstGenerator.cpp"
#include "NFileGenerator.cpp"
#include "NPulseGenerator.cpp"
#include "NSinusGenerator.cpp"
#include "NManipulatorSourceEmulator.cpp"
#include "NManipulatorSource.cpp"
#include "NControlObjectSource.cpp"
  */
namespace NMSDK {

NSourceLibrary NeuronSourceLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NSourceLibrary::NSourceLibrary(void)
 : ULibrary("NeuronSourceLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NSourceLibrary::CreateClassSamples(UStorage *storage)
{
 UContainer *cont;

 cont=new NPulseGenerator;
 cont->SetName("PGenerator");
 cont->Default();
 UploadClass("NPGenerator",cont);

 cont=new NConstGenerator;
 cont->SetName("CGenerator");
 cont->Default();
 UploadClass("NCGenerator",cont);

 cont=new NSinusGenerator;
 cont->SetName("SinusGenerator");
 cont->Default();
 UploadClass("NSinusGenerator",cont);

 cont=new NFileGenerator;
 cont->SetName("FileGenerator");
 cont->Default();
 UploadClass("NFileGenerator",cont);

 cont=new NManipulatorSourceEmulator;
 cont->SetName("ManipulatorSourceEmulator");
 cont->Default();
 UploadClass("NManipulatorSourceEmulator",cont);

 cont=new NManipulatorSource;
 cont->SetName("ManipulatorSource");
 cont->Default();
 UploadClass("NManipulatorSource",cont);  
 
 cont=new NControlObjectSource;
 cont->SetName("ManipulatorSource");
 cont->Default();
 UploadClass("NControlObjectSource",cont);  
 
 
}
// --------------------------


}
