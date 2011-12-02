// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2011.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
//---------------------------------------------------------------------------
#ifndef NWPhysicalManipulatorCPP
#define NWPhysicalManipulatorCPP

#include "NWPhysicalManipulator.h"

namespace NMSDK {

/* *************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NWPhysicalManipulator::NWPhysicalManipulator(void)
// : NADItem(name),
{
 ManipulatorDLL=0;
 DLLManipulatorInit=0;
 DLLManipulatorDeInit=0;
 DLLManipulatorComOpen=0;
 DLLManipulatorComClose=0;
 DLLManipulatorComStatus=0;
 DLLManipulatorStart=0;
 DLLManipulatorStop=0;
 DLLManipulatorReset=0;
 DLLManipulatorMoveServo=0;
 DLLManipulatorGetServoData=0;
 DLLManipulatorSetExternalData=0;
 DLLManipulatorGetModelTime=0;

 DLLManipulatorGetState=0;
 DLLManipulatorNeiroPulse=0;
 DLLManipulatorNeiroPulseGroup=0;
 DLLManipulatorGetNeiroSumm=0;
 DLLManipulatorSetNeiroParam=0;
 DLLManipulatorSetWorkMode=0;

 WindowHandle=0;
}

NWPhysicalManipulator::~NWPhysicalManipulator(void)
{
 UnInitManipulator();
 UnLoadManipulatorDll();
}
// --------------------------

// --------------------------
// Методы управления железом
// --------------------------
// Загрузка DLL
bool NWPhysicalManipulator::LoadManipulatorDll(void)
{
 if(!WindowHandle)
  return false;

 if(ManipulatorDLL)
  return true;

 // Идентификатор библиотеки
 ManipulatorDLL=LoadLibrary("RoboLib.dll");

 if(!ManipulatorDLL)
  return false;

 DLLManipulatorInit=(PDLLManipulatorInit)GetProcAddress(ManipulatorDLL, "Init");
 DLLManipulatorDeInit=(PDLLManipulatorDeInit)GetProcAddress(ManipulatorDLL, "DeInit");
 DLLManipulatorComOpen=(PDLLManipulatorComOpen)GetProcAddress(ManipulatorDLL, "ComOpen");
 DLLManipulatorComClose=(PDLLManipulatorComClose)GetProcAddress(ManipulatorDLL, "ComClose");
 DLLManipulatorComStatus=(PDLLManipulatorComStatus)GetProcAddress(ManipulatorDLL, "ComStatus");
 DLLManipulatorStart=(PDLLManipulatorStart)GetProcAddress(ManipulatorDLL, "Start");
 DLLManipulatorStop=(PDLLManipulatorStop)GetProcAddress(ManipulatorDLL, "Stop");
 DLLManipulatorReset=(PDLLManipulatorReset)GetProcAddress(ManipulatorDLL, "Reset");
 DLLManipulatorMoveServo=(PDLLManipulatorMoveServo)GetProcAddress(ManipulatorDLL, "MoveServo");
 DLLManipulatorGetServoData=(PDLLManipulatorGetServoData)GetProcAddress(ManipulatorDLL, "GetServoData");
 DLLManipulatorSetExternalData=(PDLLManipulatorSetExternalData)GetProcAddress(ManipulatorDLL, "SetExternalData");
 DLLManipulatorGetModelTime=(PDLLManipulatorGetModelTime)GetProcAddress(ManipulatorDLL, "GetModelTime");

 DLLManipulatorGetState=(PDLLManipulatorGetState)GetProcAddress(ManipulatorDLL, "GetState");
 DLLManipulatorNeiroPulse=(PDLLManipulatorNeiroPulse)GetProcAddress(ManipulatorDLL, "NeiroPulse");
 DLLManipulatorNeiroPulseGroup=(PDLLManipulatorNeiroPulseGroup)GetProcAddress(ManipulatorDLL, "NeiroPulseGroup");

 DLLManipulatorGetNeiroSumm=(PDLLManipulatorGetNeiroSumm)GetProcAddress(ManipulatorDLL, "GetNeiroSumm");
 DLLManipulatorSetNeiroParam=(PDLLManipulatorSetNeiroParam)GetProcAddress(ManipulatorDLL, "SetNeiroParam");

 DLLManipulatorSetWorkMode=(PDLLManipulatorSetWorkMode)GetProcAddress(ManipulatorDLL, "SetWorkMode");

 return true;
}

// Выгрузка DLL
bool NWPhysicalManipulator::UnLoadManipulatorDll(void)
{
 if(!ManipulatorDLL)
  return true;

 DLLManipulatorInit=0;
 DLLManipulatorDeInit=0;
 DLLManipulatorComOpen=0;
 DLLManipulatorComClose=0;
 DLLManipulatorComStatus=0;
 DLLManipulatorStart=0;
 DLLManipulatorStop=0;
 DLLManipulatorReset=0;
 DLLManipulatorMoveServo=0;
 DLLManipulatorGetServoData=0;
 DLLManipulatorSetExternalData=0;
 DLLManipulatorGetModelTime=0;

 DLLManipulatorGetState=0;
 DLLManipulatorNeiroPulse=0;
 DLLManipulatorNeiroPulseGroup=0;
 DLLManipulatorGetNeiroSumm=0;
 DLLManipulatorSetNeiroParam=0;
 DLLManipulatorSetWorkMode=0;

 FreeLibrary(ManipulatorDLL);
 ManipulatorDLL=0;

 return true;
}

// Инициализация манипулятора
bool NWPhysicalManipulator::InitManipulator(void)
{
 if(!ManipulatorDLL)
  return false;

 bool res=false;
 res=DLLManipulatorInit((void*)WindowHandle,EmulatorMode);
 res=DLLManipulatorComOpen(ComPort);
 res=DLLManipulatorReset();
// res=DLLManipulatorSetWorkMode(DllManipulatorMode);
 res=DLLManipulatorStart();
}

// Деинициализация манипулятора
bool NWPhysicalManipulator::UnInitManipulator(void)
{
 if(!ManipulatorDLL)
  return true;

 DLLManipulatorStop();
 DLLManipulatorComClose();
 DLLManipulatorDeInit();
 return true;
}

// Шаг по накоплению в контроллере за 1мс
bool NWPhysicalManipulator::SetAccumulationStep(int value)
{
 AccumulationStep=value;
 // Отправка
 if(ManipulatorDLL && !EmulatorMode && DLLManipulatorSetNeiroParam)
 {
  DLLManipulatorSetNeiroParam(AccumulationStep,DissociationStep);
 }

 return true;
}

// Шаг по разряду в контроллере за 1мс
bool NWPhysicalManipulator::SetDissociationStep(int value)
{
 DissociationStep=value;
 // Отправка
 if(ManipulatorDLL && !EmulatorMode && DLLManipulatorSetNeiroParam)
 {
  DLLManipulatorSetNeiroParam(AccumulationStep,DissociationStep);
 }

 return true;
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NWPhysicalManipulator* NWPhysicalManipulator::New(void)
{
 return new NWPhysicalManipulator;
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
bool NWPhysicalManipulator::SetEMFactor(real value)
{
 if(value<=0)
  return false;

 return true;
}

bool NWPhysicalManipulator::SetInductance(real value)
{
 if(value<=0)
  return false;

 return true;
}

bool NWPhysicalManipulator::SetResistance(real value)
{
 if(value<=0)
  return false;

 return true;
}

// Электромеханическая постоянная времени
bool NWPhysicalManipulator::SetTm(real value)
{
 if(value<=0)
  return false;

 return true;
}

// Передаточное число
bool NWPhysicalManipulator::SetReductionRate(real value)
{
 if(value<=0)
  return false;

 return true;
}
// --------------------------

// --------------------------
// Computation methods
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NWPhysicalManipulator::ADefault(void)
{
 SetNumOutputs(3);
 SetOutputDataSize(0,1);
 SetOutputDataSize(1,1);
 SetOutputDataSize(2,1);

 //TimeStep=1000;
 MinControlVoltage=0;//150;

// Mode=0;

 // Шаг по накоплению в контроллере за 1мс
 AccumulationStep=100;

 // Шаг по разряду в контроллере за 1мс
 DissociationStep=5;

 NumAnglesHistory=2;
 AnglesHistoryTime=0.3;

 DllManipulatorMode=2;

 // Диапазоны по току (моменту)
 MinMoment=-0.7;
 MaxMoment=0.7;

 // Диапазоны по углу
 MinAngle=0;
 MaxAngle=190;

 //Дипазоны по входному напряжению
 MinVoltage=-5;
 MaxVoltage=5;


 OutputMul=2;
 ComPort=2;
 ServoNumber=1;

 RightDirection=ServoRight;
 LeftDirection=ServoLeft;

 MaxSendCounter=20;
 MaxReadCounter=50;

 TimeDuration=1;

 EmulatorMode=true;



 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NWPhysicalManipulator::ABuild(void)
{

 return true;
}

// Reset computation
bool NWPhysicalManipulator::AReset(void)
{
// if(Activity)
// {
// }

 Params.clear();
 FoundMinForce=10000;
 FoundMaxForce=-10000;

 FoundMinSpeed=10000;
 FoundMaxSpeed=-10000;


 SendCounter=MaxSendCounter;

 LastSentTime=GetTickCount64();

 if(ManipulatorDLL && !EmulatorMode && DLLManipulatorSetWorkMode)
 {
  DLLManipulatorSetWorkMode(DllManipulatorMode);
 }

 return true;
}

// Execute math. computations of current object on current step
bool NWPhysicalManipulator::ACalculate(void)
{
 if(!ManipulatorDLL)
  return true;

 bool res;


// res=DLLManipulatorReset();
// res=DLLManipulatorComStatus();

if(ReadCounter == MaxReadCounter)
{

 unsigned char buffer[100];
 if(!DLLManipulatorGetServoData(ServoNumber,buffer))
 {
  POutputData[2].Double[0]=0.001;
  POutputData[1].Double[0]=0.001;
  POutputData[0].Double[0]=0.001;
 }
//  memcpy(buffer,(void*)param.second,18);
  unsigned char N;
  unsigned char Dir;
  double speed;
  double angle;
  double force;
  memcpy(&N,&buffer[0],1);
  memcpy(&angle,&buffer[1],8);
  memcpy(&force,&buffer[9],8);
  memcpy(&Dir,&buffer[17],1);
  memcpy(&speed,&buffer[18],8);

  int n=N;
  if(n != ServoNumber)
  {
   return true;
  }

  if(Dir<0)
  {
   force=-force;
  }

  if(FoundMinForce>force)
   FoundMinForce=force;
  if(FoundMaxForce<force)
   FoundMaxForce=force;

  MinMoment=-max(fabs(FoundMinForce),fabs(FoundMaxForce));
  MaxMoment=-MinMoment;


  angle=(angle*3.141)/180-3.14/2;
//  POutputData[1].Double[0]=((angle-MinAngle)*(3.14/2+3.14/2))/(MaxAngle-MinAngle)-3.14/2;  // Угол
  POutputData[1].Double[0]=angle;//(angle*3.141)/180-3.14/2;  // Угол

  if(MaxMoment-MinMoment != 0)
   POutputData[0].Double[0]=(((force-MinMoment)*(10+10))/(MaxMoment-MinMoment)-10);  // Момент

  PreviousAngles.push_back(POutputData[1].Double[0]);
  AnglesTimes.push_back(GetTickCount());

  while((AnglesTimes.back()-AnglesTimes.front())/1000.0 >AnglesHistoryTime)
  {
   AnglesTimes.erase(AnglesTimes.begin());
   PreviousAngles.erase(PreviousAngles.begin());
  }

  if(PreviousAngles.size()<NumAnglesHistory)
   POutputData[2].Double[0]=speed; // Угловая скорость
  else
  {
   if(!EmulatorMode)
   {
/*	if(PreviousAngles.size()>NumAnglesHistory)
	 PreviousAngles.erase(PreviousAngles.begin());

	if(AnglesTimes.size()>NumAnglesHistory)
	 AnglesTimes.erase(AnglesTimes.begin());
  */
	AngleSpeed=0;
	real moment_speed=0;
	for(size_t j=0;j<PreviousAngles.size()-1;j++)
	{
	 if(AnglesTimes[j+1]-AnglesTimes[j]>0)
	  moment_speed=(PreviousAngles[j+1]-PreviousAngles[j])/((AnglesTimes[j+1]-AnglesTimes[j])/1000.0);
	 else
	  moment_speed=0;
	 AngleSpeed+=moment_speed;
	}
	AngleSpeed/=(PreviousAngles.size()-1);
   }
   else
	AngleSpeed=speed;

   if(FoundMinSpeed>AngleSpeed)
	FoundMinSpeed=AngleSpeed;
   if(FoundMaxSpeed<AngleSpeed)
	FoundMaxSpeed=AngleSpeed;

   real minspeed=-max(fabs(FoundMinSpeed),fabs(FoundMaxSpeed));
   real maxspeed=-minspeed;
   // Масштабируем
   if(maxspeed-minspeed != 0)
	POutputData[2].Double[0]=(((AngleSpeed-minspeed)*(2.0*M_PI+2.0*M_PI))/(maxspeed-minspeed)-2.0*M_PI);  // Момент

