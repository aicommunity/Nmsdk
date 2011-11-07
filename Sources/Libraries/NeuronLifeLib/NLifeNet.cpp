// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NLIFE_NET_CPP
#define NLIFE_NET_CPP

#include "NLifeNet.h"
#include "../PulseLib/NPulseMembrane.h"
#include "../PulseLib/NPulseLTZone.h"
#include "../PulseLib/NPulseChannel.h"
#include <algorithm>

namespace NMSDK {


// ------------------------
// Операторы
// ------------------------
bool NEnsembleLink::operator < (const NEnsembleLink &link)
{
 return (Power<link.Power);
}
// ------------------------


// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NLifeNet::NLifeNet(void)
//: NNet(name),
 : AvailableEnergy("AvailableEnergy",this),
  CellDivisionFlag("CellDivisionFlag",this),
  CellDivisionEnergy("CellDivisionEnergy",this),
  EnsembleThreshold("EnsembleThreshold",this),
  EnsembleLinkThreshold("EnsembleLinkThreshold",this),
  EnsembleThresholdMode("EnsembleThresholdMode",this),
  EnsembleCalculationStep("EnsembleCalculationStep",this),
  EnergyBalanceMode("EnergyBalanceMode",this),

  SummaryFeeling("SummaryFeeling",this),
  SummaryWearOut("SummaryWearOut",this),
  SummaryFrequency("SummaryFrequency",this),
  SummaryLiveNeurons("SummaryLiveNeurons",this),
  SummaryEnergy("SummaryEnergy",this)
{
}

NLifeNet::~NLifeNet(void)
{
}
// --------------------------

// --------------------------
// Методы управления данными
// --------------------------
// Возвращает число систем жизнеобеспечения нейронов
size_t NLifeNet::GetNumNeuronsLife(void) const
{
 return NeuronsLife.size();
}

// Возвращает заданную систему жизнеобеспечения нейрона
NNeuronLife* NLifeNet::GetNeuronLife(size_t i)
{
 return NeuronsLife[i];
}

// Возвращает число бета-ансамблей нейронов
size_t NLifeNet::GetNumBetaEnsembles(void) const
{
 return BetaEnsembles.size();
}

// Возвращает заданный бета-ансамбль
const NEnsemble& NLifeNet::GetBetaEnsemble(size_t i)
{
 return BetaEnsembles[i].second;
}

// Возвращает мощность заданного бета-ансамбля
real NLifeNet::GetBetaEnsemblePower(size_t i) const
{
 return BetaEnsembles[i].first;
}

// Возвращает число ансамблей нейронов
size_t NLifeNet::GetNumEnsembles(void) const
{
 return Ensembles.size();
}

// Возвращает заданный ансамбль
const NEnsemble& NLifeNet::GetEnsemble(size_t i)
{
 return Ensembles[i].second;
}

// Возвращает мощность заданного ансамбля
real NLifeNet::GetEnsemblePower(size_t i) const
{
 return Ensembles[i].first;
}

// Возвращает имя ансамбля по имени составляющих нейронов
NameT NLifeNet::GetEnsembleName(size_t i) const
{
 NameT name;
 for(size_t j=0;j<Ensembles[i].second.size();j++)
 {
  name+=Ensembles[i].second[j]->GetName();
  if(j<Ensembles[i].second.size()-1)
   name+="+";
 }
 return name;
}

// Возвращает абсолютное значение активности ансамбля
// (средняя частота всех нейронов ансамбля)
real NLifeNet::GetEnsembleActivity(size_t i) const
{
 real eactivity=0;
 for(size_t j=0;j<Ensembles[i].second.size();j++)
  eactivity+=Ensembles[i].second[j]->GetLTZone()->GetOutputData(2).Double[0];

 if(Ensembles[i].second.size())
  return eactivity/Ensembles[i].second.size();

 return 0;
}

real NLifeNet::GetRelativeEnsembleActivity(size_t i) const
{
 real eactivity=GetEnsembleActivity(i);
// return (eactivity>POutputData[9].Double[0])?(eactivity-POutputData[9].Double[0]):0;
 return eactivity-POutputData[9].Double[0];
}

// Возвращает число связей между ансамблями
size_t NLifeNet::GetNumEnsembleLinks(void) const
{
 return EnsembleLinks.size();
}

// Возвращает связь между ансамблями
const NEnsembleLink& NLifeNet::GetEnsembleLink(size_t i) const
{
 return EnsembleLinks[i];
}
// --------------------------


// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NLifeNet* NLifeNet::New(void)
{
 return new NLifeNet;
}
// --------------------------

// --------------------------
// Скрытые методы управления компонентами
// --------------------------
// Выполняет завершающие пользовательские действия
// при добавлении дочернего компонента в этот объект
// Метод будет вызван только если comp был
// успешно добавлен в список компонент
bool NLifeNet::AAddComponent(NAContainer* comp, RDK::UIPointer* pointer)
{
 if(!NNet::AAddComponent(comp,pointer))
  return false;

 bool res=true;

 NPulseLifeNeuron *n=dynamic_cast<NPulseLifeNeuron*>(comp);
 NNeuronLife *life=0;
 NSum *pebonus=0;
 if(n)
 {
  life=n->GetNeuronLife();
   if(life)
   {
	pebonus=&*life->ExternalEnergyBonus;
	NeuronsLife.push_back(life);
	res&=Connect(life,0,2);
	res&=Connect(life,1,1);
   }

  // Устанавливает первичные связи нейрона
  for(size_t i=0;i<GetNumComponents();i++)
  {
   NPulseLifeNeuron *nn=dynamic_cast<NPulseLifeNeuron*>(GetComponentByIndex(i));
   NNeuronLife *life2=0;
   if(nn && nn != n)
   {
	life2=nn->GetNeuronLife();
	if(life2)
	{
	 res&=life2->Connect(pebonus,7);
	}
//	MVector<real> dist=n->Coord-nn->Coord;
	RDK::MVector<real> dist=n->GetCoord()-nn->GetCoord();
	if(!dist<=LinkDistance) // Фиксированное расстояние
	{
	 NPulseMembrane *cont=n->BranchDendrite(n->GetComponentId("PNeuronHebbMembrane4"),true);
	 NPulseMembrane *cont2=nn->BranchDendrite(nn->GetComponentId("PNeuronHebbMembrane4"),true);
	 RDK::ULinkSide item,conn;

	 // Подключаем возбуждающие синапсы
	 RDK::MVector<real> diff1=n->GetCoord()-nn->GetCoord(),
						  diff2=nn->GetCoord()-n->GetCoord();
	 real mul1=diff1*RDK::MVector<real>(1,0,0);
	 real mul2=diff2*RDK::MVector<real>(1,0,0);
	 if(mul1>0)
	 {
	  item.Id=n->GetLTZone()->GetLongId(this);
	  item.Index=0;
	  for(size_t k=0;k<cont2->GetNumPosChannels();k++)
	  {
	   NPulseChannel* channel=cont2->GetPosChannel(k);
	   for(size_t l=0;l<channel->GetNumSynapses();l++)
	   {
		conn.Id=channel->GetSynapse(l)->GetLongId(this);
		conn.Index=0;
		res&=CreateLink(item,conn);
	   }
	  }

	  item.Id=nn->GetLTZone()->GetLongId(this);
	  item.Index=0;
	  for(size_t k=0;k<cont->GetNumPosChannels();k++)
	  {
	   NPulseChannel* channel=cont->GetPosChannel(k);
	   for(size_t l=0;l<channel->GetNumSynapses();l++)
	   {
		conn.Id=channel->GetSynapse(l)->GetLongId(this);
		conn.Index=0;
		res&=CreateLink(item,conn);
	   }
	  }
	 }

	 if(mul2<0)
	 {
	  cont=n->BranchDendrite(n->GetComponentId("PNeuronHebbMembrane3"),true);
	  cont2=nn->BranchDendrite(nn->GetComponentId("PNeuronHebbMembrane3"),true);
	  // Подключаем тормозные синапсы
	  item.Id=n->GetLTZone()->GetLongId(this);
	  item.Index=0;
	  for(size_t k=0;k<cont2->GetNumNegChannels();k++)
	  {
	   NPulseChannel* channel=cont2->GetNegChannel(k);
	   for(size_t l=0;l<channel->GetNumSynapses();l++)
	   {
		conn.Id=channel->GetSynapse(l)->GetLongId(this);
		conn.Index=0;
		res&=CreateLink(item,conn);
	   }
	  }

	  item.Id=nn->GetLTZone()->GetLongId(this);
	  item.Index=0;
	  for(size_t k=0;k<cont->GetNumNegChannels();k++)
	  {
	   NPulseChannel* channel=cont->GetNegChannel(k);
	   for(size_t l=0;l<channel->GetNumSynapses();l++)
	   {
		conn.Id=channel->GetSynapse(l)->GetLongId(this);
		conn.Index=0;
		res&=CreateLink(item,conn);
	   }
	  }
	 }
	}
   }
  }
 }


 return res;
}

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
bool NLifeNet::ADelComponent(NAContainer* comp)
{
 vector<NNeuronLife*>::iterator I;

 I=NeuronsLife.begin();
 do
 {
  if((*I)->GetOwner() == comp)
  {
   Disconnect((*I)->GetId());
   NeuronsLife.erase(I);
   I=NeuronsLife.begin();
  }
  else
   ++I;
 }while(I != NeuronsLife.end());

 return NNet::ADelComponent(comp);
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NLifeNet::ADefault(void)
{
 SetNumOutputs(10);
 vector<size_t> size;
 size.assign(NumOutputs,1);
 SetOutputDataSize(size);

 AvailableEnergy=10;

 CellDivisionFlag=true;
 CellDivisionEnergy=0.5;
 EnsembleThreshold=0.0;
 EnsembleLinkThreshold=0.000;
 EnsembleThresholdMode=0;
 EnsembleCalculationStep=0.1;
 LinkDistance=1;

 EnergyBalanceMode=1;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NLifeNet::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NLifeNet::AReset(void)
{
 EnsembleCalculationCounter=0;
 return true;
}

// Выполняет расчет этого объекта
bool NLifeNet::ACalculate(void)
{
 vector<NNeuronLife*> best_neurons;
 SummaryFeeling=0;
 SummaryWearOut=0;
 SummaryLiveNeurons=0;
 SummaryFrequency=0;
 SummaryEnergy=0;

 SynapticMap.clear();
 for(size_t i=0;i<NeuronsLife.size();i++)
 {
//  POutputData[10].Double[i]=0;
  SynapticMap[static_cast<NPulseLifeNeuron*>(NeuronsLife[i]->GetOwner())];
  if(NeuronsLife[i]->GetActivity())
  {
   SummaryFeeling.v+=NeuronsLife[i]->GetOutputData(1).Double[0];
   SummaryWearOut.v+=NeuronsLife[i]->GetOutputData(2).Double[0];
   SummaryEnergy.v+=NeuronsLife[i]->GetOutputData(4).Double[0];
   NPulseLTZone *zone=static_cast<NPulseLTZone*>(static_cast<NAContainer*>(NeuronsLife[i]->GetOwner())->GetComponent("LTZone"));
//   POutputData[10].Double[i]=zone->GetNumAConnectors(0);
   SummaryFrequency.v+=zone->GetOutputData(2).Double[0];
   ++SummaryLiveNeurons.v;
   if(CellDivisionFlag && NeuronsLife[i]->GetOutputData(4).Double[0]>CellDivisionEnergy)
	best_neurons.push_back(NeuronsLife[i]);
  }
 }

 // Нейроны способные делится - делятся
 for(size_t i=0;i<best_neurons.size();i++)
 {
  best_neurons[i]->Energy=best_neurons[i]->Energy/2;
  NPulseLifeNeuron *n=static_cast<NPulseLifeNeuron*>(Storage->TakeObject(best_neurons[i]->GetMainOwner()->GetClass()));
  n->SetName("N");
  n->SetCoord(static_cast<NPulseLifeNeuron*>(best_neurons[i]->GetMainOwner())->GetCoord());
  n->GetNeuronLife()->Energy=best_neurons[i]->Energy;
  AddComponent(n);
 }

 POutputData[0].Double[0]=SummaryFeeling.v;
 if(SummaryLiveNeurons.v>0)
 {
  switch(EnergyBalanceMode)
  {
  case 0:
   POutputData[1].Double[0]=AvailableEnergy.v/SummaryLiveNeurons.v;
  break;

  case 1:
   POutputData[1].Double[0]=AvailableEnergy.v/SummaryLiveNeurons.v;
  break;
  }
 }
 else
  POutputData[1].Double[0]=0;

 POutputData[2].Double[0]=SummaryWearOut.v;
 POutputData[3].Double[0]=SummaryEnergy.v;
 POutputData[4].Double[0]=SummaryFrequency.v;

 POutputData[5].Double[0]=SummaryLiveNeurons.v;
 if(SummaryLiveNeurons.v>0)
 {
  POutputData[6].Double[0]=SummaryFeeling.v/SummaryLiveNeurons.v;
  POutputData[7].Double[0]=SummaryWearOut.v/SummaryLiveNeurons.v;
  POutputData[8].Double[0]=SummaryEnergy.v/SummaryLiveNeurons.v;
  POutputData[9].Double[0]=SummaryFrequency.v/SummaryLiveNeurons.v;
 }
 else
 {
  POutputData[6].Double[0]=0;
  POutputData[7].Double[0]=0;
  POutputData[8].Double[0]=0;
  POutputData[9].Double[0]=0;
 }

 if(EnsembleCalculationStep.v == 0)
  return true;

 ++EnsembleCalculationCounter;
 if(real(EnsembleCalculationCounter)/real(TimeStep) >= EnsembleCalculationStep)
 {
  EnsembleCalculationCounter=0;
  if(!CalcEnsembles(EnsembleThreshold))
   return false;

  if(!CalcEnsembleLinks(EnsembleLinkThreshold))
   return false;
 }

 return true;
}

// Вычисляет ансамбли сети
bool NLifeNet::CalcEnsembles(real threshold)
{
 Ensembles.clear();
 BetaEnsembles.clear();

 real resthreshold=0;
 size_t numneurons=0;
 NPulseLifeNeuron* n=0;
 switch(EnsembleThresholdMode)
 {
 case 2:
  for(size_t i=0;i<NeuronsLife.size();i++)
  {
   n=static_cast<NPulseLifeNeuron*>(NeuronsLife[i]->GetOwner());
   if(n->GetActivity())
   {
	resthreshold+=n->GetOutputData(5).Double[0];
	++numneurons;
   }
  }
  if(numneurons)
   resthreshold/=numneurons;
 break;
 }

 for(size_t i=0;i<NeuronsLife.size();i++)
 {
  n=static_cast<NPulseLifeNeuron*>(NeuronsLife[i]->GetOwner());
  pair<real, NEnsemble > ensemble;
  ensemble.second.push_back(n);
  ensemble.first=n->GetOutputData(4).Double[0];
  if(n->GetActivity())
  {
   for(int j=0;j<n->GetNumComponents();j++)
   {
	NPulseMembrane* membrane=dynamic_cast<NPulseMembrane*>(n->GetComponentByIndex(j));
	if(membrane)
	{
	 for(int k=0;k<membrane->GetNumComponents();k++)
	 {
	  NPulseChannel* channel=dynamic_cast<NPulseChannel*>(membrane->GetComponentByIndex(k));
	  if(channel)
	  {
	   for(int m=0;m<channel->GetNumComponents();m++)
	   {
		NPulseHebbSynapse* synapse=dynamic_cast<NPulseHebbSynapse*>(channel->GetComponentByIndex(m));
		if(synapse)
		{
		 if(EnsembleThresholdMode == 1)
		  resthreshold=n->GetOutputData(5).Double[0];
		 if(synapse->GetOutputData(3).Double[0] > resthreshold+threshold)
		 {
		  NPulseLifeNeuron* item=dynamic_cast<NPulseLifeNeuron*>(synapse->GetCItem(0).Item->GetMainOwner());
		  if(item)
		  {
		   ensemble.first+=n->GetOutputData(4).Double[0];
		   ensemble.second.push_back(item);
		  }
		 }
		}
	   }
	  }
	 }
	}
   }

   if(ensemble.second.size()>1)
	BetaEnsembles.push_back(ensemble);
  }
 }

 // Формируем список ансамблей
 for(size_t i=0;i<BetaEnsembles.size();i++)
 {
  // Берем бета-ансабль...
  pair<real, NEnsemble > bensemble=BetaEnsembles[i];
  pair<real, NEnsemble > ensemble;
  vector<pair<real, NEnsemble > > egroup;

  egroup.push_back(bensemble);
  size_t ix=0;
  for(size_t j=i+1;j<BetaEnsembles.size();j++)
  {
   for(size_t k=0;k<bensemble.second.size();k++)
   {
	if(BetaEnsembles[j].second.size() == bensemble.second.size() &&
	   find(BetaEnsembles[j].second.begin(),BetaEnsembles[j].second.end(),bensemble.second[k]) ==
				BetaEnsembles[j].second.end())
	{
	 break;
	}
	else
	 ix=k;
   }
   if(ix == bensemble.second.size()-1)
   {
	egroup.push_back(BetaEnsembles[j]);
   }
  }

  // Сформировали egroup, проверяем его размер
  if(egroup.size() >= bensemble.second.size())
  {
   for(size_t m=1;m<egroup.size();m++)
	bensemble.first+=egroup[m].first;

   // Сортируем ансамбль
   vector<string> enames;
   enames.resize(bensemble.second.size());
   for(size_t m=0;m<enames.size();m++)
	enames[m]=bensemble.second[m]->GetName();

   sort(enames.begin(),enames.end());

   for(size_t m=0;m<enames.size();m++)
   {
	for(size_t mm=0;mm<bensemble.second.size();mm++)
	{
	 if(enames[m] == bensemble.second[mm]->GetName() && mm > m)
	  swap(bensemble.second[m],bensemble.second[mm]);
	}
   }
   // Конец сортировки


   size_t m;
   for(m=0;m<Ensembles.size();++m)
	if(Ensembles[m].second == bensemble.second)
	 break;

   if(m == Ensembles.size())
	Ensembles.push_back(bensemble);
  }
 }

 return true;
}

// Вычисляет связи между ансамблями сети
bool NLifeNet::CalcEnsembleLinks(real threshold)
{
 EnsembleLinks.clear();
 for(size_t i=0;i<Ensembles.size();i++)
 {
  for(size_t j=0;j<Ensembles[i].second.size();j++)
  {
	 for(int k=0;k<Ensembles[i].second[j]->GetLTZone()->GetNumOutputs();k++)
	  for(int l=0;l<Ensembles[i].second[j]->GetLTZone()->GetNumAConnectors(k);l++)
	  {
	   const NPulseHebbSynapse* synapse=
	   	dynamic_cast<const NPulseHebbSynapse*>(Ensembles[i].second[j]->GetLTZone()->GetAConnectorByIndex(int(k), int(l)));
	   if(synapse)
	   {
		for(size_t n=0;n<Ensembles.size();n++)
		{
		  for(size_t m=0;m<Ensembles[n].second.size();m++)
		  {
		   if(n != i)
			if(synapse->CheckOwner(Ensembles[n].second[m]))
			 if(synapse->GetOutputData(3).Double[0] > threshold)
			 {
			  NEnsembleLink link;
			  link.In=GetEnsembleName(i);
			  link.Out=GetEnsembleName(n);
			  link.Power=synapse->GetOutputData(3).Double[0];

			  size_t p=0;
			  for(;p<EnsembleLinks.size();p++)
			   if(EnsembleLinks[p].In == link.In &&
				  EnsembleLinks[p].Out == link.Out)
			   {
				EnsembleLinks[p].Power+=link.Power;
				break;
			   }

			  if(p >= EnsembleLinks.size())
			   EnsembleLinks.push_back(link);
			 }
		  }
		}
	   }
	  }
  }
 }

 sort(EnsembleLinks.begin(),EnsembleLinks.end());
 return true;
}
// --------------------------

}
#endif

