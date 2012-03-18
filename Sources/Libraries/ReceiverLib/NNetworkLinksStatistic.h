/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2011.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NNetworkLinksStatisticH
#define NNetworkLinksStatisticH

#include "../../Kernel/NBios.h"
#include "rdk.h"

namespace NMSDK {

class NNetworkLinksStatistic: public NANet
{
public: // ���������
// �������� ������� ����� ������� ����������� ����������
double StatsInterval;

// ����� ������������ ����������
int Mode;

protected: // ������
// ����� ����������
int StatsNumber;

protected: // ��������� ����������
// ����� ������
RDK::UIniFile<char> StatsFile;

// ������ ������ ���������� ��������� ���������� ����������
RDK::ULongTime StatsStartTime;


public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NNetworkLinksStatistic(void);
virtual ~NNetworkLinksStatistic(void);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NNetworkLinksStatistic* New(void);
// --------------------------

// --------------------------
// Computation methods
// --------------------------
// ��������� ����� ����, �������� ����������
bool ReCreateFile(void);
// --------------------------

// --------------------------
// Proctected computation methods
// --------------------------
protected:
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool ADefault(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool ABuild(void);

// Reset computation
virtual bool AReset(void);

// Execute math. computations of current object on current step
virtual bool ACalculate(void);
// --------------------------

// --------------------------
// ��������������� ������ ����� ����������
// --------------------------
protected:
// ���������� ������� ����������
void ClearStats(void);

// ������ ������� �������� ������ ������� ����������
void ResizeStats(void);
// --------------------------

};

}

#endif
