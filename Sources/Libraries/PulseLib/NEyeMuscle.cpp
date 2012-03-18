// ===========================================================
// Version:        3.0.2
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

#ifndef NEYEMUSCLE_CPP
#define NEYEMUSCLE_CPP

//#pragma hdrstop

#include "NEyeMuscle.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NEyeMuscle::NEyeMuscle(void)
//: NADItem(name),
 : MulCoeffs("MulCoeffs",this),
  K("K",this),
  TC("TC",this)
{
 // Устанавливаем новые параметры
// AddLookupParameter("MulCoeffs",MulCoeffs);
// AddLookupParameter("K",K);
// AddLookupParameter("TC",TC);
}

NEyeMuscle::~NEyeMuscle(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду синуса
bool NEyeMuscle::SetAmplitude(real value)
{
 return true;
}

// Устанавливает частоту
bool NEyeMuscle::SetFrequency(real value)
{
 if(value <=0)
  return false;

 return true;
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NEyeMuscle* NEyeMuscle::New(void)
{
 return new NEyeMuscle;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NEyeMuscle::ADefault(void)
{
 Real value;
 value.resize(3);
 value[0]=0.4;
 value[1]=0.12;
 value[2]=0.0015;
 MulCoeffs=value;

 K=0.2;

 value.resize(3);
 value[0]=1;
 value[1]=1;
 value[2]=1;
 TC=value;
 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NEyeMuscle::ABuild(void)
{
 P1.resize(GetOutputDataSize(0));
 P2.resize(GetOutputDataSize(0));
 P3.resize(GetOutputDataSize(0));
 L.resize(GetOutputDataSize(0));

 Threshold.assign(GetOutputDataSize(0),0.5);

 return true;
}

// Сброс процесса счета.
bool NEyeMuscle::AReset(void)
{
 P1.assign(GetOutputDataSize(0),0);
 P2.assign(GetOutputDataSize(0),0);
 P3.assign(GetOutputDataSize(0),0);
 L.assign(GetOutputDataSize(0),0);

 // Порог
 Threshold.assign(GetOutputDataSize(0),0.5);

 return true;
}

// Выполняет расчет этого объекта
bool NEyeMuscle::ACalculate(void)
{
 size_t k=0;
 for(int i=0;i<NumInputs;i++)
  for(size_t j=0;j<GetInputDataSize(i);j++)
  {
   if(k >= GetOutputDataSize(0))
	break;

   real in=GetInputData(i)->Double[j];
   in/=100;
   ThresholdCount(k);
   in*=Threshold[k];

   L[k]=MuscularReduction(k,in)*K;
   POutputData[0].Double[k]=L[k];
   ++k;
  }

 return true;
}
// --------------------------


// --------------------------
// Дополнительные скрытые методы управления счетом
// --------------------------
// мускульное сокращение
real NEyeMuscle::MuscularReduction(size_t k,real in)
{
 P1[k]=(P1[k]+in-P3[k]*MulCoeffs[2]-P1[k]*MulCoeffs[0])/TC[0];
 P2[k]=(P2[k]+P1[k]-P2[k]*MulCoeffs[1])/TC[1];
 P3[k]=(P3[k]+P2[k])/TC[2];
 return P3[k];
}


// Пороговая функция
void NEyeMuscle::ThresholdCount(size_t k)
{
 Threshold[k]+=0.4*L[k]-0.005*L[k]*L[k];
 if(Threshold[k]>1.) Threshold[k]=1.;
 if(Threshold[k]<0.) Threshold[k]=0.;
}
// --------------------------
}
//---------------------------------------------------------------------------
#endif
