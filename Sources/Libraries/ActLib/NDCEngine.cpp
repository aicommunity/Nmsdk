// ===========================================================
// Version:        1.0.1
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:			alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#include "NDCEngine.h"

//---------------------------------------------------------------------------
namespace NMSDK{

/* *************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NDCEngine::NDCEngine(void)
// : NADItem(name),
 : EMFactor("EMFactor",this,&NDCEngine::SetEMFactor),
   Inductance("Inductance",this,&NDCEngine::SetInductance),
   Resistance("Resistance",this,&NDCEngine::SetResistance),
   Tm("Tm",this,&NDCEngine::SetTm),
   ReductionRate("ReductionRate",this,&NDCEngine::SetReductionRate),
   OutMoment("OutMoment",this)
{
// UpdateDataMethod=FullUpdate;

// AddLookupParameter("EMFactor",EMFactor);
// AddLookupParameter("Inductance",Inductance);
// AddLookupParameter("Resistance",Resistance);
// AddLookupParameter("Tm",Tm);
// AddLookupParameter("ReductionRate",ReductionRate);
}

NDCEngine::~NDCEngine(void)
{
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NDCEngine* NDCEngine::New(void)
{
 return new NDCEngine;
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
bool NDCEngine::SetEMFactor(real value)
{
 if(value<=0)
  return false;

 return true;
}

bool NDCEngine::SetInductance(real value)
{
 if(value<=0)
  return false;

 return true;
}

bool NDCEngine::SetResistance(real value)
{
 if(value<=0)
  return false;

 return true;
}

// Электромеханическая постоянная времени
bool NDCEngine::SetTm(real value)
{
 if(value<=0)
  return false;

 return true;
}

// Передаточное число
bool NDCEngine::SetReductionRate(real value)
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
bool NDCEngine::ADefault(void)
{
 EMFactor=2;
 Inductance=0.1;
 Resistance=1;
 Tm=0.1;
 ReductionRate=1;

 SetNumInputs(2);
 SetNumOutputs(3);
 SetOutputDataSize(0,1);
 SetOutputDataSize(1,1);
 SetOutputDataSize(2,1);

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NDCEngine::ABuild(void)
{

 return true;
}

// Reset computation
bool NDCEngine::AReset(void)
{
 Current=0;
 EMF=0;
 Angle=0;
 AngleSpeed=0;

 DiffMoment=0;
 return true;
}

// Execute math. computations of current object on current step
bool NDCEngine::ACalculate(void)
{
 vector<real> input;
 int k=0;

 input.resize(2);

 for(int i=0;i<NumInputs;i++)
  for(size_t j=0;j<GetInputDataSize(i);j++)
  {
   if(k >= 2)
	break;

   input[k]=GetInputData(i)->Double[j];

   ++k;
   break;
  }

 if(k == 1)
  input[1]=OutMoment();
 else
  OutMoment=input[1];

 Current=((input[0]-EMF)*Resistance)/(TimeStep*Inductance)+(1.0-Resistance/(TimeStep*Inductance))*Current;
 EMF+=(Current-input[1]*Resistance/EMFactor)/(TimeStep*Tm);

// POutputData[0].Double[0]=(-Current*EMFactor/Resistance-DiffMoment)*TimeStep();
// DiffMoment=-Current*EMFactor/Resistance; // Момент


// AngleSpeed=Angle;

// Angle+=POutputData[0].Double[0]/(ReductionRate*TimeStep());

// AngleSpeed=(Angle-AngleSpeed)*TimeStep();

 Moment=Current*EMFactor/Resistance;//EMF;

 POutputData[2].Double[0]=EMF/EMFactor; // Угловая скорость //AngleSpeed;
 Angle+=POutputData[2].Double[0]/(ReductionRate*TimeStep);
 POutputData[1].Double[0]=Angle;
 POutputData[0].Double[0]=Current*EMFactor/Resistance;
// POutputData[0].Double[0]=Angle;
// POutputData[1].Double[0]=-Current*EMFactor/Resistance;


 return true;
}
// --------------------------
/* *************************************************************************** */

}
//---------------------------------------------------------------------------

