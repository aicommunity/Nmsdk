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

#ifndef NPULSE_HEBB_SYNAPSE_CPP
#define NPULSE_HEBB_SYNAPSE_CPP

#include "NPulseHebbSynapse.h"
#include "../NeuronLifeLib/NPulseLifeNeuron.h"
#include "NPulseChannel.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseHebbSynapse::NPulseHebbSynapse(void)
//: NPulseSynapse(name),
: G("G",this),
Gd("Gd",this),
Gs("Gs",this),
Min("Min",this),
Mout("Mout",this),
Win("Win",this),
Wout("Wout",this),
Md("Md",this),
ActiveMs("ActiveMs",this),
PassiveMs("PassiveMs",this),
Kin("Kin",this),
Kout("Kout",this),
Kmot("Kmot",this),

GdGain("GdGain",this),
GsGain("GsGain",this)
{
}

NPulseHebbSynapse::~NPulseHebbSynapse(void)
{
}
// --------------------------


// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду импульсов
/*bool NPulseHebbSynapse::SetPulseAmplitude(real value)
{
 return true;
}

// Постоянная времени выделения медиатора
bool NPulseHebbSynapse::SetSecretionTC(real value)
{
 if(value <= 0)
  return false;

 Ready=false;

 return true;
}

// Постоянная времени распада медиатора
bool NPulseHebbSynapse::SetDissociationTC(real value)
{
 if(value <= 0)
  return false;

 Ready=false;

 return true;
}

// Коэффициент пресинаптического торможения
bool NPulseHebbSynapse::SetInhibitionCoeff(real value)
{
 if(Resistance.v > 0)
  OutputConstData=4.0*(value+1)/Resistance.v;
 else
  OutputConstData=0;

 return true;
}

// Вес (эффективность синапса) синапса
bool NPulseHebbSynapse::SetResistance(real value)
{
 if(value<=0)
  return false;

 OutputConstData=4.0*InhibitionCoeff.v/value;

 return true;
}                */
// --------------------------


// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NPulseHebbSynapse* NPulseHebbSynapse::New(void)
{
 return new NPulseHebbSynapse;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NPulseHebbSynapse::ADefault(void)
{
 if(!NPulseSynapse::ADefault())
  return false;

 SetNumOutputs(6);
 vector<size_t> size;
 size.assign(NumOutputs,1);
 SetOutputDataSize(size);

	Min=10;
	Mout=10;
	Md=10;
	Kmot=1;
	Kin=100;
	Kout=100;

	GdGain=10;
	GsGain=1;//10;

 Kmot->resize(5);
 Kmot[0]=1;
 Kmot[1]=1;
 Kmot[2]=10000;
 Kmot[3]=100000;
 Kmot[4]=100;

 Gs->resize(Kmot->size());

 ActiveMs->resize(Kmot->size());
 ActiveMs[0]=0.001;
 ActiveMs[1]=0.001;
 ActiveMs[2]=0.001;
 ActiveMs[3]=0.001;
 ActiveMs[4]=0.001;

 PassiveMs->resize(Kmot->size());
 PassiveMs[0]=0.1;
 PassiveMs[1]=0.1;
 PassiveMs[2]=0.1;
 PassiveMs[3]=0.1;
 PassiveMs[4]=0.1;

 // Вес (эффективность синапса) синапса
 Resistance=1.0e10;
// Resistance=1.0e8;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NPulseHebbSynapse::ABuild(void)
{
 return NPulseSynapse::ABuild();
}

// Сброс процесса счета.
bool NPulseHebbSynapse::AReset(void)
{
 // Сброс временных переменных
 Win=0;
 Wout=0;
 Gd=0;
 Gs->assign(Kmot->size(),0);
 G=0;

 return NPulseSynapse::AReset();
}

// Выполняет расчет этого объекта
bool NPulseHebbSynapse::ACalculate(void)
{
 real input=0;
 real ltzoneoutput=0;
 vector<real> motivation;


 if(!NPulseSynapse::ACalculate())
  return false;

 if(NumInputs <2 || GetInputDataSize(0)<=0 || GetInputDataSize(1)<=0)
  return true;

 motivation.assign(Kmot->size(),0);
 input=GetInputData(0)->Double[0];
 ltzoneoutput=GetInputData(1)->Double[0];

 // Применяем мотивацию если есть
 if(NumInputs > 2 && GetInputDataSize(2)>0)
 {
  size_t motmin=(Kmot->size()<GetInputDataSize(2))?Kmot->size():GetInputDataSize(2);
  for(size_t i=0;i<motmin;i++)
   motivation[i]=GetInputData(2)->Double[i]*Kmot[i];
 }

 Win.v += (Kin.v*input - Min.v*Win.v)/TimeStep;
 Wout.v += (Kout.v*ltzoneoutput - Mout.v*Wout.v)/TimeStep;
// Wout.v=1;

 Gd.v += (Win.v*Wout.v - Md.v*Gd.v)/TimeStep;

// for(size_t i=0;i<Gs->size();i++)
//  Gs[i] += (motivation[i]*Gd.v - ActiveMs[i]*Gs[i])/TimeStep;

 for(size_t i=0;i<Gs->size();i++)
  if(motivation[i]>0)
//  if(motivation[i]*Gd.v > PassiveMs[i]*Gs[i])
   Gs[i] += (motivation[i]*Gd.v - ActiveMs[i]*Gs[i])/TimeStep;
  else
   Gs[i] += (motivation[i]*Gd.v - PassiveMs[i]*Gs[i])/TimeStep;

 real gs_res=0;
 for(size_t i=0;i<Gs->size();i++)
  gs_res+=Gs[i];
 G.v = (Gd.v*GdGain + gs_res*GsGain);

 POutputData[0].Double[0]*=(1.0+G.v);
 POutputData[1].Double[0]=G.v;
 POutputData[2].Double[0]=Gd.v*GdGain;
 POutputData[3].Double[0]=gs_res*GsGain;
 POutputData[4].Double[0]=Win.v;
 POutputData[5].Double[0]=Wout.v;

 if(MainOwner && Owner)
 {
  UEPtr<NPulseLifeNeuron> neuron=dynamic_pointer_cast<NPulseLifeNeuron>(MainOwner);
  if(neuron)
  {
   if(static_pointer_cast<NPulseChannel>(Owner)->Type()>0)
   {
	neuron->SummaryNegGs.v+=gs_res*GsGain.v;
	neuron->SummaryNegGd.v+=Gd.v*GdGain.v;
	neuron->SummaryNegG.v+=G;
   }
   else
   {
	neuron->SummaryPosGs.v+=gs_res*GsGain.v;
	neuron->SummaryPosGd.v+=Gd.v*GdGain.v;
	neuron->SummaryPosG.v+=G;
   }
  }
 }

 return true;
}
// --------------------------
}

#endif
