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
NANet* CreateMotionElement(NStorage *storage, const string &netclassname, int mode)
{
 NAContainer *cont;
 bool res;

 NANet *net=dynamic_cast<NANet*>(storage->TakeObject(netclassname));
 if(!net)
  return 0;

 // Клетка реншоу 1
 cont=storage->TakeObject("NSynRenshowCell");
 if(!cont)
  return 0;
 cont->SetName("Renshow1");
 res=net->AddComponent(cont);

 // Клетка реншоу 2
 cont=storage->TakeObject("NSynRenshowCell");
 if(!cont)
  return 0;
 cont->SetName("Renshow2");
 res=net->AddComponent(cont);

 // Мотонейрон 1
 cont=storage->TakeObject("NSynMotoneuron");
 if(!cont)
  return 0;
 cont->SetName("Motoneuron1");
 res=net->AddComponent(cont);

 // Мотонейрон 2
 cont=storage->TakeObject("NSynMotoneuron");
 if(!cont)
  return 0;
 cont->SetName("Motoneuron2");
 res=net->AddComponent(cont);

 // Постафферентные нейроны
 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent11");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent12");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent13");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent14");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent21");
 res=net->AddComponent(cont);


 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent22");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent23");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent24");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ia1");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ia2");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ib1");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ib2");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_II1");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
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


// Формирует СУ двигательной единицей
// Аналогично, но с развязкой по дендритам
NANet* CreateBranchedMotionElement(NStorage *storage, const string &netclassname, int mode)
{
 NAContainer *cont;
 bool res;

 NANet *net=dynamic_cast<NANet*>(storage->TakeObject(netclassname));
 if(!net)
  return 0;

 // Клетка реншоу 1
 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("Renshow1");
 res=net->AddComponent(cont);

 // Клетка реншоу 2
 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("Renshow2");
 res=net->AddComponent(cont);

 // Мотонейрон 1
 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("Motoneuron1");
 res=net->AddComponent(cont);

 // Мотонейрон 2
 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("Motoneuron2");
 res=net->AddComponent(cont);

 // Постафферентные нейроны
 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent11");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent12");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent13");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent14");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent21");
 res=net->AddComponent(cont);


 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent22");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent23");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSynSPNeuron");
 if(!cont)
  return 0;
 cont->SetName("PostAfferent24");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ia1");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ia2");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ib1");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_Ib2");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_II1");
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return 0;
 cont->SetName("Afferent_II2");
 res=net->AddComponent(cont);

 // Установка связей
 ULongId item,conn;
 NameT tmpname;
 res=true;

 NPulseNeuron* neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
 NPulseMembrane* branch=0;
// NPulseSynapse* synapse=0;
 NPulseChannel* channel=0;
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Afferent_Ia1.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent11"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Afferent_Ia1.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Afferent_Ia2.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent21"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Afferent_Ia2.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("PostAfferent11.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("PostAfferent21.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Renshow1"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Motoneuron1.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("Renshow1.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent11"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("Renshow1.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Renshow2"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
 res&=net->CreateLink("Motoneuron2.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("Renshow2.LTZone",0,
				 channel->GetLongName(net,tmpname));

 neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent21"));
 branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
 channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
 res&=net->CreateLink("Renshow2.LTZone",0,
				 channel->GetLongName(net,tmpname));

 string name;
 switch(mode)
 {
 case 0:
  // Канал Ib
  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent12"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib1.LTZone",0,
				 channel->GetLongName(net,tmpname));

/*  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent13"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib1.LTZone",0,
				 channel->GetLongName(net,tmpname));
  */
  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("PostAfferent12.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("PostAfferent12.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent22"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib2.LTZone",0,
				 channel->GetLongName(net,tmpname));
  /*
  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent23"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib2.LTZone",0,
				 channel->GetLongName(net,tmpname));
	 */
  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("PostAfferent22.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("PostAfferent22.LTZone",0,
				 channel->GetLongName(net,tmpname));


  // Канал II
  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent14"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_II1.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("PostAfferent14.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("PostAfferent14.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("PostAfferent24"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_II2.LTZone",0,
				 channel->GetLongName(net,tmpname));


  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("PostAfferent24.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("PostAfferent24.LTZone",0,
				 channel->GetLongName(net,tmpname));
 break;

 case 1:
  // Варинат канала b без промежуточных нейронов
  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib1.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("Afferent_Ib1.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_Ib2.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("Afferent_Ib2.LTZone",0,
				 channel->GetLongName(net,tmpname));

  // Варинат канала II без промежуточных нейронов
  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("Afferent_II1.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_II1.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron2"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("NegChannel"));
  res&=net->CreateLink("Afferent_II2.LTZone",0,
				 channel->GetLongName(net,tmpname));

  neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
  branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
  channel=dynamic_cast<NPulseChannel*>(branch->GetComponentL("PosChannel"));
  res&=net->CreateLink("Afferent_II2.LTZone",0,
				 channel->GetLongName(net,tmpname));
 break;
 }

 if(!res)
  res=true;

 return net;
}

}
//---------------------------------------------------------------------------
#endif
