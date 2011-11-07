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

#include "NManipulator.h"

//---------------------------------------------------------------------------
namespace NMSDK{

/* *************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NManipulator::NManipulator(void)
// : NADItem(name),
 :  EMFactor("EMFactor",this,&NManipulator::SetEMFactor),
   Inductance("Inductance",this,&NManipulator::SetInductance),
   Resistance("Resistance",this,&NManipulator::SetResistance)
{
}

NManipulator::~NManipulator(void)
{
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NManipulator* NManipulator::New(void)
{
 return new NManipulator;
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
bool NManipulator::SetEMFactor(real value)
{
 if(value<=0)
  return false;

 return true;
}

bool NManipulator::SetInductance(real value)
{
 if(value<=0)
  return false;

 return true;
}

bool NManipulator::SetResistance(real value)
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
bool NManipulator::ADefault(void)
{
 EMFactor=1;
 Inductance=1;
 Resistance=1;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NManipulator::ABuild(void)
{

 return true;
}

// Reset computation
bool NManipulator::AReset(void)
{
 Current=0;
 return true;
}

// Execute math. computations of current object on current step
bool NManipulator::ACalculate(void)
{
 real cs;
 list<real>::iterator I,J,K,L;
 size_t k=0;

 for(int i=0;i<NumInputs;i++)
  for(size_t j=0;j<PInputDataSize[i];j++)
  {
   if(k >= GetOutputDataSize(0))
	break;

   cs=PInputData[i]->Double[j];

   Current=(cs/TimeStep-0*EMFactor)/Inductance+(1.0-Resistance/(TimeStep*Inductance))*Current;

   POutputData[0].Double[k]=Current;

   ++k;
   break;
  }


 return true;
}
// --------------------------
/* *************************************************************************** */

}
//---------------------------------------------------------------------------

