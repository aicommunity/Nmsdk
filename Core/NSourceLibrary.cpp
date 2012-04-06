/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#include "NSourceLibrary.h"


#include "NConstGenerator.cpp"
#include "NFileGenerator.cpp"
#include "NPulseGenerator.cpp"
#include "NSinusGenerator.cpp"
#include "NManipulatorSourceEmulator.cpp"
#include "NManipulatorSource.cpp"

namespace NMSDK {

NSourceLibrary SourceLibrary;

// --------------------------
// ������������ � �����������
// --------------------------
NSourceLibrary::NSourceLibrary(void)
 : NLibrary("SourceLibrary","1.0")
{
}
// --------------------------

// --------------------------
// ������ ����������� �����������
// --------------------------
// ��������� ������ ClassSamples �������� ������������ �������� � �� �������.
// �� ��������� ��������������� ������� ������� � ������ ������.
void NSourceLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NPulseGenerator;
 cont->SetName("PGenerator");
 cont->Default();
 UploadClass("NPGenerator",cont);

 cont=new NConstGenerator;
 cont->SetName("CGenerator");
 cont->Default();
 UploadClass("NCGenerator",cont);

 cont=new NSinusGenerator;
 cont->SetName("SinusGenerator");
 cont->Default();
 UploadClass("NSinusGenerator",cont);

 cont=new NFileGenerator;
 cont->SetName("FileGenerator");
 cont->Default();
 UploadClass("NFileGenerator",cont);

 cont=new NManipulatorSourceEmulator;
 cont->SetName("ManipulatorSourceEmulator");
 cont->Default();
 UploadClass("NManipulatorSourceEmulator",cont);

 cont=new NManipulatorSource;
 cont->SetName("ManipulatorSource");
 cont->Default();
 UploadClass("NManipulatorSource",cont);
}
// --------------------------


}
