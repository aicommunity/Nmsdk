//---------------------------------------------------------------------------


#pragma hdrstop

#include "CRFeatureSelector.h"

//---------------------------------------------------------------------------
// ---------------------
// ������������ � �����������
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
// ������ ���������� �����������
// ---------------------
// ����� ���������� ����������
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
// ������ ������� � ������
// ---------------------
const UBitmap& CRFeatureSelector::GetInputImage(void) const
{
 return InputImage;
}
// ---------------------

// ---------------------
// ������ �����
// ---------------------
// ����� ������� �������� �������
bool CRFeatureSelector::SetInputImage(const UBitmap &input)
{
 InputImage=input;
 return true;
}
// ---------------------
//---------------------------------------------------------------------------

#pragma package(smart_init)
