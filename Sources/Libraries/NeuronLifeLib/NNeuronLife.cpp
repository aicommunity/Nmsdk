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

#ifndef NNEURON_LIFE_CPP
#define NNEURON_LIFE_CPP

#include "NNeuronLife.h"
#include "../PulseLib/NPulseChannel.h"
#include "../BCL/NConnector.h"


namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NNeuronLife::NNeuronLife(void)
//: NADItem(name),
 : Threshold("Threshold",this,&NNeuronLife::SetThreshold),
  ThresholdLife("ThresholdLife",this),
  ThresholdWearOut("ThresholdWearOut",this),
  ThresholdFeel("ThresholdFeel",this),
  CriticalEnergy("CriticalEnergy",this),
  EnergyBonus("EnergyBonus",this),

  WearOut("WearOut",this),
  Energy("Energy",this),
  Feel("Feel",this),

  Usum("Usum",this),
  WearOutConstPositive("WearOutConstPositive",this),
  WearOutConstNegative("WearOutConstNegative",this),
  MaxPotentialGradient("MaxPotentialGradient",this,&NNeuronLife::SetMaxPotentialGradient),
//  UsumOld("UsumOld",this),
//  UsumProizv("UsumProizv",this),
  Kw("Kw",this),

  Esum("Esum",this),
  En("En",this,&NNeuronLife::SetEn),
  Emax("Emax",this,&NNeuronLife::SetEmax),
  EsumOld("EsumOld",this),
  EsumProizv("EsumProizv",this),
  Kq("Kq",this),

  EyConst("EyConst",this),
  EyBonusPos("EyBonusPos",this),
  EyBonusNeg("EyBonusNeg",this),
  EnergyComprehensibility("EnergyComprehensibility",this),

  Ea("Ea",this),
  Ey("Ey",this),
  Ee("Ee",this),
  Eh("Eh",this),
  dEa("dEa",this),
  dEy("dEy",this),
  dEe("dEe",this),
  dEh("dEh",this),
  dE("dE",this),
//  E("E",this),
  Econst("Econst",this),
  Ecr("Ecr",this),
  WearOutcr("WearOutcr",this),
  EnergyWearOutCritical("EnergyWearOutCritical",this),
//  N("N",this),
  Ee0("Ee0",this),
  Eh0("Eh0",this),
  Es("Es",this),

  Kdp("Kdp",this),
  Pdmax("Pdmax",this,&NNeuronLife::SetPdmax),
  Qd("Qd",this),
  Qsummax("Qsummax",this,&NNeuronLife::SetQsummax),

  Qsum("Qsum",this),
  Khp0("Khp0",this),
  Khp1("Khp1",this),

  ExternalEnergyBonus(this,"ExternalEnergyBonus")
{
}

