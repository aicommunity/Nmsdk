/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#include "NPhysLibrary.h"

#include "NManipulator.cpp"

namespace NMSDK {      

NPhysLibrary PhysLibrary;

// --------------------------
// ������������ � �����������
// --------------------------
NPhysLibrary::NPhysLibrary(void)
 : NLibrary("PhysLibrary","1.0")
{
}
// --------------------------

// --------------------------
// ������ ����������� �����������
// --------------------------
// ��������� ������ ClassSamples �������� ������������ �������� � �� �������.
// �� ��������� ��������������� ������� ������� � ������ ������.
void NPhysLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NManipulator;
 cont->SetName("Manipulator");
 cont->Default();
 UploadClass("NManipulator",cont);
}
// --------------------------


}
