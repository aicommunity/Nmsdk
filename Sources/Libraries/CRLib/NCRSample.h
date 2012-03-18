// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:        http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NCRSampleH
#define NCRSampleH

#include "../Kernel/NBios.h"
#include "rdk.h"

//---------------------------------------------------------------------------
namespace NMSDK {

//using namespace RDK;

class NCRSample: public NANet
{
public: // ������������� ��������
// ������ ��������� ������� �������
RDK::ULProperty<size_t, NCRSample> VectorSize;

// ������ �������
RDK::ULProperty<size_t, NCRSample> SampleSize;

// ����� ������
// 0 - ������������� (����� ������������ � ������ ������ ������)
// 1 - �������� (������������ ������ ������ �� ��������� ����)
RDK::ULProperty<int, NCRSample> Mode;

// ������� ������� �������
RDK::ULProperty<int, NCRSample> CurrentSample;

protected: // ������ ���������
// ������ �������
//RDK::UCLStateProperty<vector<NIOData>, NCRSample> SampleData;
vector<pair<RDK::UItemData,int> > SampleData;

public:
// --------------------------
// ������������ � �����������
// --------------------------
NCRSample(void);
~NCRSample(void);
// --------------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������� ������� �������
bool SetCurrentSample(int value);

// ��������� ������� �������
bool SetSampleSize(size_t value);

// ��������� ������� ������� �������
bool SetVectorSize(size_t value);
// --------------------------

// --------------------------
// ������ ���������� ��������
// --------------------------
// ��������� ������� ������� �������� ������
bool Add(int class_index);

// ������� �������� ������� ������� ������ �� ��������
bool Del(size_t index);

// ������� �������
void Clear(void);

// ���������� ������ ������ �������� ������� ��������� �������
int GetCurrentClassIndex(void) const;

// ���������� ������ ��������� �������
const vector<pair<RDK::UItemData,int> >& GetSampleData(void) const;
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NAContainer* New(void);
// --------------------------

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

// ��������� ������ ����� ������� �� ������� ����.
virtual bool ACalculate(void);
// --------------------------
};

}
//---------------------------------------------------------------------------
#endif
