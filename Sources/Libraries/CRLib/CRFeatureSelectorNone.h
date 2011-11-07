//---------------------------------------------------------------------------

#ifndef CRFeatureSelectorNoneH
#define CRFeatureSelectorNoneH

#include "CRFeatureSelector.h"

class CRFeatureSelectorNone: public CRFeatureSelector
{
// ---------------------
// ������ �����
// ---------------------
// ����� ������� �������� �������
virtual bool SetInputImage(const UBitmap &input);
// ---------------------


// --------------------------
// ������� ������ ���������� ������
// --------------------------
protected:
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool ADefault(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool ABuild(void);

// ����� �������� �����.
virtual bool AReset(void);

// ��������� ������ ����� �������
virtual bool ACalculate(void);
// --------------------------


// ---------------------
// ������ ������������
// ---------------------
virtual bool SaveToFile(const std::string &filename);
virtual bool LoadToFile(const std::string &filename);
// ---------------------

};
//---------------------------------------------------------------------------
#endif
