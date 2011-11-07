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

#ifndef NCONNECTOR_CPP
#define NCONNECTOR_CPP

#include "NConnector.h"

namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NConnector::NConnector(void)
//: NADItem(name)
{
}

NConnector::~NConnector(void)
{
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NConnector* NConnector::New(void)
{
 return new NConnector;
}
// --------------------------



}
#endif


