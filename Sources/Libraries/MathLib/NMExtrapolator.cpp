// ===========================================================
// Version:        3.0.3
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

//#pragma hdrstop

#include "NMExtrapolator.h"

namespace NMSDK {

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NMExtrapolator::NMExtrapolator(void)
// : NADItem(name),
 : PredictionTime("PredictionTime",this,&NMExtrapolator::SetPredictionTime),
   NumLevels("NumLevels",this,&NMExtrapolator::SetNumLevels)
{
// AddLookupParameter("PredictionTime",PredictionTime);
// AddLookupParameter("NumLevels",NumLevels);
}

NMExtrapolator::~NMExtrapolator(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Время прогноза, с
bool NMExtrapolator::SetPredictionTime(TimeT ptime)
{
 if(ptime <= 0)
  return false;

 return true;
}

// Число уровней сети
bool NMExtrapolator::SetNumLevels(size_t value)
{
 if(value <= 1)
  return false;

 CalcPascalCoeff(value+1, PascalCoeffs);

 return true;
}
// --------------------------


// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NAContainer* NMExtrapolator::New(void)
{
 return new NMExtrapolator;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NMExtrapolator::ADefault(void)
{
 PredictionTime=1;
 NumLevels=4;
 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NMExtrapolator::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NMExtrapolator::AReset(void)
{
// for(size_t i=0;i<History.size();i++)
//  History[i].assign(History[i].size(),0);
 History.clear();
 History.reserve((PredictionTime.v*TimeStep)*(NumLevels+1));
 //History2.clear();
 HistoryCounter=0;

 return true;
}

// Выполняет расчет этого объекта
bool NMExtrapolator::ACalculate(void)
{
 // Пополнение истории
 Real input;
 input.resize(FullInputDataSize);
 size_t k=0;
 for(size_t i=0;i<NumInputs;i++)
 {
  for(size_t j=0;j<PInputDataSize[i];j++)
  {
   input[k]=PInputData[i]->Double[j];
   ++k;
  }
 }


 History.push(input);
 if(History.size()>(PredictionTime.v*TimeStep)*(NumLevels+1))
  History.pop();
 else
   return true;


 long long buff[256];
 memcpy(buff,&PascalCoeffs[0],PascalCoeffs.size()*sizeof(long long));

 k=0;
 long long currsign=1;
 for(size_t i=0;i<NumInputs;i++)
 {
  for(size_t j=0;j<PInputDataSize[i];j++)
  {
   real res=0;
   for(size_t m=0;m<NumLevels;m++)
   {
	int i1=static_cast<int>((real(m)*PredictionTime)*TimeStep);
//	int i2=(float(m+1)*PredictionTime)/TimeStep;
//	if(History[History.size()-i1-1].size()>k &&
//	   History[History.size()-i2-1].size()>k)
	res+=currsign*PascalCoeffs[m+1]*History[History.size()-i1-1][k];
	currsign*=-1;
   }
   res-=History[0][k];
   POutputData[0].Double[k]=res;

   ++k;
  }
 }

	 /*
 k=0;
 for(size_t i=0;i<NumInputs;i++)
 {
  for(size_t j=0;j<PInputDataSize[i];j++)
  {
   Output.Double[k]=0;
   Real level;
   level.resize(NumLevels);
   for(size_t m=0;m<NumLevels;m++)
   {
	int i1=(float(m)*PredictionTime)/TimeStep;
	int i2=(float(m+1)*PredictionTime)/TimeStep;
//	if(History[History.size()-i1-1].size()>k &&
//	   History[History.size()-i2-1].size()>k)
	 level[m]=History[History.size()-i1-1][k]-History[History.size()-i2-1][k];
   }

//   if(History[History.size()-1].size()>k)
   Output.Double[k]=level[0]+History[History.size()-1][k];
   for(size_t n=1;n<NumLevels;n++)
   {
	for(size_t m=0;m<NumLevels-n;m++)
	{
	 level[m]-=level[m+1];
	}
	Output.Double[k]+=level[0];
   }
   ++k;
  }
 }
              */


 return true;
}
// --------------------------


// --------------------------
// Скрытые методы счета
// --------------------------
// Вычисляет коэффициенты треугольника паскаля
void NMExtrapolator::CalcPascalCoeff(size_t level, vector<size_t> &coeffs)
{
 coeffs.assign(level+1,0);

 size_t i, j;

 coeffs[0] = 1;
 for(j = 1 ; j <= level; j++)
   for(i = j; i >= 1 ; i--)
	 coeffs[i] = coeffs[i-1] + coeffs[i];
}
// --------------------------


}
//---------------------------------------------------------------------------


