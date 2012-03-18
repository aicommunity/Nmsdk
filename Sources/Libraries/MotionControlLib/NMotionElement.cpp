/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		1.0.0

This file - part of the project: NMSDK

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */
#ifndef NMotionElementCPP
#define NMotionElementCPP

#include "NMotionElement.h"
#include "../PulseLib/NPulseNeuron.h"
#include "../PulseLib/NAfferentNeuron.h"
#include "../../Kernel/NStorage.h"
//---------------------------------------------------------------------------
namespace NMSDK {

// Формирует СУ двигательной единицей
UEPtr<NANet> CreateMotionElement(NStorage *storage, const string &netclassname, int mode)
{
 UEPtr<NAContainer> cont;
 bool res;

 UEPtr<NANet> net=RDK::dynamic_pointer_cast<NANet>(storage->TakeObject(netclassname));
 if(!net)
  return 0;

 // Клетка реншоу 1
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynRenshowCell"));
 if(!cont)
  return 0;
 cont->SetName("Renshow1");
 res=net->AddComponent(cont);

 // Клетка реншоу 2
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynRenshowCell"));
 if(!cont)
  return 0;
 cont->SetName("Renshow2");
 res=net->AddComponent(cont);

 // Мотонейрон 1
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynMotoneuron"));
 if(!cont)
  return 0;
 cont->SetName("Motoneuron1");
 res=net->AddComponent(cont);

 // Мотонейрон 2
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynMotoneuron"));
 if(!cont)
  return 0;
 cont->SetName("Motoneuron2");
 res=net->AddComponent(cont);

 // Постафферентные нейроны
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent11");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent12");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent13");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent14");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent21");
 res=net->AddComponent(cont);


 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent22");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent23");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent24");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ia1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ia2");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ib1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ib2");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_II1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_II2");
 res=net->AddComponent(cont);

 // Установка связей
 ULongId item,conn;

 res=net->CreateLink("Afferent_Ia1.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.PosChannel");

 res=net->CreateLink("Afferent_Ia1.LTZone",0,
				 "PostAfferent11.PNeuronMembrane.PosChannel");

 res=net->CreateLink("Afferent_Ia2.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.PosChannel");

 res=net->CreateLink("Afferent_Ia2.LTZone",0,
				 "PostAfferent21.PNeuronMembrane.PosChannel");

 res=net->CreateLink("PostAfferent11.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.NegChannel");

 res=net->CreateLink("PostAfferent21.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel");

 res=net->CreateLink("Motoneuron1.LTZone",0,
				 "Renshow1.PNeuronMembrane.PosChannel");

 res=net->CreateLink("Renshow1.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel");

 res=net->CreateLink("Renshow1.LTZone",0,
				 "PostAfferent11.PNeuronMembrane.NegChannel");

 res=net->CreateLink("Motoneuron2.LTZone",0,
				 "Renshow2.PNeuronMembrane.PosChannel");

 res=net->CreateLink("Renshow2.LTZone",0,
 				 "Motoneuron2.PNeuronMembrane.NegChannel");

 res=net->CreateLink("Renshow2.LTZone",0,
				 "PostAfferent21.PNeuronMembrane.NegChannel");

 switch(mode)
 {
 case 0:
  // Канал Ib
  res=net->CreateLink("Afferent_Ib1.LTZone",0,
				 "PostAfferent12.PNeuronMembrane.PosChannel");

  res=net->CreateLink("Afferent_Ib1.LTZone",0,
				 "PostAfferent13.PNeuronMembrane.PosChannel");

  res=net->CreateLink("PostAfferent12.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.PosChannel");

  res=net->CreateLink("PostAfferent13.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel");

  res=net->CreateLink("Afferent_Ib2.LTZone",0,
				 "PostAfferent22.PNeuronMembrane.PosChannel");

  res=net->CreateLink("Afferent_Ib2.LTZone",0,
				 "PostAfferent23.PNeuronMembrane.PosChannel");

  res=net->CreateLink("PostAfferent22.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.PosChannel");

  res=net->CreateLink("PostAfferent23.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.NegChannel");

  // Канал II
  res=net->CreateLink("Afferent_II1.LTZone",0,
				 "PostAfferent14.PNeuronMembrane.PosChannel");

  res=net->CreateLink("PostAfferent14.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel");
  res=net->CreateLink("PostAfferent14.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.PosChannel");

  res=net->CreateLink("Afferent_II2.LTZone",0,
				 "PostAfferent24.PNeuronMembrane.PosChannel");

  res=net->CreateLink("PostAfferent24.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.NegChannel");
  res=net->CreateLink("PostAfferent24.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.PosChannel");
 break;

 case 1:
  // Варинат канала b без промежуточных нейронов
  res=net->CreateLink("Afferent_Ib1.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.PosChannel");

  res=net->CreateLink("Afferent_Ib1.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel");

  res=net->CreateLink("Afferent_Ib2.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.PosChannel");

  res=net->CreateLink("Afferent_Ib2.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.NegChannel");

  // Варинат канала II без промежуточных нейронов
  res=net->CreateLink("Afferent_II1.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel");

  res=net->CreateLink("Afferent_II1.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.PosChannel");

  res=net->CreateLink("Afferent_II2.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.NegChannel");

  res=net->CreateLink("Afferent_II2.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.PosChannel");
 break;
 }

 if(!res)
  res=true;

 return net;
}

