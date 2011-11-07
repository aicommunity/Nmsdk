/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.2.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#include "../../Kernel/NStorage.h"
#include "NPulseNeuronLibrary.h"


namespace NMSDK {

NPulseNeuronLibrary PulseNeuronLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseNeuronLibrary::NPulseNeuronLibrary(void)
 : NLibrary("PulseNeuronLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы создания составных моделей
// --------------------------
// Метод формирования модели простого импульсного нейрона
NPulseNeuron* NPulseNeuronLibrary::CreateSimplePulseNeuron(NStorage *storage, const string &neuronclass, const string &membraneclass, int num_membranes,
                    int num_stimulates, int num_arresting, int dendrite_length)
{
 NAContainer *membr=0;
 NPulseChannel *channel1=0, *channel2=0;
 NPulseNeuron *n=0;
 NPulseLTZone *ltzone=0;
 bool res;
 RDK::ULinkSide item,conn;


 if(!storage)
  return 0;

 n=static_cast<NPulseNeuron*>(storage->TakeObject(neuronclass));
 if(!n)
  return 0;


 ltzone=static_cast<NPulseLTZone*>(storage->TakeObject("NPLTZone"));
 n->AddComponent(ltzone,&n->LTZone);
 ltzone->SetName("LTZone");

 NConstGenerator *gen_pos,*gen_neg;
 gen_pos=static_cast<NConstGenerator*>(storage->TakeObject("NPNeuronPosCGenerator"));
 res=n->AddComponent(gen_pos);
 gen_neg=static_cast<NConstGenerator*>(storage->TakeObject("NPNeuronNegCGenerator"));
 n->AddComponent(gen_neg);

 for(int i=0;i<num_membranes;i++)
 {
  membr=static_cast<NPulseMembrane*>(storage->TakeObject(membraneclass/*"NPNeuronMembrane"*/));
  res=n->AddComponent(membr);

  channel1=static_cast<NPulseChannel*>(membr->GetComponent("PosChannel"));

  channel2=static_cast<NPulseChannel*>(membr->GetComponent("NegChannel"));

  item.Index=0;
  conn.Index=-1;

  // Устанавливаем обратную связь
  item.Id=ltzone->GetLongId(n);
  conn.Id=membr->GetLongId(n);
  res=n->CreateLink(item,conn);

  // Устанавливаем связь генератора с мембраной
  item.Id=channel1->GetLongId(n);
  conn.Id=ltzone->GetLongId(n);
  res=n->CreateLink(item,conn);
  item.Id=channel2->GetLongId(n);
  res=n->CreateLink(item,conn);

  // Связь между начальными значениями мощностей ионных каналов и каналами
  item.Id=gen_neg->GetLongId(n);
  conn.Id=channel1->GetLongId(n);
  res=n->CreateLink(item,conn);

  item.Id=gen_pos->GetLongId(n);
  conn.Id=channel2->GetLongId(n);
  res=n->CreateLink(item,conn);
 }

 for(int i=1;i<dendrite_length;i++)
 {
  membr=static_cast<NPulseMembrane*>(storage->TakeObject(membraneclass/*"NPNeuronMembrane"*/));
  res=n->AddComponent(membr);

  channel1=static_cast<NPulseChannel*>(membr->GetComponent("PosChannel"));

  channel2=static_cast<NPulseChannel*>(membr->GetComponent("NegChannel"));

 }

 NPulseLifeNeuron* lifeneuron=dynamic_cast<NPulseLifeNeuron*>(n);
 if(lifeneuron)
 {
  NNeuronLife *nlife=dynamic_cast<NNeuronLife*>(storage->TakeObject("NNeuronLife"));
  lifeneuron->AddComponent(nlife);

  item.Id=ltzone->GetLongId(n);
  item.Index=0;//1;
  conn.Id=nlife->GetLongId(n);
  conn.Index=0;
  res=n->CreateLink(item,conn);
 }

 if(!res)
  return 0;

 return dynamic_cast<NPulseNeuron*>(n);
}

// Метод формирования модели простого импульсного нейрона с синапсами хебба
NPulseNeuron* NPulseNeuronLibrary::CreateSimplePulseHebbNeuron(NStorage *storage, const string &neuronclass, int num_membranes,
                    int num_stimulates, int num_arresting, int dendrite_length)
{
 NAContainer *membr=0;
 NPulseChannel *channel1=0, *channel2=0;
 NPulseChannel *dchannel1=0, *dchannel2=0;

 NPulseNeuron *n=0;
 NPulseLTZone *ltzone=0;
 bool res;
 RDK::ULinkSide item,conn;
 vector<NPulseHebbSynapse*> synapse_list;

 if(!storage)
  return 0;

 n=static_cast<NPulseNeuron*>(storage->TakeObject(neuronclass));
 if(!n)
  return 0;


 ltzone=static_cast<NPulseLTZone*>(storage->TakeObject("NPLTZone"));
 n->AddComponent(ltzone,&n->LTZone);
 ltzone->SetName("LTZone");

 NConstGenerator *gen_pos,*gen_neg;
 gen_pos=static_cast<NConstGenerator*>(storage->TakeObject("NPNeuronPosCGenerator"));
 res=n->AddComponent(gen_pos);
 gen_neg=static_cast<NConstGenerator*>(storage->TakeObject("NPNeuronNegCGenerator"));
 n->AddComponent(gen_neg);

 synapse_list.clear();
 for(int i=0;i<num_membranes;i++)
 {
  membr=static_cast<NPulseMembrane*>(storage->TakeObject("NPNeuronHebbMembrane"));
  res=n->AddComponent(membr);

  channel1=static_cast<NPulseChannel*>(membr->GetComponent("PosHebbChannel"));

  for(int j=0;j<channel1->GetNumComponents();j++)
   synapse_list.push_back(dynamic_cast<NPulseHebbSynapse*>(channel1->GetComponentByIndex(j)));

  channel2=static_cast<NPulseChannel*>(membr->GetComponent("NegHebbChannel"));

  for(int j=0;j<channel2->GetNumComponents();j++)
   synapse_list.push_back(dynamic_cast<NPulseHebbSynapse*>(channel2->GetComponentByIndex(j)));


  item.Index=0;
  conn.Index=-1;

  // Устанавливаем обратную связь
  item.Id=ltzone->GetLongId(n);
  conn.Id=membr->GetLongId(n);
  res=n->CreateLink(item,conn);

  // Устанавливаем связь генератора с мембраной
  item.Id=channel1->GetLongId(n);
  conn.Id=ltzone->GetLongId(n);
  res=n->CreateLink(item,conn);
  item.Id=channel2->GetLongId(n);
  res=n->CreateLink(item,conn);

  if(dendrite_length == 1 || i != 0)
  {
   // Связь между начальными значениями мощностей ионных каналов и каналами
   item.Id=gen_neg->GetLongId(n);
   conn.Id=channel1->GetLongId(n);
   res=n->CreateLink(item,conn);

   item.Id=gen_pos->GetLongId(n);
   conn.Id=channel2->GetLongId(n);
   res=n->CreateLink(item,conn);
  }

  if(i == 0)
  {
   dchannel1=channel1;
   dchannel2=channel2;
  }
 }

 for(int i=1;i<dendrite_length;i++)
 {
  membr=static_cast<NPulseMembrane*>(storage->TakeObject("NPNeuronHebbMembrane"));
  res=n->AddComponent(membr);

  channel1=static_cast<NPulseChannel*>(membr->GetComponent("PosHebbChannel"));

  for(int j=0;j<channel1->GetNumComponents();j++)
   synapse_list.push_back(dynamic_cast<NPulseHebbSynapse*>(channel1->GetComponentByIndex(j)));


  channel2=static_cast<NPulseChannel*>(membr->GetComponent("NegHebbChannel"));

  for(int j=0;j<channel2->GetNumComponents();j++)
   synapse_list.push_back(dynamic_cast<NPulseHebbSynapse*>(channel2->GetComponentByIndex(j)));

   // Связь между каналами в цепочке
   item.Id=channel1->GetLongId(n);
   conn.Id=dchannel1->GetLongId(n);
   res=n->CreateLink(item,conn);

   item.Id=channel2->GetLongId(n);
   conn.Id=dchannel2->GetLongId(n);
   res=n->CreateLink(item,conn);

   dchannel1=channel1;
   dchannel2=channel2;
 }

 // Связь между начальными значениями мощностей ионных каналов и каналами
 item.Id=gen_neg->GetLongId(n);
 conn.Id=channel1->GetLongId(n);
 res=n->CreateLink(item,conn);

 item.Id=gen_pos->GetLongId(n);
 conn.Id=channel2->GetLongId(n);
 res=n->CreateLink(item,conn);


  // Устанавливаем связь генератора с синапсами хебба
  item.Id=ltzone->GetLongId(n);
  item.Index=0;
  conn.Index=1;
  for(size_t j=0;j<synapse_list.size();j++)
  {
   if(synapse_list[j])
   {
    conn.Id=synapse_list[j]->GetLongId(n);
    res=n->CreateLink(item,conn);
   }
  }

 NPulseLifeNeuron* lifeneuron=dynamic_cast<NPulseLifeNeuron*>(n);
 if(lifeneuron)
 {
  NNeuronLife *nlife=dynamic_cast<NNeuronLife*>(storage->TakeObject("NNeuronLife"));
  lifeneuron->AddComponent(nlife);

  item.Id=ltzone->GetLongId(n);
  item.Index=0;//1;
  conn.Id=nlife->GetLongId(n);
  conn.Index=0;
  res=n->CreateLink(item,conn);
 }

 if(!res)
  return 0;

 return dynamic_cast<NPulseNeuron*>(n);
}

// Метод формирования модели афферентного нейрона
NAfferentNeuron* NPulseNeuronLibrary::CreateAfferentNeuron(NStorage *storage, int num_membranes)
{
 NAContainer *membr=0;
 NPulseChannel *channel1=0, *channel2=0;
 NAfferentNeuron *n=0;
 NPulseLTZone *ltzone=0;
 NReceptor *receptor=0;
 bool res;
 RDK::ULinkSide item,conn;

 item.Index=0;
 conn.Index=-1;

 if(!storage)
  return 0;

 n=static_cast<NAfferentNeuron*>(storage->TakeObject("NAfferentNeuron"));
 if(!n)
  return 0;

 ltzone=static_cast<NPulseLTZone*>(storage->TakeObject("NPLTZone"));
 n->AddComponent(ltzone,&n->LTZone);
 ltzone->SetName("LTZone");
 ltzone->Threshold=0;

 NConstGenerator *gen_pos,*gen_neg;
 gen_pos=static_cast<NConstGenerator*>(storage->TakeObject("NPNeuronPosCGenerator"));
 res=n->AddComponent(gen_pos);
 gen_neg=static_cast<NConstGenerator*>(storage->TakeObject("NPNeuronNegCGenerator"));
 n->AddComponent(gen_neg);

 bool linkres=true;
 for(int i=0;i<num_membranes;i++)
 {
  membr=static_cast<NPulseMembrane*>(storage->TakeObject("NPNeuronMembrane"));
  res=n->AddComponent(membr);

  receptor=static_cast<NReceptor*>(storage->TakeObject("NReceptor"));
  receptor->ExpCoeff=0.01;
  receptor->Gain=1;
  res=n->AddComponent(receptor);

  channel1=static_cast<NPulseChannel*>(membr->GetComponent("PosChannel"));//(storage->TakeObject("NPChannel"));
//  channel1->SetNumInputs(2);

  channel2=static_cast<NPulseChannel*>(membr->GetComponent("NegChannel"));//(storage->TakeObject("NPChannel"));
  // Устанавливаем обратную связь
  item.Id=ltzone->GetLongId(n);
  conn.Id=membr->GetLongId(n);
  linkres&=n->CreateLink(item,conn);

  // Устанавливаем связь генератора с мембраной
  item.Id=channel1->GetLongId(n);
  conn.Id=ltzone->GetLongId(n);
  linkres&=n->CreateLink(item,conn);
  item.Id=channel2->GetLongId(n);
//  conn.Index=1;
  linkres&=res=n->CreateLink(item,conn);
//  conn.Index=0;

  // Связь между начальными значениями мощностей ионных каналов и каналами
  item.Id=gen_neg->GetLongId(n);
  conn.Id=channel1->GetLongId(n);
  conn.Index=0;
  linkres&=n->CreateLink(item,conn);

  item.Id=receptor->GetLongId(n);
  conn.Id=channel2->GetLongId(n);
  conn.Index=0;
  linkres&=n->CreateLink(item,conn);

//  item.Id=gen_pos->GetLongId(n);
//  conn.Id=channel2->GetLongId(n);
//  linkres=n->CreateLink(item,conn);
 }

 if(!linkres)
  return 0;

 if(!res)
  return 0;

 return dynamic_cast<NAfferentNeuron*>(n);
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NPulseNeuronLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont=0;

 // Содержимое старой библиотеки PulseItemsLibrary
 cont=storage->TakeObject("NCGenerator");
 cont->SetName("PNeuronNegCGenerator");
 ((NConstGenerator*)cont)->Amplitude=-1;
 UploadClass("NPNeuronNegCGenerator",cont);

 cont=storage->TakeObject("NCGenerator");
 cont->SetName("PNeuronPosCGenerator");
 ((NConstGenerator*)cont)->Amplitude=1;
 UploadClass("NPNeuronPosCGenerator",cont);

 // Формируем обычные синапсы и участки мембраны с ними
 NPulseSynapse *s_pos;
 NPulseChannel *ch_pos, *ch_neg;
 ch_pos=(NPulseChannel*)storage->TakeObject("NPChannel");
 ch_pos->SetName("PNeuronChannel");
 for(int i=0;i<3;i++)
 {
  s_pos=(NPulseSynapse*)storage->TakeObject("NPSynapse");
  s_pos->SetName("Synapse");
  ch_pos->AddComponent(s_pos);
 }
 UploadClass("NPNeuronChannel",ch_pos);

 ch_pos=(NPulseChannel*)storage->TakeObject("NPSynChannel");
 ch_pos->SetName("PNeuronChannel");
 UploadClass("NPSynNeuronChannel",ch_pos);

 cont=storage->TakeObject("NPMembrane");
 cont->SetName("PNeuronMembrane");
 ch_pos=(NPulseChannel*)storage->TakeObject("NPNeuronChannel");
 ch_pos->SetName("PosChannel");
 ch_pos->Type=-1;

 ch_neg=(NPulseChannel*)storage->TakeObject("NPNeuronChannel");
 ch_neg->SetName("NegChannel");
 ch_neg->Type=1;
 cont->AddComponent(ch_pos);
 cont->AddComponent(ch_neg);
 UploadClass("NPNeuronMembrane",cont);

 cont=storage->TakeObject("NPMembrane");
 cont->SetName("PNeuronMembrane");
 ch_pos=(NPulseChannel*)storage->TakeObject("NPSynNeuronChannel");
 ch_pos->SetName("PosChannel");
 ch_pos->Type=-1;

 ch_neg=(NPulseChannel*)storage->TakeObject("NPSynNeuronChannel");
 ch_neg->SetName("NegChannel");
 ch_neg->Type=1;
 cont->AddComponent(ch_pos);
 cont->AddComponent(ch_neg);
 UploadClass("NPSynNeuronMembrane",cont);

 // Формируем синапсы хебба и участки мембраны с ними
 NPulseHebbSynapse *hs_pos;
 ch_pos=(NPulseChannel*)storage->TakeObject("NPChannel");
 ch_pos->SetName("PNeuronHebbChannel");
 for(int i=0;i<1;i++)
 {
  hs_pos=(NPulseHebbSynapse*)storage->TakeObject("NPHebbSynapse");
  hs_pos->SetName("HebbSynapse");
  ch_pos->AddComponent(hs_pos);
 }
 UploadClass("NPNeuronHebbChannel",ch_pos);

 cont=storage->TakeObject("NPMembrane");
 cont->SetName("PNeuronHebbMembrane");
 ch_pos=(NPulseChannel*)storage->TakeObject("NPNeuronHebbChannel");
 ch_pos->SetName("PosHebbChannel");
 ch_pos->Type=-1;

 ch_neg=(NPulseChannel*)storage->TakeObject("NPNeuronHebbChannel");
 ch_neg->SetName("NegHebbChannel");
 ch_neg->Type=1;
 cont->AddComponent(ch_pos);
 cont->AddComponent(ch_neg);

 UploadClass("NPNeuronHebbMembrane",cont);

 // Модель мышцы
 cont=storage->TakeObject("NMuscle");

 NReceptor *input;
 input=dynamic_cast<NReceptor*>(storage->TakeObject("NReceptor"));
 input->SetName("LengthInput");
 cont->AddComponent(input);

 cont->SetName("SMuscle");
 UploadClass("NSMuscle",cont);

 // Создаем мелкий нейрон
 NPulseNeuron *n=CreateSimplePulseNeuron(storage,"NPNeuron","NPNeuronMembrane",1,5,5);
 n->SetName("SPNeuron");
 UploadClass("NSPNeuron",n);

 // Создаем крупный нейрон
 n=CreateSimplePulseNeuron(storage,"NPNeuron","NPNeuronMembrane",3,1,1);
 n->SetName("LPNeuron");
 UploadClass("NLPNeuron",n);

 // Создаем мотонейрон
 n=CreateSimplePulseNeuron(storage,"NPNeuron","NPNeuronMembrane",3,10,10);
 n->SetName("Motoneuron");
 UploadClass("NMotoneuron",n);

 // Создаем клетку реншоу
 n=CreateSimplePulseNeuron(storage,"NPNeuron","NPNeuronMembrane",1,5,5);
 n->SetName("RenshowCell");
 UploadClass("NRenshowCell",n);

 // Нейроны с оптимизированными синапсами
 // Создаем мелкий нейрон
 n=CreateSimplePulseNeuron(storage,"NPNeuron","NPSynNeuronMembrane",1,5,5);
 n->SetName("SPNeuron");
 UploadClass("NSynSPNeuron",n);

 // Создаем крупный нейрон
 n=CreateSimplePulseNeuron(storage,"NPNeuron","NPSynNeuronMembrane",3,1,1);
 n->SetName("LPNeuron");
 UploadClass("NSynLPNeuron",n);

 // Создаем мотонейрон
 n=CreateSimplePulseNeuron(storage,"NPNeuron","NPSynNeuronMembrane",3,10,10);
 n->SetName("Motoneuron");
 UploadClass("NSynMotoneuron",n);

 // Создаем клетку реншоу
 n=CreateSimplePulseNeuron(storage,"NPNeuron","NPSynNeuronMembrane",1,5,5);
 n->SetName("RenshowCell");
 UploadClass("NSynRenshowCell",n);
 // Конец нейронов с оптимизирванными синапсами

 // Создаем мелкий нейрон с синапсами хебба
 n=CreateSimplePulseHebbNeuron(storage,"NPNeuron",1,1,1);
 n->SetName("SPHebbNeuron");
 UploadClass("NSPHebbNeuron",n);

 // Создаем крупный нейрон с синапсами хебба
 n=CreateSimplePulseHebbNeuron(storage,"NPNeuron",3,1,1);
 n->SetName("LPHebbNeuron");
 UploadClass("NLPHebbNeuron",n);

 // Создаем мелкий живой нейрон
 n=CreateSimplePulseNeuron(storage,"NPLifeNeuron","NPNeuronMembrane",1,1,1);
 n->SetName("SPLifeNeuron");
 UploadClass("NSPLifeNeuron",n);


 // Создаем крупный живой нейрон
 n=CreateSimplePulseNeuron(storage,"NPLifeNeuron","NPNeuronMembrane",3,1,1);
 n->SetName("LPLifeNeuron");
 UploadClass("NLPLifeNeuron",n);

 // Создаем мелкий живой нейрон с синапсами хебба
 n=CreateSimplePulseHebbNeuron(storage,"NPLifeNeuron",1,1,1);
 n->SetName("SPLifeHebbNeuron");
 UploadClass("NSPLifeHebbNeuron",n);

 // Создаем мелкий живой нейрон с синапсами хебба и дендритом
 n=CreateSimplePulseHebbNeuron(storage,"NPLifeNeuron",1,1,1,4);
 n->SetName("SPDendriteLifeHebbNeuron");
 UploadClass("NSPDendriteLifeHebbNeuron",n);

 // Создаем крупный живой нейрон с синапсами хебба
 n=CreateSimplePulseHebbNeuron(storage,"NPLifeNeuron",3,1,1);
 n->SetName("LPLifeHebbNeuron");
 UploadClass("NLPLifeHebbNeuron",n);

 // Создаем афферентный нейрон
 NAfferentNeuron *an=CreateAfferentNeuron(storage,1);
 an->SetName("AfferentNeuron");
 UploadClass("NSAfferentNeuron",an);
}
// --------------------------


}
