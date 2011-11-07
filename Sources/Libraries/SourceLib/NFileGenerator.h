// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NFILE_GENERATOR_H
#define NFILE_GENERATOR_H

#include "../BCL/NSource.h"
#include "rdk.h"

namespace NMSDK {

class NFileGenerator: public NSource
{
public: // ������������� ��������
// ��� ����� � �������
RDK::ULProperty<string,NFileGenerator> FileName;

protected: // �������� ��������

protected: // ������
RDK::UIniFile<char> Ini;

// 2D ������ ������ �� ������ ������ �������
map<real,vector<RDK::UItemData> > Data;

public: // ��������� ����������
// ��������, ����������� �� ������� ������ �������
map<real,vector<RDK::UItemData> >::iterator CurrentIndex;

// ������ ������� ������ ��������� ��������
real DataStartTime;


public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NFileGenerator(void);
virtual ~NFileGenerator(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������� ��� ����� � �������
bool SetFileName(const string &value);
// --------------------------

public:
// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NFileGenerator* New(void);
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
virtual bool CheckComponentType(const NAContainer* comp) const;
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

// ��������� ������ ����� �������
virtual bool ACalculate(void);
// --------------------------
};

}
#endif