bool CreateNeuronBranchLink(UEPtr<NANet> net,const string &source,
	const string &target_head, const string &target_tail)
{
 string tmpname;
 UEPtr<NPulseNeuron> neuron=dynamic_pointer_cast<NPulseNeuron>(net->GetComponent(target_head));
 UEPtr<NPulseMembrane> branch;
 UEPtr<NPulseChannel> channel;
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_pointer_cast<NPulseChannel>(branch->GetComponentL(target_tail));
 bool res=net->CreateLink(source,0,
				 channel->GetLongName(net,tmpname));
 return res;
}

// Формирует СУ двигательной единицей
// Аналогично, но с развязкой по дендритам
UEPtr<NANet> CreateBranchedMotionElement(NStorage *storage, const string &netclassname, int mode)
{
 UEPtr<NAContainer> cont;
 bool res;

 UEPtr<NANet> net=dynamic_pointer_cast<NANet>(storage->TakeObject(netclassname));
 if(!net)
  return 0;

 // Клетка реншоу 1
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Renshow1");
 res=net->AddComponent(cont);

 // Клетка реншоу 2
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Renshow2");
 res=net->AddComponent(cont);

 // Мотонейрон 1
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Motoneuron1");
 res=net->AddComponent(cont);

 // Мотонейрон 2
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Motoneuron2");
 res=net->AddComponent(cont);

 // Постафферентные нейроны
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent11");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent12");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent13");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent14");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent21");
 res=net->AddComponent(cont);


 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent22");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent23");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSynSPNeuron"));
 if(!cont)
  return 0;
 cont->SetName("PostAfferent24");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ia1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ia2");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ib1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ib2");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_II1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NSAfferentNeuron"));
 if(!cont)
  return 0;
 cont->SetName("Afferent_II2");
 res=net->AddComponent(cont);

 // Установка связей
 ULongId item,conn;
 NameT tmpname;
 res=true;

 CreateNeuronBranchLink(net,"Afferent_Ia1.LTZone","Motoneuron1", "PosChannel");
/* NPulseNeuron* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
 NPulseMembrane* branch=0;
// NPulseSynapse* synapse=0;
 NPulseChannel* channel=0;
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Afferent_Ia1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"Afferent_Ia1.LTZone","PostAfferent11", "PosChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent11"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Afferent_Ia1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */

 CreateNeuronBranchLink(net,"Afferent_Ia2.LTZone","Motoneuron2", "PosChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Afferent_Ia2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"Afferent_Ia2.LTZone","PostAfferent21", "PosChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent21"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Afferent_Ia2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"PostAfferent11.LTZone","Motoneuron2", "NegChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("PostAfferent11.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"PostAfferent21.LTZone","Motoneuron1", "NegChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("PostAfferent21.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"Motoneuron1.LTZone","Renshow1", "PosChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Renshow1"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Motoneuron1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"Renshow1.LTZone","Motoneuron1", "NegChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("Renshow1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"Renshow1.LTZone","PostAfferent11", "NegChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent11"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("Renshow1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"Motoneuron2.LTZone","Renshow2", "PosChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Renshow2"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Motoneuron2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"Renshow2.LTZone","Motoneuron2", "NegChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("Renshow2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 CreateNeuronBranchLink(net,"Renshow2.LTZone","PostAfferent21", "NegChannel");
/* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent21"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("Renshow2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
 string name;
 switch(mode)
 {
 case 0:
  // Канал Ib
  CreateNeuronBranchLink(net,"Afferent_Ib1.LTZone","PostAfferent12", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent12"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"PostAfferent12.LTZone","Motoneuron2", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("PostAfferent12.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"PostAfferent12.LTZone","Motoneuron1", "NegChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("PostAfferent12.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"Afferent_Ib2.LTZone","PostAfferent22", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent22"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib2.LTZone",0,
				 channel->GetLongName(net,tmpname));*/

  CreateNeuronBranchLink(net,"PostAfferent22.LTZone","Motoneuron1", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("PostAfferent22.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"PostAfferent22.LTZone","Motoneuron2", "NegChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("PostAfferent22.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */

  // Канал II
  CreateNeuronBranchLink(net,"Afferent_II1.LTZone","PostAfferent14", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent14"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_II1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"PostAfferent14.LTZone","Motoneuron1", "NegChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("PostAfferent14.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"PostAfferent14.LTZone","Motoneuron2", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("PostAfferent14.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"Afferent_II2.LTZone","PostAfferent24", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent24"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_II2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */

  CreateNeuronBranchLink(net,"PostAfferent24.LTZone","Motoneuron2", "NegChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("PostAfferent24.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"PostAfferent24.LTZone","Motoneuron1", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("PostAfferent24.LTZone",0,
				 channel->GetLongName(net,tmpname));*/
 break;

 case 1:
  // Варинат канала b без промежуточных нейронов
  CreateNeuronBranchLink(net,"Afferent_Ib1.LTZone","Motoneuron2", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"Afferent_Ib1.LTZone","Motoneuron1", "NegChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("Afferent_Ib1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"Afferent_Ib2.LTZone","Motoneuron1", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"Afferent_Ib2.LTZone","Motoneuron2", "NegChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("Afferent_Ib2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  // Варинат канала II без промежуточных нейронов
  CreateNeuronBranchLink(net,"Afferent_II1.LTZone","Motoneuron1", "NegChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("Afferent_II1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"Afferent_II1.LTZone","Motoneuron2", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_II1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"Afferent_II2.LTZone","Motoneuron2", "NegChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("Afferent_II2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  CreateNeuronBranchLink(net,"Afferent_II2.LTZone","Motoneuron1", "PosChannel");
/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_II2.LTZone",0,
				 channel->GetLongName(net,tmpname));*/
 break;
 }

 if(!res)
  res=true;

 return net;
}

}
//---------------------------------------------------------------------------
#endif