//   POutputData[2].Double[0]=AngleSpeed; // Угловая скорость
  }

   ReadCounter=0;
}
else
 ++ReadCounter;

 if(DllManipulatorMode == 2 || EmulatorMode)
 {
  if(SendCounter == MaxSendCounter)
  {
   CurrentTime=GetTickCount();

   LastDuration=CurrentTime-LastSentTime;
   double max_duration=2;
   int int_control_duration=((double(LastDuration)*255.0/1000.0))/max_duration;
   if(int_control_duration>255)
	int_control_duration=255;

   if(NumInputs>0 && PInputDataSize[0]>0)
   {
	InputVoltage=PInputData[0]->Double[0];
	if(InputVoltage>=0)
	{
	 OutputVoltage=OutputMul*((InputVoltage-0)*(255-MinControlVoltage))/(100-0)+MinControlVoltage;
	 if(OutputVoltage>255)
	  OutputVoltage=255;
	 try {
	 res=DLLManipulatorMoveServo(ServoNumber,RightDirection,OutputVoltage,/*TimeDuration*/int_control_duration);
	 }
	 catch(...)
	 {
	  return true;
	 }
	}
	else
	{
	 OutputVoltage=-OutputMul*((fabs(InputVoltage)-0)*(255-MinControlVoltage))/(100-0)+MinControlVoltage;
	 if(OutputVoltage<-255)
	  OutputVoltage=-255;
	 try {
	 res=DLLManipulatorMoveServo(ServoNumber,LeftDirection,-OutputVoltage,int_control_duration/*TimeDuration*/);
	 }
	 catch(...)
	 {
	  return true;
	 }
	}
   }
   SendCounter=0;

   LastSentTime=GetTickCount();
  }
  else
   ++SendCounter;
 }
 else
 if(DllManipulatorMode == 3)
 {
  if(NumInputs<1)
   return true;

  PulseState.resize(NumInputs-1);
  for(size_t i=0;i<PulseState.size();i++)
  {
/*   if(PInputDataSize[i+1]<0)
   {
	PulseState[i].first=0;
	PulseState[i].second=0;
	continue;
   }
  */
   double curval=PInputData[i+1]->Double[0];

   if(curval > 0 && !(i%2))
	PulseState[i]+=1;
   else
   if(curval > 0 && (i%2))
	PulseState[i]+=-1;
  }

  if(SendCounter == MaxSendCounter)
  {

   // Отправка
   for(size_t i=0;i<PulseState.size();i++)
   {
	if(PulseState[i] >= 1)
	{
 //	 for(int k=0;k<abs(PulseState[i].first);k++)
	 {
	  res=DLLManipulatorNeiroPulse(ServoNumber, i/2, 1);
 //	  Sleep(0);
	 }
	 PulseState[i]=0;
	}
	else
	if(PulseState[i] <= -1)
	{
  //	 for(int k=0;k<abs(PulseState[i].second);k++)
	 {
	  res=DLLManipulatorNeiroPulse(ServoNumber, i/2, 0);
 //	  Sleep(0);
	 }
	 PulseState[i]=0;
	}
   }
   /*
   unsigned char group=0;
   unsigned char table[8]={1,0,3,2,5,4,7,6};
//   unsigned char table[8]={0,1,2,3,4,5,6,7};
   for(size_t i=0;i<PulseState.size();i++)
   {
	if(PulseState[i] != 0)
	{
	 group+= (unsigned char)(1)<<table[i];
	 PulseState[i]=0;
    }
   }
   res=DLLManipulatorNeiroPulseGroup(ServoNumber, group);
      */
  }
  else
  ++SendCounter;
 }

// if(!EmulatorMode)
//  POutputData[2].Double[0]=AngleSpeed;

 return true;
}
// --------------------------
/* *************************************************************************** */

}
#endif
