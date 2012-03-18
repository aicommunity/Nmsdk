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

#include "NMotionControlLibrary.h"

#include "NMotionElement.cpp"
#include "NEngineMotionControl.cpp"

namespace NMSDK {

NMotionControlLibrary MotionControlLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NMotionControlLibrary::NMotionControlLibrary(void)
 : NLibrary("MotionControlLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы создания составных моделей
// --------------------------
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NMotionControlLibrary::ACreateClassSamples(NStorage *storage)
{
 // Создаем СУ двигательной единицей
 UEPtr<NANet> net=CreateMotionElement(storage, "NNet",0);
 net->SetName("MotionElement");
 UploadClass("NMotionElement",net);

 // Создаем СУ двигательной единицей без вставочных интернейронов
 net=CreateMotionElement(storage, "NNet",1);
 net->SetName("SimpleMotionElement");
 UploadClass("NSimpleMotionElement",net);

 // Создаем СУ с ветвлением
 net=CreateBranchedMotionElement(storage, "NNet",0);
 net->SetName("MotionElement");
 UploadClass("NBranchedMotionElement",net);

 // Создаем СУ с ветвлением без вставочных интернейронов
 net=CreateBranchedMotionElement(storage, "NNet",1);
 net->SetName("MotionElement");
 UploadClass("NSimpleBranchedMotionElement",net);

 // Создаем прототип систем управления
 UEPtr<NEngineMotionControl> cs=0;
 cs=new NEngineMotionControl;
 cs->Default();
 cs->SetName("EngineMotionControl");
 UploadClass("NEngineMotionControl",cs);


// pair<real,real> Ia(-2.0*M_PI,2.0*M_PI);
// pair<real,real> Ib(-10,10);
// pair<real,real> II(-M_PI/2,M_PI/2);
 size_t max_number_of_mc=1;

 // Формируем сеть управления двигателем с разделением информационного потока с датчиков
 // на две полосы по знаку
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=0;
  cs->MotionElementClassName="NMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlSignumAfferent(storage, "NNet", "NMotionElement",i+1);
  net->SetName("EngineControlSignumAfferent");
  if(i>0)
   UploadClass(string("NEngineControlSignumAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass(string("NEngineControlSignumAfferent"),net);
 }

 // Формируем сеть управления двигателем c разделением информационного потока с датчиков
 // на полосы по амплитуде
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=1;
  cs->MotionElementClassName="NMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlRangeAfferent(storage, "NNet", "NMotionElement",
//   Ia,Ib,II,i+1);
  net->SetName("EngineControlRangeAfferent");
  if(i>0)
   UploadClass(string("NEngineControlRangeAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass("NEngineControlRangeAfferent",net);
 }

 // Формируем сеть управления двигателем с разделением информационного потока с датчиков
 // на две полосы по знаку
 // используется двигательная единица без вставочных интернейронов
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=0;
  cs->MotionElementClassName="NSimpleMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlSignumAfferent(storage, "NNet", "NSimpleMotionElement",i+1);
  net->SetName("SimpleEngineControlSignumAfferent");
  if(i>0)
   UploadClass(string("NSimpleEngineControlSignumAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass("NSimpleEngineControlSignumAfferent",net);
 }

 // Формируем сеть управления двигателем c разделением информационного потока с датчиков
 // на полосы по амплитуде
 // используется двигательная единица без вставочных интернейронов
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=1;
  cs->MotionElementClassName="NSimpleMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlRangeAfferent(storage, "NNet", "NSimpleMotionElement",
//  Ia,Ib,II,i+1);
  net->SetName("SimpleEngineControlRangeAfferent");
  if(i>0)
   UploadClass(string("NSimpleEngineControlRangeAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass("NSimpleEngineControlRangeAfferent",net);
 }


 // Формируем сеть управления двигателем c разделением информационного потока с датчиков
 // на полосы по амплитуде
 // Автоматическое формирование нейронов
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=2;
  cs->MotionElementClassName="NBranchedMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlRangeAfferent(storage, "NNet", "NBranchedMotionElement",
//   Ia,Ib,II,i+1);
  net->SetName("EngineControlRangeAfferent");
  if(i>0)
   UploadClass(string("NBranchedEngineControlRangeAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass("NBranchedEngineControlRangeAfferent",net);
 }

 // Формируем сеть управления двигателем c разделением информационного потока с датчиков
 // на полосы по амплитуде
 // используется двигательная единица без вставочных интернейронов
 // Автоматическое формирование нейронов
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=2;
  cs->MotionElementClassName="NSimpleBranchedMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlRangeAfferent(storage, "NNet", "NSimpleBranchedMotionElement",
//  Ia,Ib,II,i+1);
  net->SetName("SimpleEngineControlRangeAfferent");
  if(i>0)
   UploadClass(string("NSimpleBranchedEngineControlRangeAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass("NSimpleBranchedEngineControlRangeAfferent",net);
 }

 // Формируем сеть управления двигателем c разделением информационного потока с датчиков
 // на полосы по амплитуде
 // Автоматическое формирование нейронов
 // Перекрестные связи
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=3;
  cs->MotionElementClassName="NBranchedMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlRangeAfferent(storage, "NNet", "NBranchedMotionElement",
//   Ia,Ib,II,i+1,true);
  net->SetName("EngineControlRangeAfferent");
  if(i>0)
   UploadClass(string("NBranchedCrosslinksEngineControlRangeAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass("NBranchedCrosslinksEngineControlRangeAfferent",net);
 }

 // Формируем сеть управления двигателем c разделением информационного потока с датчиков
 // на полосы по амплитуде
 // используется двигательная единица без вставочных интернейронов
 // Автоматическое формирование нейронов
 // Перекрестные связи
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=3;
  cs->MotionElementClassName="NSimpleBranchedMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlRangeAfferent(storage, "NNet", "NSimpleBranchedMotionElement",
//  Ia,Ib,II,i+1,true);
  net->SetName("SimpleEngineControlRangeAfferent");
  if(i>0)
   UploadClass(string("NSimpleBranchedCrosslinksEngineControlRangeAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass("NSimpleBranchedCrosslinksEngineControlRangeAfferent",net);
 }


 // Формируем сеть управления двигателем c разделением информационного потока с датчиков
 // на полосы по амплитуде
 // Автоматическое формирование нейронов
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=4;
  cs->MotionElementClassName="NBranchedMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlRangeAfferent(storage, "NNet", "NBranchedMotionElement",
//   Ia,Ib,II,i+1,false,false);
  net->SetName("EngineControlRangeAfferent");
  if(i>0)
   UploadClass(string("NIndRangeBranchedEngineControlRangeAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass("NIndRangeBranchedEngineControlRangeAfferent",net);
 }

 // Формируем сеть управления двигателем c разделением информационного потока с датчиков
 // на полосы по амплитуде без пересекающихся диапазонов
 // Автоматическое формирование нейронов
 // Перекрестные связи
 for(size_t i=0;i<max_number_of_mc;i++)
 {
  cs=dynamic_pointer_cast<NEngineMotionControl>(storage->TakeObject("NEngineMotionControl"));
  cs->NumMotionElements=i+1;
  cs->CreationMode=5;
  cs->MotionElementClassName="NBranchedMotionElement";
  cs->Create();
  net=cs;

//  net=CreateEngineControlRangeAfferent(storage, "NNet", "NBranchedMotionElement",
//   Ia,Ib,II,i+1,true,false);
  net->SetName("EngineControlRangeAfferent");
  if(i>0)
   UploadClass(string("NIndRangeBranchedCrosslinksEngineControlRangeAfferent")+RDK::sntoa(i+1),net);
  else
   UploadClass("NIndRangeBranchedCrosslinksEngineControlRangeAfferent",net);
 }


}
// --------------------------


}
