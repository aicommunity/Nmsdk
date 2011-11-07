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

#ifndef NMODEL_H
#define NMODEL_H

#include "../../Kernel/NBios.h"

namespace NMSDK {

class NModel: public NANet
{
protected: // �������� ��������

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NModel(void);
virtual ~NModel(void);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NModel* New(void);
// --------------------------
};

}

#endif



