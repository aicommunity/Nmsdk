/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:        http://ailab.ru
Version:    1.0.0

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NUSupportH
#define NUSupportH

#include "NSupport.h"

namespace NMSDK {

//using namespace RDK;

// ���������� ����������� � bitmap
RDK_LIB_TYPE RDK::UBitmap& operator << (RDK::UBitmap &bmp, const RDK::UItemData &data);

// ���������� ����������� � data
// data.DataSize ��������������� = 1
// ������ ������: Width,Height,ColorModel,<������>
RDK_LIB_TYPE RDK::UItemData& operator >> (const RDK::UBitmap &bmp, RDK::UItemData &data);

// ���������� ����������� � data
// ������������, ��� ������ ��� ��������
// ������ ������: Width,Height,ColorModel,<������>
RDK_LIB_TYPE const RDK::UItemData& operator >> (const RDK::UBitmap &bmp, const RDK::UItemData &data);
}
#endif
