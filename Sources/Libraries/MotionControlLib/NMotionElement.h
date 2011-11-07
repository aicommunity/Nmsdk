/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		1.0.0

This file - part of the project: NMSDK

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */
#ifndef NMotionElementH
#define NMotionElementH

#include "../../Kernel/NBios.h"
//---------------------------------------------------------------------------
namespace NMSDK {

// ��������� �� ������������ ��������
// ���� mode == 0 - ����������� ������ ������
// 	    mode == 1 - ������ ��� ���������� �������������
NANet* CreateMotionElement(NStorage *storage, const string &netclassname, int mode);

// ����������, �� � ��������� �� ���������
NANet* CreateBranchedMotionElement(NStorage *storage, const string &netclassname, int mode);

}
//---------------------------------------------------------------------------
#endif
