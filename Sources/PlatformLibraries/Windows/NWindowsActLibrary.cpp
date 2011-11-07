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

#include "NWindowsActLibrary.h"
#include "NWPhysicalManipulator.cpp"

namespace NMSDK {
                   
NWindowsActLibrary WindowsActLibrary;

// --------------------------
// ������������ � �����������
// --------------------------
NWindowsActLibrary::NWindowsActLibrary(void)
 : NLibrary("WindowsActLibrary","1.0")
{
}
// --------------------------

// --------------------------
// ������ ����������� �����������
// --------------------------
// ��������� ������ ClassSamples �������� ������������ �������� � �� �������.
// �� ��������� ��������������� ������� ������� � ������ ������.
void NWindowsActLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NWPhysicalManipulator;
 cont->SetName("WPhysicalManipulator");
 cont->Default();
 UploadClass("NWPhysicalManipulator",cont);
}
// --------------------------


}
