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

#ifndef NMUSCLE_CPP
#define NMUSCLE_CPP
//#pragma hdrstop

#include "../BCL/NItem.h"
#include "NMuscle.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NMuscle::NMuscle(void)
//: NADItem(name),
 : MulCoeffs("MulCoeffs",this),
  Param("Param",this),
  TC("TC",this),
  Threshold("Threshold",this),
  Mass("Mass",this),
  G("G",this)
{
 // Устанавливаем новые параметры
/* AddLookupParameter("MulCoeffs",MulCoeffs);
 AddLookupParameter("Param",Param);
 AddLookupParameter("TC",TC);

 AddLookupParameter("Threshold",Threshold);
 AddLookupParameter("Mass",Mass);
 AddLookupParameter("G",G);
  */
// Указатель на вход по длине
 LengthInput=0;
/*
 ExternalForce=0;

 // Указатели на дополнительные выходы
 // Активная сила
 ActivePower=0;

 // Длина
 Length=0;

 // Веретена
 Spindle1=Spindle2=0;

 // Сухожильный орган Гольджи
 Tendon=0;  */
}

NMuscle::~NMuscle(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------

// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NMuscle* NMuscle::New(void)
{
 return new NMuscle;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NMuscle::CheckComponentType(UEPtr<NAContainer> comp) const
{
 if(//dynamic_cast<const NItem*>(comp) ||
	dynamic_pointer_cast<NReceptor>(comp))
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
bool NMuscle::AAddComponent(UEPtr<UAContainer> comp, UEPtr<UIPointer> pointer)
{
/* NItem* item=dynamic_cast<NItem*>(comp);
 if(item)
 {
  // Указатели на дополнительные выходы
  if(!ActivePower)
   ActivePower=item;
  else
  if(!Length)
   Length=item;
  else
  if(!Spindle1)
   Spindle1=item;
  else
  if(!Spindle2)
   Spindle2=item;
  else
  if(!Tendon)
   Tendon=item;
  else
   return false;

  item->OutputSize=OutputSize;
  return true;
 }             */

 UEPtr<NReceptor> input=dynamic_pointer_cast<NReceptor>(comp);
 if(input)
 {
/*  if(!ExternalForce)
   ExternalForce=input;
  else*/
  if(!LengthInput)
   LengthInput=input;
  else
   return false;
 }


 return true;
}


// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
bool NMuscle::ADelComponent(UEPtr<UAContainer> comp)
{
  // Указатели на дополнительные выходы
/*  if(comp == ActivePower)
   ActivePower=0;
  else
  if(comp == Length)
   Length=0;
  else
  if(comp == Spindle1)
   Spindle1=0;
  else
  if(comp == Spindle2)
   Spindle2=0;
  else
  if(comp == Tendon)
   Tendon=0;
  else*/
  if(comp == LengthInput)
   LengthInput=0;
/*  else
  if(comp == ExternalForce)
   ExternalForce=0;
				*/
 return true;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NMuscle::ADefault(void)
{
 Real value;
 value.resize(18);
 value[0]=0.74;//0.09;//0.3;//0.45;
 value[1]=0.75;//0.25;//0.5;
 value[2]=0.5;//0.015;//0.02;
// value[3]=0.6;
// value[4]=0.004;
// value[5]=0.6;
// value[6]=0.004;

 value[3]=0.1;
 value[4]=0.6;
 value[5]=0.1;
 value[6]=0.6;

 value[7]=1;//37;
 value[8]=0.001;//30;
 value[9]=0.005;

 value[10]=0.5;

 value[11]=1;
 value[12]=0.005;
 value[13]=0.01;

 value[14]=0.1;
 value[15]=0.1;
 value[16]=22;//19.12;
 value[17]=1;

 MulCoeffs=value;

 value.resize(4);
 value[0]=0.039;
 value[1]=2.127;
 value[2]=0.153;
 value[3]=1.719;
 Param=value;

 value.resize(3);
 value[0]=0.003;//0.002;//0.003;
 value[1]=0.0055;//0.0092;//0.0004;//0.001513;
 value[2]=0.0298;//0.0327;//0.03;//0.00386;
 TC=value;


 Threshold = 0.2;//0.5;
 Mass 	   = 1;
 G 	   = 9.8;

// TimeStep=0.000001;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NMuscle::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NMuscle::AReset(void)
{
 for (int i=0; i<7; i++)
  mrOld[i] = mr[i] = 0;

 for (int i=0; i<15; i++)
  yOld[i] = y[i] = 0;

 goldgi    = 0;
 vereteno1 = 0;
 vereteno2 = 0;
 MaxActionPower = 0;
 FirstStep = true;

 return true;
}

// Выполняет расчет этого объекта
bool NMuscle::ACalculate(void)
{
 size_t k=0;

 for (int i=0; i<15; i++)
  yOld[i] = y[i];

 for(int i=0;i<NumInputs;i++)
  for(size_t j=0;j<GetInputDataSize(i);j++)
  {
   //if(k >= OutputSize)
   //	break;

   y[0]=GetInputData(i)->Double[j];

   ++k;
   break;
  }

 if(LengthInput)
 {
  for(int i=0;i<LengthInput->GetNumInputs();i++)
   for(size_t j=0;j<LengthInput->GetInputDataSize(i);j++)
   {
   //if(k >= OutputSize)
   //	break;

	y[8]=LengthInput->GetInputData(i)->Double[j];

	++k;
	break;
   }
 }
 else
  y[8]=0;

/* if(ExternalForce)
 {
  for(size_t i=0;i<ExternalForce->GetNumInputs();i++)
   for(size_t j=0;j<ExternalForce->GetInputSize(i);j++)
   {
   //if(k >= OutputSize)
   //	break;

	y[8]=ExternalForce->GetInputData(i)->Double[j];

	++k;
	break;
   }
 }
 else
  y[8]=0;
		 */
 y[1] = yOld[0] + yOld[11] - yOld[13] - yOld[6] + yOld[4];
// y[1] = yOld[0] + yOld[14] - yOld[13] - yOld[6] + yOld[4];
// y[1] = yOld[0] - yOld[6] + yOld[4];
// y[1] = yOld[0] + yOld[6] - yOld[4];
 y[2] = CompareThreshold( yOld[1] );
 y[3] = MuscularReduction( yOld[2] )*MulCoeffs[16];
 y[4] = MuscleFeedback(y[3], yOld[3], yOld[4],
					  1, MulCoeffs[3], MulCoeffs[4]);
 //AperiodicSection( y[3], yOld[3], MulCoeffs[3], MulCoeffs[4]);
 y[5] = yOld[3] * yOld[3];
 y[6] = MuscleFeedback(y[5], yOld[5], yOld[6],
					  1, MulCoeffs[5], MulCoeffs[6]);
 //AperiodicSection( y[5], yOld[5], MulCoeffs[5], MulCoeffs[6]);
 y[7] = yOld[3] + yOld[13];

 y[11]=MuscleFeedback(y[8], yOld[8], yOld[11],
					  MulCoeffs[11], MulCoeffs[12], MulCoeffs[13]);

 //y[11] = yOld[11]*(1.0-TimeStep/MulCoeffs[11])+yOld[8]*TimeStep/MulCoeffs[11];
 y[12] = yOld[8] * yOld[8]*((yOld[8]>=0)?1:-1);
 y[13] = MuscleFeedback(y[12], yOld[12], yOld[13],
					  MulCoeffs[7], MulCoeffs[8], MulCoeffs[9]);
// y[14] = AperiodicSection( y[11], yOld[11], MulCoeffs[9], MulCoeffs[10]);

/* y[11] = yOld[11]*(1.0-TimeStep/MulCoeffs[11])+yOld[8]*TimeStep/MulCoeffs[11];
 y[12] = yOld[11] * yOld[11]*((yOld[11]>=0)?1:-1);
 y[13] = (AperiodicSection( y[12], yOld[12], MulCoeffs[7], MulCoeffs[8]))*MulCoeffs[17];
 y[14] = AperiodicSection( y[11], yOld[11], MulCoeffs[9], MulCoeffs[10]);
  */

// (y[3] > MaxActionPower) ? (MaxActionPower = y[3]) : 0;
// (y[13] > MaxActionPower) ? (y[11] = yOld[11]) : 0;

// goldgi = AperiodicSection( y[7], yOld[7], MulCoeffs[11], MulCoeffs[12]);
// vereteno1 = AperiodicSection( y[13], yOld[13], MulCoeffs[13], MulCoeffs[14]);
// vereteno2 = AperiodicSection( y[14], yOld[14], MulCoeffs[15], MulCoeffs[16]);
  /*
 // Указатели на дополнительные выходы
 real res;
 // Активная сила
 if(ActivePower)
 {
  res=y[3];
  ActivePower->SetOutput(&res,1);
 }

 // Длина
 if(Length)
 {
  res=y[11];
  Length->SetOutput(&res,1);
 }

 // Веретена
 if(Spindle1)
 {
  res=vereteno1;
  Spindle1->SetOutput(&res,1);
 }

 if(Spindle2)
 {
  res=vereteno2;
  Spindle2->SetOutput(&res,1);
 }

 // Сухожильный орган Гольджи
 if(Tendon)
 {
  res=goldgi;
  Tendon->SetOutput(&res,1);
 }
          */
 real res;
 res=y[7];
 POutputData[0].Double[0]=res;

 FirstStep = false;

 return true;
}
// --------------------------


// --------------------------
// Дополнительные скрытые методы управления счетом
// --------------------------
// Апериодическое звено
real NMuscle::AperiodicSection(real in, real inOld, real param1, real param2)
{
 if ( FirstStep == true )
   return param1*in;

/* if(in-inOld>10e6)
  return param1*in+10e6;

 if(in-inOld<-10e6)
  return param1*in-10e6;
  */
 return param1*in+param2*(in-inOld)*TimeStep;
}

// Порог
real NMuscle::CompareThreshold(real in)
{
 return ((in>Threshold) ? (in-Threshold) : 0);
}

// мускульное сокращение
real NMuscle::MuscularReduction(real in)
{
 for (int i=0; i<7; i++)
  mrOld[i] = mr[i];

 mr[0] = in;
 mr[1] = mrOld[0] - MulCoeffs[2] * mrOld[6];
 mr[2] = mrOld[1] - MulCoeffs[0] * mrOld[3];
 mr[3] = 1.0 / (TC[0] * mrOld[2] + mrOld[3])*TimeStep;
 mr[4] = mrOld[3] - MulCoeffs[1] * mrOld[5];
 mr[5] = 1.0 / (TC[1] * mrOld[4] + mrOld[5])*TimeStep;
 mr[6] = 1.0 / (TC[2] * mrOld[5] + mrOld[6])*TimeStep;

 return mr[6];
}


// Инерционный элемент ОС мышцы
real NMuscle::MuscleFeedback(real x_new, real x_old, real y_old,
					  real k, real T1, real T2)
{
 real res=0;

 res=(1.0-1.0/(T2*TimeStep))*y_old+(k/TimeStep-T1)*x_old/T2+T1*x_new/T2;

 return res;
}

// --------------------------
}
//---------------------------------------------------------------------------

#endif
