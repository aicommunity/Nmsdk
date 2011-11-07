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

#ifndef NITEM_CPP
#define NITEM_CPP

#include "NItem.h"

namespace NMSDK {

// ������
// --------------------------
// ������������ � �����������
// --------------------------
NItem::NItem(void)
//: NADItem(name)
{
}

NItem::~NItem(void)
{
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
NItem* NItem::New(void)
{
 return new NItem;
}
// --------------------------

// --------------------------
// ������ ������� � ���������
// --------------------------
// ������������� �������� ������� �������� ������
void NItem::SetOutput(const void *data)
{
 FillOutputData(0,data);
}

// ������������� �������� ������� �������� ������
// size - ����� ��������� �������
void NItem::SetOutput(const void *data,size_t size)
{
 size_t bsize=GetByteOutputDataSize(0);
 size_t bdatasize=GetByteOutputDataSize(0)*size;
 size_t result=(bsize<=bdatasize)?bsize:bdatasize;
 FillOutputData(0,&result);
}
// --------------------------


}
#endif


