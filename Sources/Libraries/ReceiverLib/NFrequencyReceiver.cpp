// ===========================================================
// Version:        3.0.3
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:		alexab@ailab.ru
url:		http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

//#pragma hdrstop

#include "NFrequencyReceiver.h"

//---------------------------------------------------------------------------
namespace NMSDK{

/* *************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NFrequencyReceiver::NFrequencyReceiver(void)
// : NReceiver(name),
 : LeftRange("LeftRange",this,&NFrequencyReceiver::SetLeftRange),
   RightRange("RightRange",this,&NFrequencyReceiver::SetRightRange),
   FrequencyStep("FrequencyStep",this,&NFrequencyReceiver::SetFrequencyStep),

   PulseCounter("PulseCounter",this)
{
}

NFrequencyReceiver::~NFrequencyReceiver(void)
{
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NFrequencyReceiver* NFrequencyReceiver::New(void)
{
 return new NFrequencyReceiver;
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает левую границу наблюдаемого интервала частот
bool NFrequencyReceiver::SetLeftRange(real range)
{
 if(range<0)
  return false;

 Ready=false;

 return true;
}

// Устанавливает правую границу наблюдаемого интервала частот
bool NFrequencyReceiver::SetRightRange(real range)
{
 if(range<0)
  return false;

 Ready=false;

 return true;
}

// Устанавливает шаг по частоте
bool NFrequencyReceiver::SetFrequencyStep(real step)
{
 if(step<0)
  return false;

 Ready=false;

 return true;
}
// --------------------------

// --------------------------
// Watch results control methods
// --------------------------
// Return number of results points
size_t NFrequencyReceiver::GetResultsSize(void) const
{
 return XResults.size();
}

// Return iterator pointed to farthest X result
const Real& NFrequencyReceiver::GetXResult(void) const
{
 return XResults;
}

real NFrequencyReceiver::GetXResult(int i) const
{
 return XResults[i];
}


// Return iterator pointed to farthest Y result
const Real& NFrequencyReceiver::GetYResult(void) const
{
 return YResults;
}
// --------------------------

// --------------------------
// Computation methods
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NFrequencyReceiver::ADefault(void)
{
 LeftRange=0;
 RightRange=500;
 FrequencyStep=1;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NFrequencyReceiver::ABuild(void)
{

 return true;
}

// Reset computation
bool NFrequencyReceiver::AReset(void)
{
 XResults.clear();
 YResults.clear();

 for(real f=LeftRange;f<RightRange;f+=FrequencyStep)
  {
   XResults.push_back(f);
   YResults.push_back(0);

  }

 PrevPulseStartTime=-1;
 PrevPulseStopTime=-1;
 PulseCounter=0;

 SetNumOutputs(2);
 SetOutputDataSize(1,YResults.size());
 SetOutputDataSize(0,XResults.size());

 return true;
}

// Execute math. computations of current object on current step
bool NFrequencyReceiver::ACalculate(void)
{
 real cs,frequency;
 list<real>::iterator I,J,K,L;
 size_t k=0;

 for(int i=0;i<NumInputs;i++)
  for(size_t j=0;j<GetInputDataSize(i);j++)
  {
   if(k >= GetOutputDataSize(0))
	break;

   cs=GetInputData(i)->Double[j];

   if(cs>0)
   {
	if(PrevPulseStartTime == -1)
	{
	 if(PrevPulseStopTime != -1)
	 {
	  frequency=(real)1.0/PrevPulseStopTime;
	  if(frequency >= LeftRange && frequency <= RightRange)
	  {
	   for(size_t ii=1;ii<XResults.size();ii++)
		if(frequency>=XResults[ii-1] && frequency<XResults[ii])
		 ++YResults[ii-1];

	   ++PulseCounter.v;
	  }


	  PrevPulseStartTime=0;
	  PrevPulseStopTime=-1;
	 }
	 else
	 {
	  PrevPulseStartTime+=1.0/TimeStep;
	 }

	 for(size_t i=0;i<YResults.size();i++)
	  POutputData[1].Double[i]=YResults[i];
	 for(size_t i=0;i<XResults.size();i++)
	  POutputData[0].Double[i]=XResults[i];
	 return true;
	}
	else
	{
	 PrevPulseStartTime+=1.0/TimeStep;
	}
   }
   else
   {
	if(PrevPulseStartTime != -1)
	{
	 PrevPulseStopTime=PrevPulseStartTime;
	 PrevPulseStartTime=-1;
	}
	else
	if(PrevPulseStopTime>=0)
	 PrevPulseStopTime+=1.0/TimeStep;
   }

   ++k;
   break;
  }

 for(size_t i=0;i<YResults.size();i++)
  POutputData[1].Double[i]=YResults[i];
 for(size_t i=0;i<XResults.size();i++)
  POutputData[0].Double[i]=XResults[i];

/* cs=InputConnector->GetInputStatus();
 if(cs)
  {
   if(RealCompare(cs,NControl::GetTime()))
	{
	 if(PrevPulseTime == -1)
	  {
	   PrevPulseTime=cs;
	   return;
	  }

	 frequency=(real)1.0/(cs-PrevPulseTime);
	 PrevPulseTime=cs;

	 I=XResults.begin(); J=YTemp.begin();
	 if(frequency < XResults.front() || frequency > XResults.back())
	  return;

	 while(I != XResults.end())
	  {
	   if(frequency >= *I-FrequencyStep && frequency <= *I+FrequencyStep)
		{
		 (*J)+=1;
		 PulseCounter++;

		 K=YResults.begin();
		 L=YTemp.begin();
		 while(K != YResults.end())
		  {
		   *K=*L/PulseCounter;
		   L++; K++;
		  }

		 break;
		}

	   I++; J++;
	  }
	}
  }    */

 return true;
}
// --------------------------
/* *************************************************************************** */

}
//---------------------------------------------------------------------------

