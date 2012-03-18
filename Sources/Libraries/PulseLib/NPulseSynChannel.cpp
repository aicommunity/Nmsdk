// ===========================================================
// Version:        3.0.3
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:        alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NPULSE_SYN_CHANNEL_CPP
#define NPULSE_SYN_CHANNEL_CPP

#include "NPulseSynChannel.h"
#include "NPulseMembrane.h"
#include "NPulseNeuron.h"
#include "../NeuronLifeLib/NPulseLifeNeuron.h"
#include "../BCL/NConnector.h"
#include "../ReceiverLib/NReceptor.h"


namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseSynChannel::NPulseSynChannel(void)
//: NPulseChannel(name),
: PulseAmplitude("PulseAmplitude",this,&NPulseSynChannel::SetPulseAmplitude),
SecretionTC("SecretionTC",this,&NPulseSynChannel::SetSecretionTC),
DissociationTC("DissociationTC",this,&NPulseSynChannel::SetDissociationTC),
InhibitionCoeff("InhibitionCoeff",this,&NPulseSynChannel::SetInhibitionCoeff),
SynapseResistance("SynapseResistance",this,&NPulseSynChannel::SetSynapseResistance),

PreOutput("PreOutput",this)
{
}

NPulseSynChannel::~NPulseSynChannel(void)
{
}
// --------------------------


// --------------------------
// Методы управления специфическими компонентами
// --------------------------
// Возвращает число синапсов
size_t NPulseSynChannel::GetNumSynapses(void) const
{
 return 0;
// return GetNumComponents();
}

// Возвращает синапс по индексу
NPulseSynapse* NPulseSynChannel::GetSynapse(size_t i)
{
// return static_cast<NPulseSynapse*>(GetComponentByIndex(i));
 return 0;
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду импульсов
bool NPulseSynChannel::SetPulseAmplitude(real value)
{
 return true;
}

// Постоянная времени выделения медиатора
bool NPulseSynChannel::SetSecretionTC(real value)
{
 if(value <= 0)
  return false;

 Ready=false;

 return true;
}

// Постоянная времени распада медиатора
bool NPulseSynChannel::SetDissociationTC(real value)
{
 if(value <= 0)
  return false;

 Ready=false;

 return true;
}

// Коэффициент пресинаптического торможения
bool NPulseSynChannel::SetInhibitionCoeff(real value)
{
 if(SynapseResistance.v > 0)
  OutputConstData=4.0*(value+1)/SynapseResistance.v;
 else
  OutputConstData=0;

 return true;
}

// Вес (эффективность синапса) синапса
bool NPulseSynChannel::SetSynapseResistance(real value)
{
 if(value<=0)
  return false;

 OutputConstData=4.0*InhibitionCoeff.v/value;

 return true;
}
// --------------------------

// --------------------------
// Методы управления объектом
// --------------------------
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NPulseSynChannel* NPulseSynChannel::New(void)
{
 return new NPulseSynChannel;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NPulseSynChannel::CheckComponentType(UEPtr<NAContainer> comp) const
{
// if(dynamic_cast<const NPulseSynapse*>(comp))
//  return true;

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
/*bool NPulseSynChannel::AAddComponent(UEPtr<UAContainer> comp, UEPtr<UIPointer> pointer)
{
 InstallHebbSynapses(comp);
 return true;
}     */

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
/*bool NPulseSynChannel::ADelComponent(UEPtr<UAContainer> comp)
{
 return true;
}                     */
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NPulseSynChannel::ADefault(void)
{
 if(!NPulseChannel::ADefault())
  return false;

 // Начальные значения всем параметрам
 // Амплитуда входных импульсов
 PulseAmplitude=1;

 // Постоянная времени выделения медиатора
 SecretionTC=0.001;

 // Постоянная времени распада медиатора
 DissociationTC=0.01;

 // Коэффициент пресинаптического торможения
 InhibitionCoeff=1;

 // Вес (эффективность синапса) синапса
 SynapseResistance=1.0e8;

// SetNumInputs(1);

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NPulseSynChannel::ABuild(void)
{
 if(!NPulseChannel::ABuild())
  return false;

 VSecretionTC=SecretionTC*TimeStep;
 VDissociationTC=DissociationTC*TimeStep;
 return true;
}

// Сброс процесса счета.
bool NPulseSynChannel::AReset(void)
{
 if(!NPulseChannel::AReset())
  return false;

 // Сброс временных переменных
// PreOutput=0;
 PreOutput->assign(PreOutput->size(),0);

 FillOutputData();
 return true;
}

// Выполняет расчет этого объекта
bool NPulseSynChannel::ACalculate(void)
{
 real channel_input=0;
 size_t num_connected_channels=0;
 real G=0;

 // Расчет синапсов
 real input=0;
 size_t num_connected_synapsis=0;
 real syn_output=0;


 for(int n=0;n<NumInputs;n++)
 {
  if(GetInputDataSize(n) == 0)
   continue;
  if(dynamic_cast<NPulseChannel*>(GetCItem(n).Item) ||
     dynamic_cast<NReceptor*>(GetCItem(n).Item) ||
	 dynamic_cast<NConstGenerator*>(GetCItem(n).Item))
  {
   size_t inpsize=0;
   if((inpsize=GetInputDataSize(n)) >0)
   {
    real *data=&(GetInputData(n)->Double[0]);
    for(size_t j=0;j<inpsize;j++,++data)
     channel_input+=*data;
    ++num_connected_channels;
   }
  }
  else // Остальные подключенные компоненты считаем входами синапсов
  {
   ++num_connected_synapsis;
   if(PreOutput->size()<num_connected_synapsis)
   {
	PreOutput->resize(num_connected_synapsis);
    PreOutput.v[num_connected_synapsis-1]=0;
   }

   input=GetInputData(n)->Double[0];

   if(MainOwner && Owner)
   {
	if(Type() < 0)
	 ++static_pointer_cast<NPulseNeuron>(MainOwner)->NumActivePosInputs.v;
	else
	 ++static_pointer_cast<NPulseNeuron>(MainOwner)->NumActiveNegInputs.v;
   }

   if(input>0)
    PreOutput.v[num_connected_synapsis-1]+=(input/PulseAmplitude.v-PreOutput.v[num_connected_synapsis-1])/VSecretionTC;
   else
    PreOutput.v[num_connected_synapsis-1]-=PreOutput.v[num_connected_synapsis-1]/VDissociationTC;

   syn_output=OutputConstData*(1.0-InhibitionCoeff.v*PreOutput.v[num_connected_synapsis-1])*PreOutput.v[num_connected_synapsis-1];

   if(syn_output>0)
	G+=syn_output;
  }
 }

 // Получение данных канала
 if(num_connected_channels)
  channel_input/=num_connected_channels;

 real feedback=static_pointer_cast<NPulseMembrane>(Owner)->Feedback;
 // Получение информации об обратной связи
 if(Owner)
  channel_input-=feedback;

 // Расчет
 real *out=&POutputData[0].Double[0];
 real Ti,sum_u;

 if(!feedback)
 {
  Ti=Capacity/(G+1.0/Resistance);
  sum_u=(1.0+G*Resistance);
 }
 else
 {
  Ti=Capacity/(G+1.0/FBResistance);
  sum_u=(1.0+G*FBResistance);
 }

 *out+=(channel_input-(*out)*sum_u)/(Ti*TimeStep);

 return true;
}
// --------------------------
}

#endif

