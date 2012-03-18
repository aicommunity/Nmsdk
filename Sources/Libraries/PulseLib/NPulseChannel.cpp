// ===========================================================
// Version:        3.0.3
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NPULSE_CHANNEL_CPP
#define NPULSE_CHANNEL_CPP

#include "NPulseChannel.h"
#include "NPulseSynapse.h"
#include "NPulseMembrane.h"
#include "NPulseNeuron.h"
#include "NPulseHebbSynapse.h"
#include "../NeuronLifeLib/NPulseLifeNeuron.h"
#include "../BCL/NConnector.h"


namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseChannel::NPulseChannel(void)
//: NADItem(name),
: Capacity("Capacity",this,&NPulseChannel::SetCapacity),
Resistance("Resistance",this,&NPulseChannel::SetResistance),
FBResistance("FBResistance",this,&NPulseChannel::SetFBResistance),
Type("Type",this)
{
}

NPulseChannel::~NPulseChannel(void)
{
}
// --------------------------


// --------------------------
// Методы управления специфическими компонентами
// --------------------------
// Возвращает число синапсов
size_t NPulseChannel::GetNumSynapses(void) const
{
 return GetNumComponents();
}

// Возвращает синапс по индексу
UEPtr<NPulseSynapse> NPulseChannel::GetSynapse(size_t i)
{
 return static_pointer_cast<NPulseSynapse>(GetComponentByIndex(i));
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Емкость мембраны
bool NPulseChannel::SetCapacity(real value)
{
 if(value <= 0)
  return false;

 return true;
}

// Сопротивление мембраны
bool NPulseChannel::SetResistance(real value)
{
 if(value <= 0)
  return false;

 return true;
}

// Сопротивление перезаряда мембраны
bool NPulseChannel::SetFBResistance(real value)
{
 if(value <= 0)
  return false;

 return true;
}
// --------------------------

// --------------------------
// Методы управления объектом
// --------------------------
// Подключает синапс хебба synapse к низкопороговой зоне нейрона-владельца
// Возвращает false только если произошла ошибка установки связи
// Если synapse == 0, то подключает все синапсы хебба
bool NPulseChannel::InstallHebbSynapses(UEPtr<NAContainer> synapse)
{
 bool res=true;
 UEPtr<NPulseNeuron> mowner=dynamic_pointer_cast<NPulseNeuron>(MainOwner);

 if(mowner && mowner->GetLTZone())
 {
  if(synapse)
  {
   UEPtr<NPulseHebbSynapse> hsynapse=dynamic_pointer_cast<NPulseHebbSynapse>(synapse);
   if(hsynapse)
   {
	RDK::ULinkSide item,conn;
	item.Id=mowner->GetLTZone()->GetLongId(mowner);
	item.Index=0;
	conn.Id=hsynapse->GetLongId(mowner);
	conn.Index=1;
	res&=mowner->CreateLink(item,conn);
   }
  }
  else
  {
   RDK::ULinkSide item,conn;
   for(size_t i=0;i<GetNumSynapses();i++)
   {
	UEPtr<NPulseHebbSynapse> hsynapse=dynamic_pointer_cast<NPulseHebbSynapse>(GetSynapse(i));
	if(hsynapse)
	{
	 item.Id=mowner->GetLTZone()->GetLongId(mowner);
     item.Index=0;
	 conn.Id=hsynapse->GetLongId(mowner);
	 conn.Index=1;
	 res&=mowner->CreateLink(item,conn);
	}
   }
  }
 }

 UEPtr<NPulseLifeNeuron> mlowner=dynamic_pointer_cast<NPulseLifeNeuron>(MainOwner);

 if(mlowner && mlowner->GetNeuronLife())
 {
  if(synapse)
  {
   UEPtr<NPulseHebbSynapse> hsynapse=dynamic_pointer_cast<NPulseHebbSynapse>(synapse);
   if(hsynapse)
   {
	RDK::ULinkSide item,conn;
	item.Id=mlowner->GetNeuronLife()->GetLongId(mlowner);
	if(Type.v>0)
	 item.Index=6;
	else
	 item.Index=5;
	conn.Id=hsynapse->GetLongId(mlowner);
	conn.Index=2;
	res&=mlowner->CreateLink(item,conn);
   }
  }
  else
  {
   RDK::ULinkSide item,conn;
   for(size_t i=0;i<GetNumSynapses();i++)
   {
	UEPtr<NPulseHebbSynapse> hsynapse=dynamic_pointer_cast<NPulseHebbSynapse>(GetSynapse(i));
	if(hsynapse)
	{
	 item.Id=mlowner->GetNeuronLife()->GetLongId(mlowner);
	 if(Type.v>0)
	  item.Index=6;
	 else
	  item.Index=5;
	 conn.Id=hsynapse->GetLongId(mlowner);
	 conn.Index=2;
	 res&=mlowner->CreateLink(item,conn);
	}
   }
  }
 }
 return res;
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NPulseChannel* NPulseChannel::New(void)
{
 return new NPulseChannel;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NPulseChannel::CheckComponentType(UEPtr<NAContainer> comp) const
{
 if(dynamic_pointer_cast<NPulseSynapse>(comp))
  return true;

 return false;
}
// --------------------------

// --------------------------
// Скрытые методы управления компонентами
// --------------------------
// Выполняет завершающие пользовательские действия
// при добавлении дочернего компонента в этот объект
// Метод будет вызван только если comp был
// успешно добавлен в список компонент
bool NPulseChannel::AAddComponent(UEPtr<UAContainer> comp, UEPtr<UIPointer> pointer)
{
 InstallHebbSynapses(comp);
 return true;
}

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
bool NPulseChannel::ADelComponent(UEPtr<UAContainer> comp)
{
 return true;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NPulseChannel::ADefault(void)
{
 // Емкость мембраны
 Capacity=1.0e-9;

 // Сопротивление мембраны
 Resistance=1.0e7;

 // Сопротивление перезаряда мембраны
 FBResistance=1.0e8;

 Type=0;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NPulseChannel::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NPulseChannel::AReset(void)
{
 FillOutputData();
 return true;
}

// Выполняет расчет этого объекта
bool NPulseChannel::ACalculate(void)
{
 real channel_input=0;
 real G=0;

 // Получение доступа к данным синапса
 for(int i=0;i<NumComponents;i++)
  G+=static_pointer_cast<NADItem>(PComponents[i])->GetOutputData(0).Double[0];
 
 // Получение данных канала
 if(FullInputDataSize>0)
 {
  size_t inpsize;
  for(int i=0;i<NumInputs;i++)
  {
   if((inpsize=GetInputDataSize(i)) >0)
   {
	real *data=&(GetInputData(i)->Double[0]);
	for(size_t j=0;j<inpsize;j++,++data)
	 channel_input+=*data;
   }
  }
  channel_input/=FullInputDataSize;
 }

 real feedback=static_pointer_cast<NPulseMembrane>(Owner)->Feedback;
 // Получение информации об обратной связи
 if(Owner)
  channel_input-=feedback;

 // Расчет
 real *out=&POutputData[0].Double[0];
 real Ti,sum_u;

 if(!feedback)
 {
  Ti=Capacity.v/(G+1.0/Resistance.v);
  sum_u=(1.0+G*Resistance.v);
 }
 else
 {
  Ti=Capacity.v/(G+1.0/FBResistance.v);
  sum_u=(1.0+G*FBResistance.v);
 }

 *out+=(channel_input-(*out)*sum_u)/(Ti*TimeStep);

 return true;
}
// --------------------------
}

#endif