NNeuronLife::~NNeuronLife(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
bool NNeuronLife::SetThreshold(real value)
{
 return true;
}

// Устанавливает ожидаемое значение максимального градиента выхода нейрона
bool NNeuronLife::SetMaxPotentialGradient(real value)
{
 if(value <= 0)
  return false;

 Ready=false;
 return true;
}

bool NNeuronLife::SetEmax(real value)
{
 if(value <= 0)
  return false;

 Ready=false;
 return true;
}

bool NNeuronLife::SetEn(real value)
{
 if(value <= 0)
  return false;

 Ready=false;
 return true;
}

bool NNeuronLife::SetPdmax(real value)
{
 if(value <= 0)
  return false;

 Ready=false;
 return true;
}

bool NNeuronLife::SetQsummax(real value)
{
 if(value <= 1)
  return false;

 Ready=false;
 return true;
}
// --------------------------


// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NNeuronLife* NNeuronLife::New(void)
{
 return new NNeuronLife;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NNeuronLife::CheckComponentType(UEPtr<NAContainer> comp) const
{
 if(dynamic_pointer_cast<NSum>(comp))
  return true;

 return false;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------


// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NNeuronLife::ABuild(void)
{
// Kw=log(float(2))/MaxPotentialGradient;

// Kq=-(1/Emax)*log(0.1);

// Kdp = -(1/Qsummax)*log(0.1);

// Qd = -1.0/Kdp*log(Pdmax-1);

 return true;
}
 // Восстановление настроек по умолчанию и сброс процесса счета
bool NNeuronLife::ADefault(void)
{
 SetNumOutputs(8);
 vector<size_t> size;
 size.resize(NumOutputs);
 size[0]=4;
 size[1]=1;
 size[2]=1;
 size[3]=4;
 size[4]=1;
 size[5]=5;
 size[6]=5;
 size[7]=1;

 SetOutputDataSize(size);

 // Начальные значения всем параметрам
 Threshold=static_cast<real>(0.001);
 WearOutConstPositive = static_cast<real>(100);//0.01;
 WearOutConstNegative = 1;//0.1;
 MaxPotentialGradient=1;
 Usum = 1;
 En = static_cast<real>(0.1);
 Emax = 1;
 Esum = 1;
 Econst = 1;
 Ecr =static_cast<real>(500);//0.5
 WearOutcr = 10000;
 EnergyWearOutCritical = 5000;
 Ee0 =static_cast<real>(10);// 0.1
 Eh0 =static_cast<real>(180);// 0.1
 Es =1;
 Khp0 = static_cast<real>(0.1e-3);//0.1;
 Khp1 = Threshold/1000;//static_cast<real>(0.001);//0.2;
 EyConst=static_cast<real>(10000);//1;
 Qsummax=2;

 CriticalEnergy=static_cast<real>(0.5);

 Kq=1;
 Pdmax=0.001;//10;//2;
// NumInputs=2;

 Kw=log(float(2))/MaxPotentialGradient;

 Kq=-(1/Emax)*log(static_cast<real>(0.1));

 Kdp=1.0/1000;//1;
 Qd=1;//0.5;//3;
// Kdp = -(1/Qsummax)*log(0.1);
// Qd = -1.0/Kdp*log(Pdmax-1);

 EyBonusPos=1;
 EyBonusNeg=0.1;
 EnergyComprehensibility=1000;

 return true;
}
// Сброс процесса счета.
bool NNeuronLife::AReset(void)
{
 // Сброс временных переменных
// NeuralPotential=0;
// PrePotential=0;
// PulseCounter=0;
// UsumProizv=0;
 Usum=0;
 EsumProizv=0;

 Energy=EsumOld=static_cast<real>(100);
 Feel=0;

 Qsum=0;

 ThresholdWearOut=1;
 ThresholdFeel=1;
// ThresholdLife=(ThresholdWearOut.v+ThresholdFeel.v+1)*Threshold;
 ThresholdLife=(ThresholdWearOut.v+ThresholdFeel.v+Threshold.v);
 WearOut=static_cast<real>(0.1);

 dEa=0;
 dEy=0;
 dEe=0;
 dEh=0;
 dE=0;

 EnergyBonus=0;

 return true;
}

bool NNeuronLife::ACalcWearOut(void)
{
 // Добавляем фиксированную прибавку к износу в секунду
 WearOut.v+=WearOutConstPositive/TimeStep;

 // Вычитаем обновление нейрона за счет генерации
// WearOut-=WearOut*(1/(1+exp(-Kw*fabs(Usum)))-0.5)*WearOutConstNegative/TimeStep;
// WearOut-=fabs(Usum)*WearOutConstNegative/TimeStep;//(1.0/(1.0+exp(-Kw*fabs(Usum)))-0.5)*WearOutConstNegative/TimeStep;
 WearOut.v-=WearOut*fabs(Usum)*WearOutConstNegative/TimeStep;

 return true;
}
bool NNeuronLife::ACalcEnergy(void)
{
 real old_Energy=Energy;
 // Вычисляем бонус энергии
// EnergyBonus+=fabs(Usum)*EyBonusPos/TimeStep;
// EnergyBonus-=EnergyBonus*EyBonusNeg/TimeStep;
 EnergyBonus.v+=fabs(Usum)*EyBonusPos;
 EnergyBonus.v-=EnergyBonus.v*EyBonusNeg.v;

 Energy.v+=Ea;

 dEy=fabs(Usum)*EyConst/TimeStep-Ey;
 Ey.v+=dEy;

 dEe=Ee0*exp((log(2.0)/Ecr)*Energy)/TimeStep-Ee;
 Ee.v+=dEe;

 dEh=Eh0*(1+exp((log(1.5)/EnergyWearOutCritical)*WearOut))/TimeStep-Eh;
 Eh.v+=dEh;

 Energy.v-=Ey.v+Ee.v+Eh.v;

 dE=(Energy-old_Energy)/TimeStep;

 return true;
}
bool NNeuronLife::ACalcFeel(void)
{
 EsumProizv = (Energy.v-EsumOld.v)*TimeStep;

 EsumOld = Energy;

 Feel=(Energy.v-En.v) + FeelDiff(Kq,EsumProizv,En);

 return true;
}
bool NNeuronLife::ACalcThresholdLife(void)
{
// ThresholdFeel = Pdmax/(1+exp(-Kdp*(CriticalEnergy-Energy)));
// ThresholdFeel = Pdmax/(1+exp(-Kdp*(Qsum.v-Qd.v)));
 ThresholdFeel = Pdmax/(1+exp(-Kdp*(Feel.v-Qd.v)));

 if (WearOut < WearOutcr)
 {
  if(WearOut.v<0.05)
   ThresholdWearOut=1e10;
  else
   ThresholdWearOut = exp(Khp0.v/WearOut.v) - exp(Khp0.v/WearOutcr.v);
 }
 else
  ThresholdWearOut = static_cast<real>(1.0-exp(Khp1*(WearOut.v - WearOutcr.v)));

// ThresholdLife = static_cast<real>((ThresholdWearOut.v + ThresholdFeel.v + 0.5)*Threshold);
 ThresholdLife = 0;//static_cast<real>(ThresholdWearOut.v + ThresholdFeel.v + Threshold);

 return true;
}

real NNeuronLife::FeelDiff(real kq, real ediff, real en)
{
 if(ediff>1e2)
//  return static_cast<real>(0.5*en);
  return static_cast<real>(en);
 if(ediff<-1e2)
  return 0;

// return static_cast<real>((1.0/(1.0+exp(-kq*ediff))-0.5)*en);
 return static_cast<real>((1.0/(1.0+exp(-kq*ediff))-0.5)*en*2.0);
}

// Выполняет расчет этого объекта
bool NNeuronLife::ACalculate(void)
{
 if(NumInputs<3 || PInputDataSize[0]<1 || PInputDataSize[1]<1 || PInputDataSize[2]<1)
  return true;

 real potential=PInputData[0]->Double[0];
 real epos=PInputData[1]->Double[0];
 real qsum=PInputData[2]->Double[0];

// UsumProizv = (potential-Usum)*TimeStep;
 Usum=potential;
// UsumOld = Usum;

 Qsum=qsum;

 real ebonus=0;
 if(&*ExternalEnergyBonus && ExternalEnergyBonus->GetOutputDataSize(0)>0)
  ebonus=ExternalEnergyBonus->GetOutputData(0).Double[0];

 ebonus+=EnergyBonus;

 if(epos>EnergyComprehensibility)
 {
  if(ebonus)
  {
   if(EnergyComprehensibility+ebonus<epos)
	epos=EnergyComprehensibility+ebonus;
  }
  else
   epos=EnergyComprehensibility;
 }
 dEa=epos/TimeStep-Ea;
 Ea.v+=dEa;

 if(!ACalcWearOut())
  return false;

 if(!ACalcEnergy())
  return false;

 if(!ACalcFeel())
  return false;

 if(!ACalcThresholdLife())
  return false;

 if(Energy.v < 0) // Вместо 0 должен быть параметр остаточного минимума
 {
  UEPtr<NADItem> item=dynamic_pointer_cast<NADItem>(Owner);
  if(item)
  {
   item->SetActivity(false);
   item->FillOutputData(0);
   FillOutputData(0);
   return true;
  }
 }

 POutputData[0].Double[0]=Threshold.v;
 POutputData[0].Double[1]=ThresholdWearOut.v;
 POutputData[0].Double[2]=ThresholdFeel.v;
 POutputData[0].Double[3]=ThresholdLife.v;

 POutputData[1].Double[0]=Feel.v;

 POutputData[2].Double[0]=WearOut.v;

 POutputData[3].Double[0]=Ey.v;
 POutputData[3].Double[1]=Ee.v;
 POutputData[3].Double[2]=Eh.v;
 POutputData[3].Double[3]=Ey.v+Ee.v+Eh.v;

 POutputData[4].Double[0]=Energy.v;

 // Вычисляем мотивацию для возбуждающих синапсов
 POutputData[5].Double[0]=dEa*TimeStep;
 POutputData[5].Double[1]=-dEy;
 POutputData[5].Double[2]=-dEe*TimeStep;
 POutputData[5].Double[3]=dEh*TimeStep;
 POutputData[5].Double[4]=0;//dE*TimeStep;

 // Вычисляем мотивацию для тормозных синапсов
/* POutputData[6].Double[0]=dEa*TimeStep;
 POutputData[6].Double[1]=-dEy;
 POutputData[6].Double[2]=-dEe*TimeStep;
 POutputData[6].Double[3]=dEh*TimeStep;
 POutputData[6].Double[4]=0;//-dE*TimeStep;
  */
 POutputData[6].Double[0]=-dEa*TimeStep;
 POutputData[6].Double[1]=dEy;
 POutputData[6].Double[2]=dEe*TimeStep;
 POutputData[6].Double[3]=-dEh*TimeStep;
 POutputData[6].Double[4]=0;//-dE*TimeStep;

 // Вычисляем опосредованные воздействия - энергетический бонус
 POutputData[7].Double[0]=EnergyBonus.v;

 return true;
}
// --------------------------
}
#endif
