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

#ifndef NCONNECTOR_H
#define NCONNECTOR_H

#include "../../Kernel/NBios.h"

namespace NMSDK {

class NConnector: public NADItem
{
public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
//NConnector(const string &name);
NConnector(void);
virtual ~NConnector(void);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NConnector* New(void);
// --------------------------
};     

}

#endif



