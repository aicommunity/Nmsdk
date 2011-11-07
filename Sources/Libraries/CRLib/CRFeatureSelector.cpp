//---------------------------------------------------------------------------


#pragma hdrstop

#include "CRFeatureSelector.h"

//---------------------------------------------------------------------------
// ---------------------
// Конструкторы и деструкторы
// ---------------------
CRFeatureSelector::CRFeatureSelector(const string &name)
: NADItem(name),
 StatisticMode("StatisticMode",this,&CRFeatureSelector::SetStatisticMode)
{
 SetNumOutputs(1);
 BmpTrainSample=0;
 StatisticMode=0;

 AddLookupParameter("StatisticMode",StatisticMode);
}

CRFeatureSelector::~CRFeatureSelector(void)
{
}
// ---------------------

// ---------------------
// Методы управления параметрами
// ---------------------
// Режим накопления статистики
bool CRFeatureSelector::SetStatisticMode(int value)
{
 if(StatisticMode <0 || StatisticMode>1)
  return false;

 if(StatisticMode == value)
  return true;

 StatisticMode=value;
 return true;
}
// ---------------------

// ---------------------
// Методы доступа к данным
// ---------------------
const UBitmap& CRFeatureSelector::GetInputImage(void) const
{
 return InputImage;
}
// ---------------------

// ---------------------
// Методы счета
// ---------------------
// Метод задания входного вектора
bool CRFeatureSelector::SetInputImage(const UBitmap &input)
{
 InputImage=input;
 return true;
}
// ---------------------
//---------------------------------------------------------------------------

#pragma package(smart_init)
