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

#ifndef NITEM_H
#define NITEM_H

#include "../../Kernel/NBios.h"

namespace NMSDK {

class NItem: public NADItem
{
public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NItem(void);
virtual ~NItem(void);
// --------------------------

// --------------------------
// ������ ������� � ���������
// --------------------------
// ������������� �������� ������� �������� ������
void SetOutput(const void *data);

// ������������� �������� ������� �������� ������
// size - ����� ��������� �������
void SetOutput(const void *data,size_t size);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NItem* New(void);
// --------------------------
};

}
#endif



