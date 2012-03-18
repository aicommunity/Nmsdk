/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002-2009.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		2.0.0

This file - part of the project: NMSDK

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NENVIRONMENT_CPP
#define NENVIRONMENT_CPP

#include "NEnvironment.h"
//#include "NParserUtility.h"

namespace NMSDK {

// --------------------------
// Constructors & destructors
// --------------------------
NEnvironment::NEnvironment(void)
 : RDK::UAContainerEnvironment()
{
}

NEnvironment::~NEnvironment(void)
{
}
// --------------------------

// --------------------------
// ������ ���������� ������� �����
// --------------------------
// ���������� ��������� �� ������
RDK::UEPtr<NModel> NEnvironment::GetModel(void)
{
 return RDK::static_pointer_cast<NModel>(Model);
}

// ���������� ������� ������
bool NEnvironment::DestroyModel(void)
{
 if(!Model)
  return true;

// GetModel()->Free();
 return RDK::UAContainerEnvironment::DestroyModel();
}
// --------------------------

// --------------------------
// ������ ���������� �������������
// --------------------------
// ��������� ����������
bool NEnvironment::AddController(NController* controller, bool delenabled)
{
 map<NController*, bool>::iterator I=Controllers.find(controller);

 if(I != Controllers.end())
  return true;

 if(!controller)
  return false;

 Controllers[controller]=delenabled;
 return true;
}

// ������� ����������
bool NEnvironment::DelController(NController* controller)
{
 map<NController*, bool>::iterator I=Controllers.find(controller);

 if(I != Controllers.end())
 {
  if(I->second)
   delete I->first;
  Controllers.erase(I);
 }

 return true;
}

// ������� ��� �����������
bool NEnvironment::DelAllControllers(void)
{
 map<NController*, bool>::iterator I,J;

 I=Controllers.begin();
 J=Controllers.end();
 while(I != J)
 {
  if(I->second)
   delete I->first;
  ++I;
 }
 Controllers.clear();
 return true;
}

// ������ ������������ ������������
map<NController*, bool>::iterator NEnvironment::GetFirstController(void)
{
 return Controllers.begin();
}

map<NController*, bool>::iterator NEnvironment::GetLastController(void)
{
 return Controllers.end();
}
// --------------------------

// --------------------------
// ��������� ������� � ������ �����
// --------------------------
// ���������� ��������� �� ������
RDK::UEPtr<NModel> const NEnvironment::operator -> (void)
{
 return GetModel();
}

// ���������� ��������� �� ��������� ������ �� �������� �����
// �������� ��������� ���������� �������
// ���� ��������� �� ������, �� ���������� 0 � ���������� ������� ���������
RDK::UEPtr<NAContainer> NEnvironment::operator () (const string &longname)
{
 if(!Model)
  CurrentComponent=0;
 else
  CurrentComponent=GetModel()->GetComponentL(longname);

 return RDK::static_pointer_cast<NAContainer>(CurrentComponent);
}

// ���������� ��������� �� ��������� ������ �� �������� ��������������
// �������� ��������� ���������� �������
// ���� ��������� �� ������, �� ���������� 0 � ���������� ������� ���������
RDK::UEPtr<NAContainer> NEnvironment::operator () (const ULongId &longid)
{
 if(!Model)
  CurrentComponent=0;
 else
  CurrentComponent=GetModel()->GetComponentL(longid);

 return RDK::static_pointer_cast<NAContainer>(CurrentComponent);
}

// ���������� ��������� �� ������� ��������� ������
RDK::UEPtr<NAContainer> NEnvironment::operator () (void)
{
 return RDK::static_pointer_cast<NAContainer>(CurrentComponent);
}
// --------------------------

// --------------------------
// ������ ������������ ��������� ������������
// --------------------------
// ���������� ������ ��������������
const map<ULongId, NGraphics*>& NEnvironment::GetGraphics(void) const
{
 return Graphics;
}

// ���������� ������������ ��� ��������� id
NGraphics* NEnvironment::GetGraphics(const ULongId &id)
{
 map<ULongId, NGraphics*>::iterator I;
 I=Graphics.find(id);
 if(I == Graphics.end())
  return 0;

 return I->second;
}

// ��������� ������� ������������� ��� �������� ����
bool NEnvironment::CheckGraphics(const ULongId &id) const
{
 map<ULongId, NGraphics*>::const_iterator I;
 I=Graphics.find(id);
 if(I == Graphics.end())
  return false;

 return true;
}

// ��������� ����� ������������
// �� ������ ������ ���� ������������ ��� �����
// ���������� ��������� ������������
// ����� �� ����� �� ���� ������ ������������ ������ �������
NGraphics* NEnvironment::AddGraphics(const ULongId &id, NGraphics *graphics)
{
 map<ULongId, NGraphics*>::iterator I;
 I=Graphics.find(id);
 if(I != Graphics.end())
  return I->second;

 if(!graphics)
  return 0;

 Graphics[id]=graphics;
 return graphics;
}

// ������� ������������ ���� id
bool NEnvironment::DelGraphics(const ULongId &id)
{
 map<ULongId, NGraphics*>::iterator I;
 I=Graphics.find(id);
 if(I != Graphics.end())
  Graphics.erase(I);

 return true;
}
// --------------------------

// --------------------------
// ������ ������������� �����
// --------------------------
// --------------------------

// --------------------------
// ������ ������� � ������ ���������
// --------------------------
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NEnvironment::ADefault(void)
{
 if(!RDK::UAContainerEnvironment::ADefault())
  return false;

 NAContainer::SetTime(0);
 return true;
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NEnvironment::ABuild(void)
{
 if(!RDK::UAContainerEnvironment::ABuild())
  return false;

 return true;
}

// ����� �������� �����.
bool NEnvironment::AReset(void)
{
 if(!RDK::UAContainerEnvironment::AReset())
  return false;

 NAContainer::SetTime(0);
 return true;
}

// ��������� ������ ����� �������
bool NEnvironment::ACalculate(void)
{
 if(!RDK::UAContainerEnvironment::ACalculate())
  return false;

 return true;
}
// --------------------------

// --------------------------
// ��������������� ������ ������������� �����
// --------------------------
// ��������� ������������ ���������� � ����������� ��������� � ����������
// ��������� �� ����.
// � ������� ������ �� ������ ������ � ���������� 0.
/*RDK::UAStorage* NEnvironment::LoadStorageLibrary(const string &filename)
{
 return 0;
}

// ��������� ������������ ���������� � ����������� ���������.
// � ������� ������ �� ������ ������ � ���������� true.
bool NEnvironment::UnLoadStorageLibrary(void)
{
 return true;
}

// ��������� ������������ ���������� � ������� �������� �������
// � ���� ���������� ��������� � ���������� ��������� �� ����.
// � ������� ������ �� ������ ������ � ���������� 0.
RDK::UStorage* NEnvironment::LoadClassLibrary(const string &libname, const string &filename)
{
 return 0;
}

// ��������� ������������ ���������� � ������� �������� �������.
// � ������� ������ �� ������ ������ � ���������� true.
bool NEnvironment::UnLoadClassLibrary(const string &libname)
{
 return true;
}               */
// --------------------------

// --------------------------
// ������ ���������� �������
// --------------------------
// ��������� ������ ��������� ������ � ������
// ���������� ��������� �� ����������� ������
RDK::UEPtr<NAContainer> NEnvironment::AddObject(const NameT &classname)
{
 RDK::UEPtr<NAContainer> comp=0;

 if(!Storage || !Model)
  return 0;

 comp=RDK::static_pointer_cast<NAContainer>(GetStorage()->TakeObject(classname));

 if(!comp)
  return 0;

 if(!GetModel()->AddComponent(comp))
 {
  comp->Free();
//  Storage->ReturnObject(RDK::static_pointer_cast<RDK::UAComponent>(comp));
  return 0;
 }
 return comp;
}


// ��������� ������ ��������� ������ 'classname' � �������� ������ 'objectname'
// � ������ � ������, ���� ������ � ������ 'objectname' �� ������ � ������
// ���������� ��������� �� ������
// ����� �� ����������� ������� ����� 'objectname', ���� ����� ��� ��� ������� � ������
RDK::UEPtr<NAContainer> NEnvironment::AddObject(const NameT &objectname, const NameT &classname)
{
 if(!Model)
  return 0;

 RDK::UEPtr<NAContainer> comp=GetModel()->GetComponent(objectname);

 if(!comp)
 {
  comp=AddObject(classname);
  if(!comp)
   return 0;

  comp->SetName(objectname);
 }

 return RDK::dynamic_pointer_cast<NAContainer>(comp);
}
// --------------------------


}
#endif
