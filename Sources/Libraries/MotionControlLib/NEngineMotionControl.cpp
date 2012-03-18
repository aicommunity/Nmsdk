#include "NEngineMotionControl.h"
#include "../../Kernel/NStorage.h"
#include "../BCL/NNet.h"
#include "../SourceLib/NConstGenerator.h"
#include "../SourceLib/NPulseGenerator.h"
#include "../ActLib/NPac.h"
#include "../SensorLib/NSignumSeparator.h"
#include "../SensorLib/NIntervalSeparator.h"
#include "../ReceiverLib/NReceptor.h"
#include "../SourceLib/NManipulatorSource.h"
#include "../SourceLib/NManipulatorSourceEmulator.h"
#include "../ReceiverLib/NManipulatorInputEmulator.h"
#include "../ReceiverLib/NManipulatorInput.h"

namespace NMSDK {

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NEngineMotionControl::NEngineMotionControl(void)
 : NumMotionElements("NumMotionElements",this,&NEngineMotionControl::SetNumMotionElements),
   CreationMode("CreationMode",this,&NEngineMotionControl::SetCreationMode),
   MotionElementClassName("MotionElementClassName",this),
   IaMin("IaMin",this),
   IaMax("IaMax",this),
   IbMin("IbMin",this),
   IbMax("IbMax",this),
   IIMin("IIMin",this),
   IIMax("IIMax",this)
{
}

NEngineMotionControl::~NEngineMotionControl(void)
{
}
// --------------------------

// --------------------------
// Методы управления параметрами
// --------------------------
// Число управляющих элементов
bool NEngineMotionControl::SetNumMotionElements(size_t value)
{
 Ready=false;
 return true;
}

// Режим формирования сети
bool NEngineMotionControl::SetCreationMode(int value)
{
 Ready=false;
 return true;
}
// --------------------------


// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NEngineMotionControl* NEngineMotionControl::New(void)
{
 return new NEngineMotionControl;
}
// --------------------------

// --------------------------
// Proctected computation methods
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NEngineMotionControl::ADefault(void)
{
 NumMotionElements=1;
 CreationMode=5;
 IaMin=-2.0*M_PI;
 IaMax=2.0*M_PI;
 IbMin=-10;
 IbMax=10;
 IIMin=-M_PI/2;
 IIMax=M_PI/2;
 MotionElementClassName="NMotionElement";

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NEngineMotionControl::ABuild(void)
{
 return true;
}

// Reset computation
bool NEngineMotionControl::AReset(void)
{
 SetNumOutputs(6);
 for(int i=0;i<NumOutputs;i++)
  SetOutputDataSize(i,1);

 receptor.resize(NumMotionElements);
 for(size_t n=0;n<NumMotionElements;n++)
 {
  receptor[n].assign(6,0);
  NAContainer* cont=0;
  try {
   cont=GetComponent(string("MotionElement")+RDK::sntoa(n));
  }
  catch (EComponentNameNotExist *exc) {
   continue;

  }
  receptor[n][0]=static_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_Ia1.Receptor"));
  receptor[n][1]=static_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_Ia2.Receptor"));
  receptor[n][2]=static_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_Ib1.Receptor"));
  receptor[n][3]=static_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_Ib2.Receptor"));
  receptor[n][4]=static_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_II1.Receptor"));
  receptor[n][5]=static_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_II2.Receptor"));
 }

 return true;
}

// Execute math. computations of current object on current step
bool NEngineMotionControl::ACalculate(void)
{
 int pos_angle=0,pos_speed=0,pos_moment=0;
 int neg_angle=0,neg_speed=0,neg_moment=0;
 // Receptors
 for(size_t i=0;i<NumMotionElements;i++)
 {
  if(receptor[i][0]->GetInputData(size_t(0))->Double[0] > 0)
   ++pos_speed;
  if(receptor[i][1]->GetInputData(size_t(0))->Double[0] > 0)
   ++neg_speed;

  if(receptor[i][2]->GetInputData(size_t(0))->Double[0] > 0)
   ++pos_moment;
  if(receptor[i][3]->GetInputData(size_t(0))->Double[0] > 0)
   ++neg_moment;

  if(receptor[i][4]->GetInputData(size_t(0))->Double[0] > 0)
   ++pos_angle;
  if(receptor[i][5]->GetInputData(size_t(0))->Double[0] > 0)
   ++neg_angle;
 }

 POutputData[0].Double[0]=pos_angle;
 POutputData[1].Double[0]=neg_angle;
 POutputData[2].Double[0]=pos_speed;
 POutputData[3].Double[0]=neg_speed;
 POutputData[4].Double[0]=pos_moment;
 POutputData[5].Double[0]=neg_moment;
 return true;
}
// --------------------------

// --------------------------
// Методы управления счетом
// --------------------------
// Создает объект с желаемой структурой в соответствии с CreationMode
bool NEngineMotionControl::Create(void)
{
 DelAllComponents();

 switch(CreationMode)
 {
 case 0:
  CreateEngineControlSignumAfferent();
 break;

 case 1:
  CreateEngineControlRangeAfferent();
 break;

 case 2:
  CreateEngineControlRangeAfferent();
 break;

 case 3:
  CreateEngineControlRangeAfferent(true);
 break;

 case 4:
  CreateEngineControlRangeAfferent(false,false);
 break;

 case 5:
  CreateEngineControlRangeAfferent(true,false);
 break;
 };

 return true;
}
// --------------------------

// --------------------------
// Вспомогательные методы
// --------------------------
// Формируем сеть управления двигателем с разделением информационного потока с датчиков
// на две полосы по знаку
NANet* NEngineMotionControl::CreateEngineControlSignumAfferent(void)
{
 UEPtr<NAContainer> cont;
 bool res;

 vector<UEPtr<NNet> > Motions;

 NANet *net=this;
 UEPtr<NStorage> storage=dynamic_pointer_cast<NStorage>(Storage);
 size_t num_motions=NumMotionElements;
 NReceptor *receptor=0;
 if(!net)
  return 0;

 // Двигательный элемент
// size_t num_motions=1;

 double exp_coeff=0.1;

 for(size_t i=0;i<num_motions;i++)
 {
  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject(MotionElementClassName));
  if(!cont)
   return 0;
  cont->SetName(string("MotionElement")+RDK::sntoa(i));
  res=net->AddComponent(cont);
  Motions.push_back(static_pointer_cast<NNet>(cont));

  receptor=dynamic_pointer_cast<NReceptor>(Motions[0]->GetComponentL("Afferent_Ia1.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=10.0/num_motions;
  receptor->InputAdaptationMode=0;
  receptor->ExpCoeff=exp_coeff;

  receptor=dynamic_pointer_cast<NReceptor>(Motions[0]->GetComponentL("Afferent_Ia2.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=10.0/num_motions;
  receptor->InputAdaptationMode=0;
  receptor->ExpCoeff=exp_coeff;

  receptor=dynamic_pointer_cast<NReceptor>(Motions[0]->GetComponentL("Afferent_Ib1.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=10.0/num_motions;
  receptor->InputAdaptationMode=0;
  receptor->ExpCoeff=exp_coeff;

  receptor=dynamic_pointer_cast<NReceptor>(Motions[0]->GetComponentL("Afferent_Ib2.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=10.0/num_motions;
  receptor->InputAdaptationMode=0;
  receptor->ExpCoeff=exp_coeff;

  receptor=dynamic_pointer_cast<NReceptor>(Motions[0]->GetComponentL("Afferent_II1.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=3.14/num_motions;
  receptor->InputAdaptationMode=0;
  receptor->ExpCoeff=exp_coeff;


  receptor=dynamic_pointer_cast<NReceptor>(Motions[0]->GetComponentL("Afferent_II2.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=3.14/num_motions;
  receptor->InputAdaptationMode=0;
  receptor->ExpCoeff=exp_coeff;
 }

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NCGenerator"));
 if(!cont)
  return 0;
 cont->SetName("AfferentSource1");
 static_pointer_cast<NConstGenerator>(cont)->Amplitude=0;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NCGenerator"));
 if(!cont)
  return 0;
 cont->SetName("AfferentSource2");
 static_pointer_cast<NConstGenerator>(cont)->Amplitude=0;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NCGenerator"));
 if(!cont)
  return 0;
 cont->SetName("LengthSource1");
 static_pointer_cast<NConstGenerator>(cont)->Amplitude=0;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPGenerator"));
 if(!cont)
  return 0;
 cont->SetName("Renshow1ActivatorGenerator");
 static_pointer_cast<NPulseGenerator>(cont)->Frequency=0;
 static_pointer_cast<NPulseGenerator>(cont)->Amplitude=1;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPGenerator"));
 if(!cont)
  return 0;
 cont->SetName("Renshow2ActivatorGenerator");
 static_pointer_cast<NPulseGenerator>(cont)->Frequency=0;
 static_pointer_cast<NPulseGenerator>(cont)->Amplitude=1;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPGenerator"));
 if(!cont)
  return 0;
 cont->SetName("Renshow1DeactivatorGenerator");
 static_pointer_cast<NPulseGenerator>(cont)->Frequency=0;
 static_pointer_cast<NPulseGenerator>(cont)->Amplitude=1;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPGenerator"));
 if(!cont)
  return 0;
 cont->SetName("Renshow2DeactivatorGenerator");
 static_pointer_cast<NPulseGenerator>(cont)->Frequency=0;
 static_pointer_cast<NPulseGenerator>(cont)->Amplitude=1;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NFrequencyReceiver"));
 if(!cont)
  return 0;
 cont->SetName("Motoneuron1FrequencyReceiver");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NFrequencyReceiver"));
 if(!cont)
  return 0;
 cont->SetName("Motoneuron2FrequencyReceiver");
 res=net->AddComponent(cont);


 // Двигатель
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NDCEngine"));
 if(!cont)
  return 0;
 cont->SetName("Engine");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NCGenerator"));
 if(!cont)
  return 0;
 cont->SetName("EngineMoment");
 static_pointer_cast<NConstGenerator>(cont)->Amplitude=0;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPac"));
 if(!cont)
  return 0;
 cont->SetName("Pac");
 res=net->AddComponent(cont);
 static_pointer_cast<NPac>(cont)->SetOutputDataSize(0,Motions.size()*2);

 // Начальные значения всем параметрам
 // Амплитуда входных импульсов
 vector<Real> values;

 values.resize(Motions.size()*2);
 for(size_t i=0;i<values.size();i++)
  values[i].assign(1,1);
 static_pointer_cast<NPac>(cont)->PulseAmplitude=values;

 // Постоянная времени выделения медиатора
 for(size_t i=0;i<values.size();i++)
  values[i].assign(1,0.05);
 static_pointer_cast<NPac>(cont)->SecretionTC=values;

 // Постоянная времени распада медиатора
 for(size_t i=0;i<values.size();i++)
  values[i].assign(1,0.5);
 static_pointer_cast<NPac>(cont)->DissociationTC=values;

 // Усиление
 for(size_t i=0;i<values.size()/2;i++)
 {
  values[i].assign(1,10.0/num_motions);
 }

 for(size_t i=values.size()/2;i<values.size();i++)
 {
  values[i].resize(1);
  values[i].assign(1,-10.0/num_motions);
 }

 static_pointer_cast<NPac>(cont)->Gain=values;

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPosSignumSeparator"));
 if(!cont)
  return 0;
 cont->SetName("Ib_PosSignumSeparator");
 static_pointer_cast<NSignumSeparator>(cont)->SetNumOutputs(1);
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NNegSignumSeparator"));
 if(!cont)
  return 0;
 cont->SetName("Ib_NegSignumSeparator");
 static_pointer_cast<NSignumSeparator>(cont)->SetNumOutputs(1);
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPosSignumSeparator"));
 if(!cont)
  return 0;
 cont->SetName("II_PosSignumSeparator");
 static_pointer_cast<NSignumSeparator>(cont)->SetNumOutputs(1);
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NNegSignumSeparator"));
 if(!cont)
  return 0;
 cont->SetName("II_NegSignumSeparator");
 static_pointer_cast<NSignumSeparator>(cont)->SetNumOutputs(1);
 res=net->AddComponent(cont);

 Real gain_value;

 cont=dynamic_pointer_cast<NSignumSeparator>(storage->TakeObject("NPosSignumSeparator"));
 if(!cont)
  return 0;
 cont->SetName("Ia_PosSignumSeparator");
 static_pointer_cast<NSignumSeparator>(cont)->SetNumOutputs(1);
 gain_value.assign(1,1.0/num_motions);
 static_pointer_cast<NSignumSeparator>(cont)->Gain=gain_value;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NNegSignumSeparator"));
 if(!cont)
  return 0;
 cont->SetName("Ia_NegSignumSeparator");
 static_pointer_cast<NSignumSeparator>(cont)->SetNumOutputs(1);
 gain_value.assign(1,1.0/num_motions);
 static_pointer_cast<NSignumSeparator>(cont)->Gain=gain_value;
 res=net->AddComponent(cont);

// return net; // Заглушка!!!

 // Установка связей
 ULongId item,conn;

 for(size_t k=0;k<Motions.size();k++)
  res=net->CreateLink(Motions[k]->GetName()+".Motoneuron1.LTZone",0,
				 "Pac");

 if(!res)
 {
  delete net;
  return 0;
 }

 for(size_t k=0;k<Motions.size();k++)
  res=net->CreateLink(Motions[k]->GetName()+".Motoneuron2.LTZone",0,
				 "Pac");
 if(!res)
 {
  delete net;
  return 0;
 }


 res=net->CreateLink("Pac",0,
				 "Engine");
 if(!res)
 {
  delete net;
  return 0;
 }


 res=net->CreateLink("Engine",2,
				 "Ia_PosSignumSeparator");
 if(!res)
 {
  delete net;
  return 0;
 }


 res=net->CreateLink("Engine",2,
				 "Ia_NegSignumSeparator");
 if(!res)
 {
  delete net;
  return 0;
 }


 res=net->CreateLink("Engine",1,
				 "II_PosSignumSeparator");
 if(!res)
 {
  delete net;
  return 0;
 }


 res=net->CreateLink("Engine",1,
				 "II_NegSignumSeparator");
 if(!res)
 {
  delete net;
  return 0;
 }


 res=net->CreateLink("Engine",0,
				 "Ib_PosSignumSeparator");
 if(!res)
 {
  delete net;
  return 0;
 }


 res=net->CreateLink("Engine",0,
				 "Ib_NegSignumSeparator");
 if(!res)
 {
  delete net;
  return 0;
 }

 res=net->CreateLink("EngineMoment",0,
				 "Engine",1);

 for(size_t k=0;k<Motions.size();k++)
 {
  res=net->CreateLink("Ia_PosSignumSeparator",0,Motions[k]->GetName()+".Afferent_Ia2.Receptor");
  if(!res)
  {
   delete net;
   return 0;
  }
  res=net->CreateLink("Ia_NegSignumSeparator",0,Motions[k]->GetName()+".Afferent_Ia1.Receptor");
  if(!res)
  {
   delete net;
   return 0;
  }

  res=net->CreateLink("II_PosSignumSeparator",0,Motions[k]->GetName()+".Afferent_II1.Receptor");
  if(!res)
  {
   delete net;
   return 0;
  }
  res=net->CreateLink("II_NegSignumSeparator",0,Motions[k]->GetName()+".Afferent_II2.Receptor");
  if(!res)
  {
   delete net;
   return 0;
  }

  res=net->CreateLink("Ib_NegSignumSeparator",0,Motions[k]->GetName()+".Afferent_Ib1.Receptor");
  if(!res)
  {
   delete net;
   return 0;
  }
  res=net->CreateLink("Ib_PosSignumSeparator",0,Motions[k]->GetName()+".Afferent_Ib2.Receptor");
  if(!res)
  {
   delete net;
   return 0;
  }

  res=net->CreateLink("Renshow1ActivatorGenerator",0,Motions[k]->GetName()+".Motoneuron1.PNeuronMembrane2.PosChannel");
  if(!res)
  {
   delete net;
   return 0;
  }

  res=net->CreateLink("Renshow1DeactivatorGenerator",0,Motions[k]->GetName()+".Motoneuron1.PNeuronMembrane2.NegChannel");
  if(!res)
  {
   delete net;
   return 0;
  }

  res=net->CreateLink("Renshow1ActivatorGenerator",0,Motions[k]->GetName()+".Motoneuron2.PNeuronMembrane2.NegChannel");
  if(!res)
  {
   delete net;
   return 0;
  }

  res=net->CreateLink("Renshow1DeactivatorGenerator",0,Motions[k]->GetName()+".Motoneuron2.PNeuronMembrane2.PosChannel");
  if(!res)
  {
   delete net;
   return 0;
  }

 }

 return net;
}

// Формируем сеть управления двигателем c разделением информационного потока с датчиков
// на полосы по амплитуде
NANet* NEngineMotionControl::CreateEngineControlRangeAfferent(bool crosslinks, bool crossranges)

{
 NAContainer *cont;
 bool res;
 NReceptor *receptor=0;
 UEPtr<NStorage> storage=static_pointer_cast<NStorage>(Storage);
 size_t num_motions=NumMotionElements;
 vector<pair<double,double> > Ia_ranges_pos,Ia_ranges_neg;
 vector<pair<double,double> > Ib_ranges_pos,Ib_ranges_neg;
 vector<pair<double,double> > II_ranges_pos,II_ranges_neg;

 // Число неперекрывающихся диапазонов
 int real_ranges;

 if(crossranges)
  real_ranges=num_motions/2+1;
 else
  real_ranges=num_motions;
 int num_ranges=num_motions;

 Ia_ranges_pos.resize(num_motions);
 Ib_ranges_pos.resize(num_motions);
 II_ranges_pos.resize(num_motions);
 Ia_ranges_neg.resize(num_motions);
 Ib_ranges_neg.resize(num_motions);
 II_ranges_neg.resize(num_motions);

 int rr_index=0;

 if(crossranges)
 {
 for(size_t i=0;i<num_motions;i++)
 {
  if(!(i % 2)) // четное
  {
   real left_range=IaMin,right_range=IaMax;
   real pos_range=(right_range-0)/real_ranges;
   real neg_range=(0-left_range)/real_ranges;

   Ia_ranges_pos[i].first=rr_index*pos_range;
   Ia_ranges_pos[i].second=(rr_index+1)*pos_range;
   Ia_ranges_neg[i].first=left_range+rr_index*neg_range;
   Ia_ranges_neg[i].second=left_range+(rr_index+1)*neg_range;

   left_range=IbMin,right_range=IbMax;
   pos_range=(right_range-0)/real_ranges;
   neg_range=(0-left_range)/real_ranges;

   Ib_ranges_pos[i].first=rr_index*pos_range;
   Ib_ranges_pos[i].second=(rr_index+1)*pos_range;
   Ib_ranges_neg[i].first=left_range+rr_index*neg_range;
   Ib_ranges_neg[i].second=left_range+(rr_index+1)*neg_range;

   left_range=IIMin,right_range=IIMax;
   pos_range=(right_range-0)/real_ranges;
   neg_range=(0-left_range)/real_ranges;

   II_ranges_pos[i].first=rr_index*pos_range;
   II_ranges_pos[i].second=(rr_index+1)*pos_range;
   II_ranges_neg[i].first=left_range+rr_index*neg_range;
   II_ranges_neg[i].second=left_range+(rr_index+1)*neg_range;
  }
  else // нечетное
  {
   real left_range=IaMin,right_range=IaMax;
   real pos_range=(right_range-0)/real_ranges;
   real neg_range=(0-left_range)/real_ranges;

   Ia_ranges_pos[i].first=(rr_index+0.5)*pos_range;
   Ia_ranges_pos[i].second=(rr_index+1.5)*pos_range;
   Ia_ranges_neg[i].first=left_range+(rr_index+0.5)*neg_range;
   Ia_ranges_neg[i].second=left_range+(rr_index+1.5)*neg_range;

   left_range=IbMin,right_range=IbMax;
   pos_range=(right_range-0)/real_ranges;
   neg_range=(0-left_range)/real_ranges;

   Ib_ranges_pos[i].first=(rr_index+0.5)*pos_range;
   Ib_ranges_pos[i].second=(rr_index+1.5)*pos_range;
   Ib_ranges_neg[i].first=left_range+(rr_index+0.5)*neg_range;
   Ib_ranges_neg[i].second=left_range+(rr_index+1.5)*neg_range;

   left_range=IIMin,right_range=IIMax;
   pos_range=(right_range-0)/real_ranges;
   neg_range=(0-left_range)/real_ranges;

   II_ranges_pos[i].first=(rr_index+0.5)*pos_range;
   II_ranges_pos[i].second=(rr_index+1.5)*pos_range;
   II_ranges_neg[i].first=left_range+(rr_index+0.5)*neg_range;
   II_ranges_neg[i].second=left_range+(rr_index+1.5)*neg_range;

   ++rr_index;
  }
 }
 }
 else
 {
 for(size_t i=0;i<num_motions;i++)
 {
   real left_range=IaMin,right_range=IaMax;
   real pos_range=(right_range-0)/real_ranges;
   real neg_range=(0-left_range)/real_ranges;

   Ia_ranges_pos[i].first=rr_index*pos_range;
   Ia_ranges_pos[i].second=(rr_index+1)*pos_range;
   Ia_ranges_neg[i].first=left_range+rr_index*neg_range;
   Ia_ranges_neg[i].second=left_range+(rr_index+1)*neg_range;

   left_range=IbMin,right_range=IbMax;
   pos_range=(right_range-0)/real_ranges;
   neg_range=(0-left_range)/real_ranges;

   Ib_ranges_pos[i].first=rr_index*pos_range;
   Ib_ranges_pos[i].second=(rr_index+1)*pos_range;
   Ib_ranges_neg[i].first=left_range+rr_index*neg_range;
   Ib_ranges_neg[i].second=left_range+(rr_index+1)*neg_range;

   left_range=IIMin,right_range=IIMax;
   pos_range=(right_range-0)/real_ranges;
   neg_range=(0-left_range)/real_ranges;

   II_ranges_pos[i].first=rr_index*pos_range;
   II_ranges_pos[i].second=(rr_index+1)*pos_range;
   II_ranges_neg[i].first=left_range+rr_index*neg_range;
   II_ranges_neg[i].second=left_range+(rr_index+1)*neg_range;
   ++rr_index;
 }
 }

 vector<NNet*> Motions;

 NANet *net=this;//dynamic_cast<NANet*>(storage->TakeObject(netclassname));
 if(!net)
  return 0;

 int outmode=1;
 int inpmode=0;

 double exp_coeff=0.0001;//0.00001;

 // Двигательные элементы
 for(size_t i=0;i<num_motions;i++)
 {
  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject(MotionElementClassName));
  if(!cont)
   return 0;
  cont->SetName(string("MotionElement")+RDK::sntoa(i));
  res=net->AddComponent(cont);
  Motions.push_back(static_cast<NNet*>(cont));

  receptor=dynamic_pointer_cast<NReceptor>(Motions[i]->GetComponentL("Afferent_Ia1.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=fabs(IaMin)/real_ranges;
  receptor->InputAdaptationMode=inpmode;
  receptor->OutputAdaptationMode=outmode;
  receptor->ExpCoeff=exp_coeff;

  receptor=dynamic_pointer_cast<NReceptor>(Motions[i]->GetComponentL("Afferent_Ia2.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=fabs(IaMax)/real_ranges;
  receptor->InputAdaptationMode=inpmode;
  receptor->OutputAdaptationMode=outmode;
  receptor->ExpCoeff=exp_coeff;

  receptor=dynamic_pointer_cast<NReceptor>(Motions[i]->GetComponentL("Afferent_Ib1.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=fabs(IbMin)/real_ranges;
  receptor->InputAdaptationMode=inpmode;
  receptor->OutputAdaptationMode=outmode;
  receptor->ExpCoeff=exp_coeff;

  receptor=dynamic_pointer_cast<NReceptor>(Motions[i]->GetComponentL("Afferent_Ib2.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=fabs(IbMax)/real_ranges;
  receptor->InputAdaptationMode=inpmode;
  receptor->OutputAdaptationMode=outmode;
  receptor->ExpCoeff=exp_coeff;

  receptor=dynamic_pointer_cast<NReceptor>(Motions[i]->GetComponentL("Afferent_II1.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=fabs(IIMin)/real_ranges;
  receptor->InputAdaptationMode=inpmode;
  receptor->OutputAdaptationMode=outmode;
  receptor->ExpCoeff=exp_coeff;


  receptor=dynamic_pointer_cast<NReceptor>(Motions[i]->GetComponentL("Afferent_II2.Receptor"));
  receptor->MinInputRange=0;
  receptor->MaxInputRange=fabs(IIMax)/real_ranges;
  receptor->InputAdaptationMode=inpmode;
  receptor->OutputAdaptationMode=outmode;
  receptor->ExpCoeff=exp_coeff;
 }


 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NCGenerator"));
 if(!cont)
  return 0;
 cont->SetName("AfferentSource1");
 ((NConstGenerator*)cont)->Amplitude=0;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NCGenerator"));
 if(!cont)
  return 0;
 cont->SetName("AfferentSource2");
 ((NConstGenerator*)cont)->Amplitude=0;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NCGenerator"));
 if(!cont)
  return 0;
 cont->SetName("LengthSource1");
 ((NConstGenerator*)cont)->Amplitude=0;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPGenerator"));
 if(!cont)
  return 0;
 cont->SetName("Renshow1ActivatorGenerator");
 ((NPulseGenerator*)cont)->Frequency=0;
 ((NPulseGenerator*)cont)->Amplitude=1;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPGenerator"));
 if(!cont)
  return 0;
 cont->SetName("Renshow2ActivatorGenerator");
 ((NPulseGenerator*)cont)->Frequency=0;
 ((NPulseGenerator*)cont)->Amplitude=1;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPGenerator"));
 if(!cont)
  return 0;
 cont->SetName("Renshow1DeactivatorGenerator");
 ((NPulseGenerator*)cont)->Frequency=0;
 ((NPulseGenerator*)cont)->Amplitude=1;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPGenerator"));
 if(!cont)
  return 0;
 cont->SetName("Renshow2DeactivatorGenerator");
 ((NPulseGenerator*)cont)->Frequency=0;
 ((NPulseGenerator*)cont)->Amplitude=1;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NFrequencyReceiver"));
 if(!cont)
  return 0;
 cont->SetName("Motoneuron1FrequencyReceiver");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NFrequencyReceiver"));
 if(!cont)
  return 0;
 cont->SetName("Motoneuron2FrequencyReceiver");
 res=net->AddComponent(cont);


 // Двигатель
 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NDCEngine"));
 if(!cont)
  return 0;
 cont->SetName("Engine");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NCGenerator"));
 if(!cont)
  return 0;
 cont->SetName("EngineMoment");
 ((NConstGenerator*)cont)->Amplitude=0;
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NManipulatorSource"));
 if(!cont)
  return 0;
 cont->SetName("NManipulatorSource1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NManipulatorSourceEmulator"));
 if(!cont)
  return 0;
 cont->SetName("NManipulatorSourceEmulator1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NManipulatorInput"));
 if(!cont)
  return 0;
 cont->SetName("NManipulatorInput1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NManipulatorInputEmulator"));
 if(!cont)
  return 0;
 cont->SetName("NManipulatorInputEmulator1");
 res=net->AddComponent(cont);

 cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NPac"));
 if(!cont)
  return 0;
 cont->SetName("Pac");
 res=net->AddComponent(cont);
 ((NPac*)cont)->SetOutputDataSize(0,Motions.size()*2);

 // Начальные значения всем параметрам
 // Амплитуда входных импульсов
 vector<Real> values;

 values.resize(Motions.size()*2);
 for(size_t i=0;i<values.size();i++)
//  values[i].assign(2,1);
  values[i].assign(1,1);
 ((NPac*)cont)->PulseAmplitude=values;

 // Постоянная времени выделения медиатора
 for(size_t i=0;i<values.size();i++)
//  values[i].assign(2,0.05);
  values[i].assign(1,0.001);
 ((NPac*)cont)->SecretionTC=values;

 // Постоянная времени распада медиатора
 for(size_t i=0;i<values.size();i++)
  values[i].assign(1,0.01);
//  values[i].assign(2,0.5);
 ((NPac*)cont)->DissociationTC=values;

 // Усиление
 for(size_t i=0;i<values.size()/2;i++)
 {
//  values[i].assign(1,100.0);
  values[i].assign(1,100.0/Motions.size());
 }

 for(size_t i=values.size()/2;i<values.size();i++)
 {
//  values[i].assign(1,-100.0);
  values[i].assign(1,-100.0/Motions.size());
 }

 ((NPac*)cont)->Gain=values;

// real left_range=Ib_range.first,right_range=Ib_range.second; //15
// real pos_range=(right_range-0)/num_ranges;
// real neg_range=(0-left_range)/num_ranges;
 Real left_value,right_value;
 Real pos_gain,neg_gain;

 vector<int> mode;
 mode.assign(1,5);

 pos_gain.assign(1,1);
// neg_gain.assign(1,1);
 neg_gain.assign(1,-1);

 for(int i=0;i<num_ranges;i++)
 {
  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NIntervalSeparator"));
  if(!cont)
   return 0;
  cont->SetName(string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1));
  ((NIntervalSeparator*)cont)->SetNumOutputs(1);
  ((NIntervalSeparator*)cont)->Gain=neg_gain;
  ((NIntervalSeparator*)cont)->Mode=mode;

  left_value.assign(1,Ib_ranges_neg[i].first);
  right_value.assign(1,Ib_ranges_neg[i].second);
//  left_value.assign(1,left_range+i*neg_range);
//  right_value.assign(1,left_range+(i+1)*neg_range);
  ((NIntervalSeparator*)cont)->MinRange=left_value;
  ((NIntervalSeparator*)cont)->MaxRange=right_value;
  res=net->AddComponent(cont);
 }

 for(int i=0;i<num_ranges;i++)
 {
  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NIntervalSeparator"));
  if(!cont)
   return 0;
  cont->SetName(string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1));
  ((NIntervalSeparator*)cont)->SetNumOutputs(1);
  ((NIntervalSeparator*)cont)->Mode=mode;
  ((NIntervalSeparator*)cont)->Gain=pos_gain;

  left_value.assign(1,Ib_ranges_pos[i].first);
  right_value.assign(1,Ib_ranges_pos[i].second);
//  left_value.assign(1,0+i*pos_range);
//  right_value.assign(1,0+(i+1)*pos_range);
  ((NIntervalSeparator*)cont)->MinRange=left_value;
  ((NIntervalSeparator*)cont)->MaxRange=right_value;
  res=net->AddComponent(cont);
 }

// left_range=II_range.first,right_range=II_range.second;//M_PI*2;
// pos_range=(right_range-0)/num_ranges;
// neg_range=(0-left_range)/num_ranges;
 for(int i=0;i<num_ranges;i++)
 {
  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NIntervalSeparator"));
  if(!cont)
   return 0;
  cont->SetName(string("II_NegIntervalSeparator")+RDK::sntoa(i+1));
  ((NIntervalSeparator*)cont)->SetNumOutputs(1);
  ((NIntervalSeparator*)cont)->Mode=mode;
  ((NIntervalSeparator*)cont)->Gain=neg_gain;

  left_value.assign(1,II_ranges_neg[i].first);
  right_value.assign(1,II_ranges_neg[i].second);
//  left_value.assign(1,left_range+i*neg_range);
//  right_value.assign(1,left_range+(i+1)*neg_range);
  ((NIntervalSeparator*)cont)->MinRange=left_value;
  ((NIntervalSeparator*)cont)->MaxRange=right_value;
  res=net->AddComponent(cont);
 }

 for(int i=0;i<num_ranges;i++)
 {
  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NIntervalSeparator"));
  if(!cont)
   return 0;
  cont->SetName(string("II_PosIntervalSeparator")+RDK::sntoa(i+1));
  ((NIntervalSeparator*)cont)->SetNumOutputs(1);
  ((NIntervalSeparator*)cont)->Mode=mode;
  ((NIntervalSeparator*)cont)->Gain=pos_gain;

  left_value.assign(1,II_ranges_pos[i].first);
  right_value.assign(1,II_ranges_pos[i].second);
//  left_value.assign(1,0+i*pos_range);
//  right_value.assign(1,0+(i+1)*pos_range);
  ((NIntervalSeparator*)cont)->MinRange=left_value;
  ((NIntervalSeparator*)cont)->MaxRange=right_value;
  res=net->AddComponent(cont);
 }

// left_range=Ia_range.first,right_range=Ia_range.second;//15
// pos_range=(right_range-0)/num_ranges;
// neg_range=(0-left_range)/num_ranges;
 for(int i=0;i<num_ranges;i++)
 {
  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NIntervalSeparator"));
  if(!cont)
   return 0;
  cont->SetName(string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1));
  ((NIntervalSeparator*)cont)->SetNumOutputs(1);
  ((NIntervalSeparator*)cont)->Mode=mode;
  ((NIntervalSeparator*)cont)->Gain=neg_gain;

  left_value.assign(1,Ia_ranges_neg[i].first);
  right_value.assign(1,Ia_ranges_neg[i].second);
//  left_value.assign(1,left_range+i*neg_range);
//  right_value.assign(1,left_range+(i+1)*neg_range);
  ((NIntervalSeparator*)cont)->MinRange=left_value;
  ((NIntervalSeparator*)cont)->MaxRange=right_value;
  res=net->AddComponent(cont);
 }

 for(int i=0;i<num_ranges;i++)
 {
  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NIntervalSeparator"));
  if(!cont)
   return 0;
  cont->SetName(string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1));
  ((NIntervalSeparator*)cont)->SetNumOutputs(1);
  ((NIntervalSeparator*)cont)->Mode=mode;
  ((NIntervalSeparator*)cont)->Gain=pos_gain;

  left_value.assign(1,Ia_ranges_pos[i].first);
  right_value.assign(1,Ia_ranges_pos[i].second);
//  left_value.assign(1,0+i*pos_range);
//  right_value.assign(1,0+(i+1)*pos_range);
  ((NIntervalSeparator*)cont)->MinRange=left_value;
  ((NIntervalSeparator*)cont)->MaxRange=right_value;
  res=net->AddComponent(cont);
 }

 // Компоненты вычисления статистики
 for(size_t i=0;i<num_motions;i++)
 {
  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NFrequencyReceiver"));
  if(!cont)
   return 0;
  cont->SetName("PosMNFrequencyReceiver"+RDK::sntoa(i+1));
  res=net->AddComponent(cont);

  cont=dynamic_pointer_cast<NAContainer>(storage->TakeObject("NFrequencyReceiver"));
  if(!cont)
   return 0;
  cont->SetName("NegMNFrequencyReceiver"+RDK::sntoa(i+1));
  res=net->AddComponent(cont);
 }


 // Установка связей
 ULongId item,conn;

 for(size_t k=0;k<Motions.size();k++)
  res=net->CreateLink(Motions[k]->GetName()+".Motoneuron1.LTZone",0,
				 "Pac");

 for(size_t k=0;k<Motions.size();k++)
  res=net->CreateLink(Motions[k]->GetName()+".Motoneuron2.LTZone",0,
                 "Pac");

 res=net->CreateLink("Pac",0,"NManipulatorInput1");

 res=net->CreateLink("Pac",0,"NManipulatorInputEmulator1");

 res=net->CreateLink("NManipulatorInputEmulator1",0,"Engine");

 res=net->CreateLink("Engine",0,"NManipulatorSourceEmulator1",0);
 res=net->CreateLink("Engine",1,"NManipulatorSourceEmulator1",1);
 res=net->CreateLink("Engine",2,"NManipulatorSourceEmulator1",2);


 res=net->CreateLink("EngineMoment",0,
				 "Engine",1);

 // Связи с моделью манипулятора (по умолчанию)
 for(int i=0;i<num_ranges;i++)
 {
  res=net->CreateLink("NManipulatorSourceEmulator1",2,
                 string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1));
  res=net->CreateLink("NManipulatorSourceEmulator1",2,
                 string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1));
 }

 for(int i=0;i<num_ranges;i++)
 {
  res=net->CreateLink("NManipulatorSourceEmulator1",1,
                 string("II_PosIntervalSeparator")+RDK::sntoa(i+1));
  res=net->CreateLink("NManipulatorSourceEmulator1",1,
                 string("II_NegIntervalSeparator")+RDK::sntoa(i+1));
 }

 for(int i=0;i<num_ranges;i++)
 {
  res=net->CreateLink("NManipulatorSourceEmulator1",0,
                 string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1));
  res=net->CreateLink("NManipulatorSourceEmulator1",0,
                 string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1));
 }

      /*
 for(int i=0;i<num_ranges;i++)
 {
  res=net->CreateLink("Engine",2,
                 string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1));
  res=net->CreateLink("Engine",2,
                 string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1));
 }

 for(int i=0;i<num_ranges;i++)
 {
  res=net->CreateLink("Engine",1,
                 string("II_PosIntervalSeparator")+RDK::sntoa(i+1));
  res=net->CreateLink("Engine",1,
                 string("II_NegIntervalSeparator")+RDK::sntoa(i+1));
 }

 for(int i=0;i<num_ranges;i++)
 {
  res=net->CreateLink("Engine",0,
                 string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1));
  res=net->CreateLink("Engine",0,
                 string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1));
 }
	 */


 for(size_t k=0;k<Motions.size();k++)
 {
  res=net->CreateLink(string("Ia_PosIntervalSeparator")+RDK::sntoa(k+1),0,Motions[k]->GetName()+".Afferent_Ia2.Receptor");
  res=net->CreateLink(string("Ia_NegIntervalSeparator")+RDK::sntoa(k+1),0,Motions[k]->GetName()+".Afferent_Ia1.Receptor");

  res=net->CreateLink(string("II_PosIntervalSeparator")+RDK::sntoa(k+1),0,Motions[k]->GetName()+".Afferent_II1.Receptor");
  res=net->CreateLink(string("II_NegIntervalSeparator")+RDK::sntoa(k+1),0,Motions[k]->GetName()+".Afferent_II2.Receptor");

  res=net->CreateLink(string("Ib_NegIntervalSeparator")+RDK::sntoa(k+1),0,Motions[k]->GetName()+".Afferent_Ib2.Receptor");
  res=net->CreateLink(string("Ib_PosIntervalSeparator")+RDK::sntoa(k+1),0,Motions[k]->GetName()+".Afferent_Ib1.Receptor");
 }


 // Устанавливаем перекрестные связи, если они нужны
 if(crosslinks)
 {
  for(size_t k=1;k<Motions.size()-1;k++)
  {
   res=net->CreateLink(Motions[k]->GetName()+".Renshow1.LTZone",0,Motions[k-1]->GetName()+".Motoneuron1.PNeuronMembrane.NegChannel");
   res=net->CreateLink(Motions[k]->GetName()+".Renshow1.LTZone",0,Motions[k+1]->GetName()+".Motoneuron1.PNeuronMembrane.NegChannel");
   res=net->CreateLink(Motions[k]->GetName()+".Renshow2.LTZone",0,Motions[k-1]->GetName()+".Motoneuron2.PNeuronMembrane.NegChannel");
   res=net->CreateLink(Motions[k]->GetName()+".Renshow2.LTZone",0,Motions[k+1]->GetName()+".Motoneuron2.PNeuronMembrane.NegChannel");

   res=net->CreateLink(Motions[k]->GetName()+".Renshow1.LTZone",0,Motions[k-1]->GetName()+".Motoneuron1.PNeuronMembrane.NegChannel");
   res=net->CreateLink(Motions[k]->GetName()+".Renshow1.LTZone",0,Motions[k+1]->GetName()+".Motoneuron1.PNeuronMembrane.NegChannel");
   res=net->CreateLink(Motions[k]->GetName()+".Renshow2.LTZone",0,Motions[k-1]->GetName()+".Motoneuron2.PNeuronMembrane.NegChannel");
   res=net->CreateLink(Motions[k]->GetName()+".Renshow2.LTZone",0,Motions[k+1]->GetName()+".Motoneuron2.PNeuronMembrane.NegChannel");

// neuron=dynamic_cast<NPulseNeuron*>(net->GetComponent("Motoneuron1"));
// branch=neuron->BranchDendrite(neuron->GetComponentId("PNeuronMembrane"),true);
// synapse=dynamic_cast<NPulseSynapse*>(branch->GetComponentL("NegChannel.Synapse"));
  }

 }

 for(size_t k=0;k<Motions.size();k++)
 {
  res=net->CreateLink(Motions[k]->GetName()+".Motoneuron1.LTZone",0,string("PosMNFrequencyReceiver")+RDK::sntoa(k+1));
  res=net->CreateLink(Motions[k]->GetName()+".Motoneuron2.LTZone",0,string("NegMNFrequencyReceiver")+RDK::sntoa(k+1));
 }

 if(!res)
  return 0;

 return net;
}
// --------------------------

}
