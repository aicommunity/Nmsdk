// ===========================================================
// Version:        3.0.7
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:		alexab@ailab.ru
url:        http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NBIOS_CPP
#define NBIOS_CPP

#include <time.h>
#include <algorithm>
#include <sstream>
#include "NBios.h"
//#include "NPointer.h"
#include "NStorage.h"

namespace NMSDK {
/*
// --------------------------
// ������������ � �����������
// --------------------------
NANet::NANet(void)
{
}

NANet::~NANet(void)
{
}
// --------------------------

// --------------------------
// ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NANet::Default(void)
{
 if(!RDK::UANet::Default())
  return false;

 SetOutputDataElementSize(0,sizeof(real));
 return true;
}
// --------------------------
          */
/* *************************************************************************** */
// Class NAContainer
/* *************************************************************************** */
/*
// --------------------------
// ���������� ��������
// --------------------------
// ������� ����� ������ � ��������
real NAContainer::Time=0;
// --------------------------

// --------------------------
// ������ ���������� ����������� ����������
// --------------------------
// ���������� ������� ����� ������
const real& NAContainer::GetTime(void)
{
 return Time;
}

// ������������� ������� ����� ������
bool NAContainer::SetTime(real value)
{
 if(Time == value)
  return true;

 Time=value;
 return true;
}
// --------------------------

// --------------------------
// ������������ � �����������
// --------------------------
NAContainer::NAContainer(void)
 : TimeStep("TimeStep",this,&NAContainer::SetTimeStep),
   Activity("Activity",this,&NAContainer::SetActivity),
   Name("Name",this,&NAContainer::SetName),
   Class("Class",this,&NAContainer::SetClass,&NAContainer::GetClass),
   Id("Id",this,&NAContainer::SetId),
   Coord("Coord",this)
{
 // ��������� �� 0-� ������� ������� ���������
 PComponents=0;

 // ���������� ��������� � ������� ���������
 NumComponents=0;

 CalcCounter=0;

 TimeStep=OwnerTimeStep=DefaultTimeStep;
}


NAContainer::~NAContainer(void)
{
 DelAllComponents();
 UnLinkAllControllers();

 if(!BreakOwner())
  return;// ��������! ������������ ������, ��������� ����������

 if(Storage)
  {
   dynamic_cast<NStorage*>(Storage)->PopObject(this);
  }
}
// --------------------------

// --------------------------
// ������ ������� � ���������
// --------------------------
// ���������, �������� �� ������ owner
// ���������� ����� ������� �� �����-���� ������ ��������
bool NAContainer::CheckOwner(const NAContainer *owner) const
{
 if(Owner == 0 && Owner != owner)
  return false;

 if(Owner == owner)
  return true;

 return static_cast<NAContainer*>(Owner)->CheckOwner(owner);
}

// ���������� ������ ��� �������
// (������� ����� ���� ����������).
NameT& NAContainer::GetFullName(NameT &buffer) const
{
 if(Owner == 0)
  {
   buffer+=Name();
   return buffer;
  }

 static_cast<NAContainer*>(Owner)->GetFullName(buffer);
 buffer+='.';
 buffer+=Name();

 return buffer;
}

// ����������  '�������' ����� �������
// (�������� ��� ��������� 'mainowner').
// ����� ���������� ������ ������, ���� 'mainowner' - �� ��������
// ���������� ������� �� �� ����� ������ ��������.
NameT& NAContainer::GetLongName(const NAContainer *mainowner, NameT &buffer) const
{
 if(Owner == 0 && Owner != mainowner)
  {
   buffer.clear();
   return buffer;
  }

 if(Owner == mainowner)
  {
   buffer=Name();
//   buffer+=Name();
   return buffer;
  }

 if(static_cast<NAContainer*>(Owner)->GetLongName(mainowner,buffer) == ForbiddenName)
  {
   buffer.clear();
   return buffer;
  }

 buffer+='.';
 buffer+=Name();

 return buffer;
}

// ���������� ������ Id �������
// (������� Id ���� ����������).
ULongId& NAContainer::GetFullId(ULongId &buffer) const
{
 return RDK::UAContainer::GetFullId(buffer);
}

// ����������  '�������' Id �������
// (�������� ��� ��������� 'mainowner').
// ����� ���������� ������ ������, ���� 'mainowner' - �� ��������
// ���������� ������� �� �� ����� ������ ��������.
ULongId& NAContainer::GetLongId(const NAContainer *mainowner, ULongId &buffer) const
{
 return RDK::UAContainer::GetLongId(mainowner,buffer);
}
// --------------------------

// --------------------------
// ������ ���������� ����������
// --------------------------
// ������� ��������� �������
bool NAContainer::BreakOwner(void)
{
 if(Owner)
  return static_cast<NAContainer*>(Owner)->DelComponent(this,false);

 return true;
}

// ������������� ��������� �� �������� ��������� ���� ��������
// ��������� ��������������� �� ����� ������� �������� ���������
// 'levels'. ���� levels < 0 �� ��������������� ����������� �� ���� �������
bool NAContainer::SetMainOwner(RDK::UAComponent* const mainowner)
{
 return RDK::UAComponent::SetMainOwner(mainowner);
}

bool NAContainer::SetMainOwner(RDK::UAComponent* const mainowner, int levels)
{
 if(MainOwner == mainowner && !levels)
  return true;

 MainOwner=mainowner;

 if(!levels)
  return true;

 for(size_t i=0;i<NumComponents;i++)
 {
  // ������������� �������� ��������� ������ ��� �������� �����������
  // � ������� �� ��� �� �����
  if(PComponents[i]->GetMainOwner() == 0)
  {
   if(levels<0)
   {
	if(!PComponents[i]->SetMainOwner(static_cast<NAContainer*>(MainOwner),levels))
	 return false;
   }
   else
	if(!PComponents[i]->SetMainOwner(static_cast<NAContainer*>(MainOwner),levels-1))
	 return false;
  }
 }

 return true;
}

// ��������� ������������ ��� 'name' �� ������������ � ������
// ������� �������.
bool NAContainer::CheckName(const NameT &name)
{
// if(!Owner)
//  return true;

 if(CompsLookupTable.find(name) == CompsLookupTable.end())
  return true;

 return false;
}

// ��������� ������������ Id 'id' �� ������������ � ������ �������, �������.
bool NAContainer::CheckId(const UId &id)
{
 return (id>LastId)?true:false;
}

#pragma warning (disable : 4996)
// ���������� ��� ���������� � ����������� ����� �������
NameT& NAContainer::GenerateName(const NameT &prefix, NameT &namebuffer)
{
 unsigned long int k=2;
 char buffer[20];

 while(true)
  {
   sprintf(buffer,"%i",k);
   if(prefix.size()>0)
    namebuffer=prefix+buffer;
   else
    namebuffer=NameT("n")+buffer;
   if(CheckName(namebuffer))
    break;

   k++;

   if(k == 0) // ��������!! ������ ���� ���������� - ������� ���������
    return namebuffer;
  }

 return namebuffer;
}
#pragma warning (default : 4996)


// ���������� ���������� Id.
UId NAContainer::GenerateId(void)
{
 return LastId+1;
}
// --------------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������� �������� ���� ��������������
bool NAContainer::SetTimeStep(TimeT timestep)
{
 if(timestep <= 0)
  return false;

 if(Owner)
  OwnerTimeStep=static_cast<NAContainer*>(Owner)->TimeStep();
 else
  OwnerTimeStep=timestep;

 // ��������� �� ���� ����������� �������
 for(size_t i=0;i<NumComponents;i++)
  PComponents[i]->OwnerTimeStep=timestep;

 return true;
}

// ������������� ���� ���������� �������
bool NAContainer::SetActivity(bool activity)
{
 for(size_t i=0;i<NumComponents;i++)
  PComponents[i]->Activity=activity;

 if(activity)
  return Reset();

 return true;
}

// ������������� ��� �������.
bool NAContainer::SetName(const NameT &name)
{
 if(name.empty())
  return false;

 if(Owner != 0)
  {
   if(!static_cast<NAContainer*>(Owner)->CheckName(name))
	return false;

   if(!static_cast<NAContainer*>(Owner)->ModifyLookupComponent(Name(), name))
	return false;
  }

 return true;
}

UId NAContainer::GetClass(void) const
{
 return RDK::UAComponent::GetClass();
}

bool NAContainer::SetClass(UId value)
{
 return RDK::UAComponent::SetClass(value);
}

// ������������� Id �������.
bool NAContainer::SetId(const UId &id)
{
 if(Owner != 0)
  {
   if(!static_cast<NAContainer*>(Owner)->CheckId(id))
	return false;

   static_cast<NAContainer*>(Owner)->SetLookupComponent(Name(), id);
  }

 return true;
}
// --------------------------

// --------------------------
// ������ ������� � �������� �����������
// --------------------------
// ���������� ��� ��������� ���������� �� ��� Id
const NameT& NAContainer::GetComponentName(const UId &id) const
{
 map<NameT,UId>::const_iterator I=CompsLookupTable.begin(),
                                 J=CompsLookupTable.end();
 while(I != J)
  {
   if(I->second == id)
    return I->first;
   ++I;
  }
 return ForbiddenName;
}

// ���������� Id ��������� ���������� �� ��� �����
const UId& NAContainer::GetComponentId(const NameT &name) const
{
 map<NameT,UId>::const_iterator I=CompsLookupTable.find(name);
 if(I == CompsLookupTable.end())
  return ForbiddenId;
 else return I->second;
}

// ���������� ��� ��������� �� ��� Id
const NameT& NAContainer::GetParameterName(const UId &id) const
{
 map<NameT,NVariable>::const_iterator I=ParamsLookupTable.begin(),
                                 J=ParamsLookupTable.end();
 while(I != J)
  {
   if(I->second.Id == id)
    return I->first;
   ++I;
  }
 return ForbiddenName;
}

// ���������� Id ��������� �� ��� �����
const UId& NAContainer::GetParameterId(const NameT &name) const
{
 map<NameT,NVariable>::const_iterator I=ParamsLookupTable.find(name);
 if(I == ParamsLookupTable.end())
  return ForbiddenId;
 else return I->second.Id;
}

// ���������� ������ ��� ��������� ��� �������� NMSDK, � �������� '*'
NameT NAContainer::GetParameterLongName(const NameT &name) const
{
 map<NameT,NVariable>::const_iterator I=ParamsLookupTable.find(name);
 if(I == ParamsLookupTable.end())
  return NameT();
 else return GetParameterLongName(*(I->second.Property));
}

NameT NAContainer::GetParameterLongName(const UId &id) const
{
 map<NameT,NVariable>::const_iterator I=ParamsLookupTable.begin(),
								 J=ParamsLookupTable.end();
 while(I != J)
  {
   if(I->second.Id == id)
	return GetParameterLongName(*(I->second.Property));
   ++I;
  }
 return NameT();
}

// ���������� ��� ���������� ��������� �� ��� Id
const NameT& NAContainer::GetStateName(const UId &id) const
{
 map<NameT,NVariable>::const_iterator I=StateLookupTable.begin(),
								 J=StateLookupTable.end();
 while(I != J)
  {
   if(I->second.Id == id)
    return I->first;
   ++I;
  }
 return ForbiddenName;
}

// ���������� Id ���������� ��������� �� ��� �����
const UId& NAContainer::GetStateId(const NameT &name) const
{
 map<NameT,NVariable>::const_iterator I=StateLookupTable.find(name);
 if(I == StateLookupTable.end())
  return ForbiddenId;
 else return I->second.Id;
}

// ���������� ������ ��� ���������� ��������� ��� �������� NMSDK, � �������� '*'
NameT NAContainer::GetStateLongName(const NameT &name) const
{
 map<NameT,NVariable>::const_iterator I=StateLookupTable.find(name);
 if(I == StateLookupTable.end())
  return NameT();
 else return GetStateLongName(*(I->second.Property));
}

NameT NAContainer::GetStateLongName(const UId &id) const
{
 map<NameT,NVariable>::const_iterator I=StateLookupTable.begin(),
								 J=StateLookupTable.end();
 while(I != J)
  {
   if(I->second.Id == id)
	return GetStateLongName(*(I->second.Property));
   ++I;
  }
 return NameT();
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// ������� ����� ����� ������� � ����������� ���� ���������
// � �������� ����������.
// ���� 'stor' == 0, �� �������� �������� ��������������
// � ��� �� ��������� ��� ������������� ���� ������
NAContainer* NAContainer::Alloc(const NameT &name, NStorage *stor, bool copystate)
{
// return dynamic_cast<NAContainer*>(RDK::UAContainer::Alloc(name,stor,copystate));
 NAContainer* copy;
 NStorage *storage=(stor!=0)?stor:static_cast<NStorage*>(Storage);

 if(storage)
 {
  copy=dynamic_cast<NAContainer*>(storage->TakeObject(Class,this));
  if(copy)
   copy->Name=name;
 }
 else
 {
  copy=New();
  copy->Name=name;
  Copy(copy,stor,copystate);
 }

 return copy;
}

// �������� ���� ������ � 'target' � ����������� ���� ���������
// � �������� ����������
bool NAContainer::Copy(NAContainer *target, NStorage *stor, bool copystate) const
{
 bool res=CopyProperties(target);
 if(!res)
  return false;

 if(copystate)
 {
  res=CopyState(target);
  if(!res)
   return false;
 }

 res=CopyComponents(target,stor);
 if(!res)
  return false;

 return true;
}

// ������������ ������������ ����� ������� � ��� ���������
// ��� ����� �����������, ���� Storage == 0
void NAContainer::Free(void)
{
 if(Storage)
 {
  if(!BreakOwner())
   throw; // ��������, ����� ������ ���� ����������!!
  Storage->ReturnObject(this);
 }
 else
  delete this;
}
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ���������� ����� �������� ���������
size_t NAContainer::GetNumComponents(void) const
{
 return NumComponents;
}


// ���������� ������ ����� �������� ���������
// (������� ��� ���������� �������� ���������)
size_t NAContainer::GetNumAllComponents(void) const
{
 size_t res=NumComponents;

 for(size_t i=0;i<NumComponents;i++)
  res+=PComponents[i]->GetNumAllComponents();

 return res;
}


// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
bool NAContainer::CheckComponentType(UEPtr<NAContainer> comp) const
{
 return false;
}

// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� ��������� Id 'id'
NAContainer* NAContainer::GetComponent(const UId &id) const
{
 if(id == ForbiddenId)
  return 0;

 for(size_t i=0;i<NumComponents;i++)
  if(id == PComponents[i]->Id())
   return PComponents[i];

 return 0;
}

// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� ��������� ����� 'name'.
NAContainer* NAContainer::GetComponent(const NameT &name) const
{
 return GetComponent(GetComponentId(name));
}


// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� �������� Id 'id'.
NAContainer* NAContainer::GetComponentL(const ULongId &id) const
{
 return dynamic_cast<NAContainer*>(RDK::UAContainer::GetComponentL(id));
}

// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� �������� ����� 'name'.
NAContainer* NAContainer::GetComponentL(const NameT &name) const
{
 return dynamic_cast<NAContainer*>(RDK::UAContainer::GetComponentL(name));
}

// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� ����������� ������ � ������ ���������
// ����� ���������� 0, ���� ������ ������� �� ������� �������
NAContainer* NAContainer::GetComponentByIndex(size_t index) const
{
 if(index >= NumComponents)
  return 0;

 return PComponents[index];
}

// ��������� �������� ��������� � ���� ������
// ���������� ��� Id ��� ForbiddenId ���� ���������� ��������
// ����� ���� ������� ��������� �� ��������� ����������
UId NAContainer::AddComponent(NAContainer* comp, RDK::UIPointer* pointer)
{
 NameT namebuffer;

 if(!comp)
  return ForbiddenId;

 if(comp->GetOwner() == this)
  return comp->Id();

 if(comp->GetOwner())
  return ForbiddenId;

 if(!CheckComponentType(comp))
  return ForbiddenId;

 if(!CheckName(comp->Name()))
  comp->Name=GenerateName(comp->Name(),namebuffer);
 comp->Id=GenerateId();

 comp->Owner=this;
 // ��������� ��������� � ������� ������������ ���������
 SetLookupComponent(comp->Name(), comp->Id());

 // ���������� � ���� ���������
 AddComponentTable(comp,pointer);

 comp->OwnerTimeStep=TimeStep();

 if(MainOwner)
  comp->SetMainOwner(MainOwner);

 if(!AAddComponent(comp,pointer))
  {
   // �����
   // ������� ��������� �� ������� ������������ ���������
   DelLookupComponent(comp->Name());

   // �������� �� ���� ���������
   DelComponentTable(comp);

   comp->Owner=0;

   return ForbiddenId;
  }

 return comp->Id();
}

// ������� �������� ��������� �� ����� �������.
// ��������� ��������� ������ ����������� ������ � ���� �������.
// ����� ������� 'id' - ������ ���� �������� Id
// ���������� �������
// ���� 'canfree' == true - ��������������� ������� ������� ������ � ���������
// ��� ������� ���. ����� ������ ����������� � ��������� � ��������� �����
// ���� ��������, ���� ��������� �� �����������
bool NAContainer::DelComponent(const UId &id, bool canfree)
{
 NAContainer *comp=GetComponent(id);

 if(!comp)
  return false;

 return DelComponent(comp, canfree);
}

// ������� �������� ��������� �� ����� �������.
// ��������� ��������� ������ ����������� ������ � ���� �������.
// ����� ������� 'name' - ������ ���� �������� ������
// ���������� �������.
// ���� 'canfree' == true - ��������������� ������� ������� ������ � ���������
// ��� ������� ���. ����� ������ ����������� � ��������� � ��������� �����
// ���� ��������, ���� ��������� �� �����������
bool NAContainer::DelComponent(const NameT &name, bool canfree)
{
 return DelComponent(GetComponentId(name),canfree);
}

// ������������� ������� ��� �������� ����������
void NAContainer::DelAllComponents(void)
{
 for(size_t i=0;i<NumComponents;i++)
 {
  PComponents[i]->Owner=0;
  PComponents[i]->Free();
 }

 Components.resize(0);
 PComponents=0;
 NumComponents=0;
 CompsLookupTable.clear();
}


// ���������� ������ ���� � Id ���������, ������������ ���������������
// � ���� �������
const map<NameT,UId>& NAContainer::GetComponentsList(void) const
{ 
 return CompsLookupTable; 
}

// �������� ��� ���������� ����� ������� � ������ 'comp', ���� ��������.
bool NAContainer::CopyComponents(NAContainer* comp, NStorage* stor) const
{
 NAContainer* bufcomp;

 if(!comp)
  return false;

 // ������� ������ ���������� �� 'comp'
 comp->DelAllComponents();

 NAContainer ** pcomponents=0;
 map<UId,RDK::UIPointer*>::const_iterator I;
 map<UId,RDK::UIPointer*>::iterator J;
 if(NumComponents>0)
  pcomponents=&PComponents[0];

 for(size_t i=0;i<NumComponents;i++,pcomponents++)
  {
   bufcomp=(*pcomponents)->Alloc((*pcomponents)->Name(),stor);
   RDK::UIPointer *pointer=0;
   I=FindLookupPointer(*pcomponents);
   if(I != PointerLookupTable.end())
   {
	J=comp->PointerLookupTable.find(I->first);
	if(J != comp->PointerLookupTable.end())
	 pointer=J->second;
   }

   if(comp->AddComponent(bufcomp,pointer) == ForbiddenId)
	return false;

   bufcomp->Id=(*pcomponents)->Id;
   comp->SetLookupComponent(bufcomp->Name(), bufcomp->Id());
  }
 return true;
}
// --------------------------



// ----------------------
// ������ ���������� ����������������� ������������
// ----------------------
// ���������� ������ ������� ��������������� ���� ����������� ����.
// 'sublevel' ����������� ����� ������� ����������� �������� ��� �������
// ���������� ����� ��������� � ������.
// ���� 'sublevel' == -1, �� ���������� �������������� ���� ����������� �������
// ��� ��������� ����.
// ���� 'sublevel' == 0, �� ���������� �������������� ����������� ������ ���� ����
// ��������������� ������� ������ �� ������������.
RDK::ULongIdVector& NAContainer::GetConnectorsList(RDK::ULongIdVector &buffer,
							int sublevel, NAContainer *ownerlevel)
{
 return RDK::UAContainer::GetConnectorsList(buffer,
							sublevel, ownerlevel);
}

// ���������� ������ ������� ��������������� ���� ��������� ����.
// 'sublevel' ����������� ����� ������� ����������� �������� ��� �������
// �������� ����� ��������� � ������.
// ���� 'sublevel' == -1, �� ���������� �������������� ���� ��������� �������
// ��� ��������� ����.
// ���� 'sublevel' == 0, �� ���������� �������������� ��������� ������ ���� ����
// ��������������� ������� ������ �� ������������.
RDK::ULongIdVector& NAContainer::GetItemsList(RDK::ULongIdVector &buffer,
							int sublevel, NAContainer *ownerlevel)
{
 return RDK::UAContainer::GetItemsList(buffer,
							sublevel, ownerlevel);
}

// ���������� ������ ������� ��������������� ���� �������� ����.
// 'sublevel' ����������� ����� ������� ����������� �������� ��� �������
// ������� ����� ��������� � ������.
// ���� 'sublevel' == -1, �� ���������� �������������� ���� �������� �������
// ��� ��������� ����.
// ���� 'sublevel' == 0, �� ���������� �������������� �������� ������ ���� ����
RDK::ULongIdVector& NAContainer::GetNetsList(RDK::ULongIdVector &buffer,
							int sublevel, NAContainer *ownerlevel)
{
 return RDK::UAContainer::GetNetsList(buffer,
							sublevel, ownerlevel);
}
// ----------------------

// --------------------------
// ������ ������� � ����������
// --------------------------
// --------------------------

// --------------------------
// ������ ������� � ���������� ���������
// --------------------------

// --------------------------

// --------------------------
// ������ ���������� ������� ����������
// --------------------------
// ��������� ������ � ������
bool NAContainer::Save(RDK::UClassRegistry &buffer)
{
 return true;
}

// ��������� ������ �� ������
// ��� �������� ��������� ������������
// ��������� ����� ������� ��� storage, ���� �� �� 0
// ���� ������� ��������� �� ������, �� �� ������ ������
bool NAContainer::Load(RDK::UClassRegistry &buffer, NStorage *storage, bool paramsonly)
{
 // ������� ������ ������ ������ ���������

 return true;
}

// ��������� ��������� ������� � ������
bool NAContainer::SaveState(RDK::UClassRegistry &buffer)
{

 return true;
}

// ��������� ��������� ������� �� ������
// ���� �����-�� �� �������� ��������� �� �������, �� �� ��������� �� �����������������
// ������ ����� ���������� true.
// ���� ��� �����-�� �������� ��������� ������ ��������� �����������, ��
// ����� ���������� false
bool NAContainer::LoadState(RDK::UClassRegistry &buffer)
{

 return true;
}
// --------------------------

// --------------------------
// ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NAContainer::Default(void)
{
 Ready=false;
 for(size_t i=0;i<NumComponents;i++)
  if(!PComponents[i]->Default())
   return false;

 // ���� ���������� �������� � ���������, �� ����� ��������� ����������
 // �� ���������
 NAContainer *original=0;
 if(Storage)
  original=static_cast<NAContainer*>(Storage->GetClass(Storage->FindClass(this)));

 if(original && original != this)
 {
  NameT name=Name();
//  UId id=Id;
  bool activity=Activity();
  original->CopyProperties(this);
  Name=name;
//  Id=id;
  Activity=activity;
 }
 else    
 {
  TimeStep=DefaultTimeStep;
  if(!ADefault())
   return false;
 }

 return true;//Build();
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NAContainer::Build(void)
{
 if(Ready)
  return true;

 for(size_t i=0;i<NumComponents;i++)
  if(!PComponents[i]->Build())
   return false;

 if(ABuild())
 {
  Ready=true;
  return Reset();
 }

 Ready=false;
 return false;
}

// ����� �������� �����.
bool NAContainer::Reset(void)
{
 if(!Ready)
  return Build();

 bool key=true;
 for(size_t i=0;i<NumComponents;i++)
  if(!PComponents[i]->Reset())
  {
   key=false;
   break;
  }

 if(!key)
  return false;
  
 if(!AReset())
  return false;

 CalcCounter=0;
 return true;
}

// ��������� ������ ����� ������� 
bool NAContainer::Calculate(void)
{
 if(!Activity.v)
  return true;

 if(!Ready && !Build())
  return false;

// bool key=true;
 NAContainer **comps=PComponents;
 for(size_t i=0;i<NumComponents;++i)
  if(!(*comps++)->Calculate())
   return false;
//  {
//   key=false;
//   break;
//  }
// if(!key)
//  return false;

 if(!Owner)
  return ACalculate();

 if(TimeStep.v == OwnerTimeStep)
  return ACalculate();
 else
 if(TimeStep.v < OwnerTimeStep)
  {
   --CalcCounter;
   if(CalcCounter <= 0)
	{
	 CalcCounter=OwnerTimeStep/TimeStep.v;
	 return ACalculate();
	}
  }
 else
 if(TimeStep.v > OwnerTimeStep)
  {
   for(TimeT i=TimeStep.v/OwnerTimeStep;i>=0;--i)
	if(!ACalculate())
     return false;
  }

 // ������������ �����������
 size_t numcontrollers=Controllers.size();

 if(numcontrollers)
 {
  NController** controllers=&Controllers[0];
  for(size_t i=0;i<numcontrollers;i++,controllers++)
  {
   (*controllers)->Update();
  }
 }
 return true;
}
// --------------------------

// --------------------------
// ������ ���������� ������������� ����������
// �������� ������������ ����� �� ���������� ������
// --------------------------
// ��������� ����� ����������
bool NAContainer::AddController(NController *controller, bool forchilds)
{
 if(!controller)
  return false;

 if(CheckController(controller))
  return true;

 Controllers.push_back(controller);
 if(forchilds)
  for(size_t i=0;i<NumComponents;i++)
  {
   PComponents[i]->AddController(controller,forchilds);
  }
 return true;
}

// ������� ���������� �� ������
bool NAContainer::DelController(NController *controller, bool forchilds)
{
 vector<NController*>::iterator I=find(Controllers.begin(),Controllers.end(),controller);

 if(I != Controllers.end())
  Controllers.erase(I);

 if(forchilds)
  for(size_t i=0;i<NumComponents;i++)
  {
   PComponents[i]->DelController(controller,forchilds);
  }

 return true;
}

// ������� ��� �����������
bool NAContainer::DelAllControllers(bool forchilds)
{
 Controllers.clear();
 if(forchilds)
  for(size_t i=0;i<NumComponents;i++)
  {
   PComponents[i]->DelAllControllers(forchilds);
  }
 return true;
}

// ���������� ���������� ���� ������������
bool NAContainer::UnLinkAllControllers(bool forchilds)
{
 while(Controllers.begin() != Controllers.end())
  Controllers.front()->UnLink(this);

 if(forchilds)
  for(size_t i=0;i<NumComponents;i++)
  {
   PComponents[i]->UnLinkAllControllers(forchilds);
  }

 return true;
}


// ���������, ���������� �� ���������� � ������
bool NAContainer::CheckController(NController *controller) const
{
 if(find(Controllers.begin(),Controllers.end(),controller) != Controllers.end())
  return true;
 return false;
}

// ���������� ����� ������������
bool NAContainer::GetNumControllers(void) const
{
 return Controllers.size();
}

// ���������� ���������� �� �������
NController* NAContainer::GetController(int index)
{
 return Controllers[index];
}
// --------------------------

// --------------------------
// ������� ������ ���������� ����������
// --------------------------
// ��������� ������� ������������ ��������� ������� 'oldname'
// ��� ���������� �� 'newname'
bool NAContainer::ModifyLookupComponent(const NameT &oldname,
                                        const NameT newname)
{
 UId id;

 map<NameT,UId>::iterator I=CompsLookupTable.find(oldname);
 if(I == CompsLookupTable.end())
  return false;

 id=I->second;
 CompsLookupTable.erase(I);
 CompsLookupTable[newname]=id;

 return true;
}

// ��������� ������� ������������ ��������� ������������ Id 'id'
// ��� ���������� � ������ 'name'
void NAContainer::SetLookupComponent(const NameT &name, const UId &id)
{
 CompsLookupTable[name]=id;
 if(LastId<id)
  LastId=id;
}

// ��������� ������� ������������ ��������� ������ ������
// ���������� � ������ 'name'
void NAContainer::DelLookupComponent(const NameT &name)
{
 map<NameT,UId>::iterator I=CompsLookupTable.find(name);

 if(I == CompsLookupTable.end())
  return; 

 CompsLookupTable.erase(name);
}
// --------------------------

// --------------------------
// ������� ������ ���������� �����������
// --------------------------
// ��������� �������� � ������ 'name' � ������� �����������
// ���������� � ��������� ��� ���������� ������
// ������ ���������� � ������������� �������
UId NAContainer::AddLookupParameter(const NameT &name, UIProperty &property)
{
 map<NameT,NVariable>::iterator I=ParamsLookupTable.begin(),
                                    J=ParamsLookupTable.end();
 NVariable P;

 P.Id=1;
 P.Property=&property;

 if(ParamsLookupTable.find(name) != J)
  return ForbiddenId;

 while(I != J)
  {
   if(P.Id <= I->second.Id)
    P.Id=I->second.Id+1;
   ++I;
  }

 ParamsLookupTable.insert(make_pair(name,P));

 return P.Id;
}

// ������� �������� � ������ 'name' �� ������� �����������
// ����������
bool NAContainer::DelLookupParameter(const NameT &name)
{
 map<NameT,NVariable>::iterator I=ParamsLookupTable.find(name);

 if(I == ParamsLookupTable.end())
  return false; 

 ParamsLookupTable.erase(I);
 return true;
}


// ���������� ������ ��� ��������� ��� �������� NMSDK, � �������� '*'
NameT NAContainer::GetParameterLongName(const UIProperty &property) const
{
 NameT name=property.GetOwnerName();

 size_t i=name.find("NMSDK::");
 if(i == NameT::npos)
  i=0;
 else
  i=7;

 size_t j=name.find_last_of("*");
 if(j == NameT::npos)
  j=name.size()-i;
 else
  j-=i+1;

 return name.substr(i,j);
}
// --------------------------

// --------------------------
// ������� ������ ���������� ����������
// --------------------------
// ��������� ���������� ��������� � ������ 'name' � ������� �����������
// ���������� � ��������� �� ���������� ������
// ������ ���������� � ������������� �������
UId NAContainer::AddLookupState(const NameT &name,UIProperty &property)
{
 map<NameT,NVariable>::iterator I=StateLookupTable.begin(),
									J=StateLookupTable.end();
 NVariable P;

 P.Id=1;
 P.Property=&property;

 if(StateLookupTable.find(name) != J)
  return ForbiddenId;

 while(I != J)
  {
   if(P.Id <= I->second.Id)
	P.Id=I->second.Id+1;
   ++I;
  }

 StateLookupTable.insert(make_pair(name,P));

 return P.Id;
}

// ������� ���������� ��������� � ������ 'name' �� ������� �����������
bool NAContainer::DelLookupState(const NameT &name)
{
 map<NameT,NVariable>::iterator I=StateLookupTable.find(name);

 if(I == StateLookupTable.end())
  return false;

 StateLookupTable.erase(I);
 return true;
}

// ���������� ������ ��� ���������� ��������� ��� �������� NMSDK, � �������� '*'
NameT NAContainer::GetStateLongName(const UIProperty &property) const
{
 NameT name=property.GetOwnerName();

 size_t i=name.find("NMSDK::");
 if(i == NameT::npos)
  i=0;
 else
  i=7;

 size_t j=name.find_last_of("*");
 if(j == NameT::npos)
  j=name.size()-i;
 else
  j-=i+1;

 return name.substr(i,j);
}
// --------------------------

// --------------------------
// ������� ������ ���������� ���������� �����������
// --------------------------
// ��������� ��������� � ������� �����������
// ������ ���������� � ������������� �������
UId NAContainer::AddLookupPointer(RDK::UIPointer &pointer)
{
 map<UId,RDK::UIPointer*>::iterator I=PointerLookupTable.begin(),
									J=PointerLookupTable.end();
 UId id=1;

 while(I != J)
  {
   if(id <= I->first)
	id=I->first+1;
   ++I;
  }

 PointerLookupTable.insert(make_pair(id,&pointer));

 return id;
}

// ������� ��������� � ID 'id' �� ������� �����������
bool NAContainer::DelLookupPointer(const UId &id)
{
 map<UId,RDK::UIPointer*>::iterator I=PointerLookupTable.find(id);

 if(I == PointerLookupTable.end())
  return true;

 PointerLookupTable.erase(I);
 return true;
}

// ���������� ������ ��� ��������� ��� �������� NMSDK, � �������� '*'
NameT NAContainer::GetPointerLongName(const RDK::UIPointer &property) const
{
 return "";
}

// ������������ ����� � ������� ���������, ���������������� ��������� ���������
map<UId,RDK::UIPointer*>::const_iterator NAContainer::FindLookupPointer(const NAContainer *source) const
{
 map<UId,RDK::UIPointer*>::const_iterator I=PointerLookupTable.begin(),
									J=PointerLookupTable.end();

 while(I != J)
  {
   if(I->second && I->second->Find(source)>=0)
	break;
   ++I;
  }

 return I;
}

// --------------------------


// --------------------------
// ������� ������ ���������� �������� ���������
// --------------------------
// ��������� ��������� 'comp' � ������� ���������
void NAContainer::AddComponentTable(NAContainer *comp, RDK::UIPointer* pointer)
{
 Components.push_back(comp);
 PComponents=&Components[0];
 NumComponents=Components.size();

 if(pointer)
  pointer->Set(comp);
 else
 {
  map<UId,RDK::UIPointer*>::const_iterator I=FindLookupPointer(comp);
  if(I != PointerLookupTable.end())
  {
   I->second->Del(comp);
  }
 }
}

// ������� ��������� 'comp' �� ������� ���������
void NAContainer::DelComponentTable(NAContainer *comp)
{
 size_t i;

 if(PComponents[NumComponents-1]==comp)
  Components.resize(NumComponents-1);
 else
  {
   for(i=0;i<NumComponents;i++)
    if(PComponents[i] == comp)
     break;

   if(i>=NumComponents)
    return;

   memmove(PComponents+i,PComponents+i+1,(NumComponents-i-1)*sizeof(NAContainer*));
   Components.resize(NumComponents-1);
  }

 NumComponents=Components.size();
 if(NumComponents>0)
  PComponents=&Components[0];
 else
  PComponents=0;

 map<UId,RDK::UIPointer*>::const_iterator I=FindLookupPointer(comp);
 if(I != PointerLookupTable.end())
 {
  I->second->Del(comp);
 }
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������������
// --------------------------
// ������� ��������� comp
// ����� ������������, ��� ��������� ����������� �������
bool NAContainer::DelComponent(NAContainer* comp, bool canfree)
{
 if(!ADelComponent(comp))
  return false;

 if(comp->GetMainOwner() == MainOwner)
  comp->SetMainOwner(0);

 // �������� �� ���� ���������
 // ������� ��������� �� ������� ������������ ���������
 DelLookupComponent(comp->Name());

 // �������� �� ���� ���������
 DelComponentTable(comp);

 comp->Owner=0;

 if(canfree)
  comp->Free();
 return true;
}


// ��������� ����������� ���������������� ��������
// ��� ���������� ��������� ���������� � ���� ������
// ����� ����� ������ ������ ���� comp ���
// ������� �������� � ������ ���������
bool NAContainer::AAddComponent(UEPtr<UAContainer> comp, RDK::UIPointer* pointer)
{
 return true;
}

// ��������� ��������������� ���������������� ��������
// ��� �������� ��������� ���������� �� ����� �������
// ����� ����� ������ ������ ���� comp
// ���������� � ������ ���������
bool NAContainer::ADelComponent(UEPtr<UAContainer> comp)
{
 return true;
}
// --------------------------

/* *************************************************************************** */



/* *************************************************************************** */
/*
// --------------------------
// ������������ � �����������
// --------------------------
NAConnector::NAConnector(void)
// : NAContainer(name),
 : NumInputs("NumInputs",this,&NAConnector::SetNumInputs,&NAConnector::GetNumInputs),
   AutoNumInputs("AutoNumInputs",this)
{
 NumInputs=0;
}

NAConnector::~NAConnector(void)
{
 DisconnectAllItems();
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ���� ������ � 'target' � ����������� ���� ���������
// � �������� ����������
// ���� 'stor' == 0, �� �������� �������� ��������������
// � ��� �� ��������� ��� ������������� ���� ������
bool NAConnector::Copy(NAContainer *target, NStorage *stor, bool copystate) const
{
 if(!dynamic_cast<NAConnector*>(target))
  return false;

 if(NAContainer::Copy(target,stor,copystate))
  return CopyInputSymLinks(static_cast<NAConnector*>(target));

 return false;
}
// --------------------------

// --------------------------
// ������ ������� � ������
// --------------------------
// ���������� ������������ � ����� ���������� ������ �� �������
CItemT NAConnector::GetCItem(int c_index) const
{
 return CItemList[c_index];
}

// ���������� ���� �������� <�����, ����> ����������� ����� item ��� <-1,-1>
// ���� ����� ����� �����������
pair<int,int> NAConnector::GetCItemIndexes(const NAItem *item) const
{
 pair<int,int> indexes;
 indexes.first=indexes.second=-1;

 if(!item)
  return indexes;

 for(size_t i=0;i<CItemList.size();i++)
  if(CItemList[i].Item == item)
  {
   indexes.first=CItemList[i].Index;
   indexes.second=i;
   break;
  }

 return indexes;
}
// --------------------------

// --------------------------
// ������ ���������� �������������� ��������
// --------------------------
// ���������� ����� ������������� ������ �� �����
size_t NAConnector::GetNumInputSymLinks(void) const
{
 return GetNumSymLinks(InputSymLinks);
}

// ���������� ������ ����� �� ������������� ������
size_t NAConnector::GetInputSymLink(const string &name) const
{
 return GetSymLink(name, InputSymLinks);
}

// ��������� ����� ������������� ������ �� ����
// ���������� false ���� ����� ��� ��� ����������
bool NAConnector::AddInputSymLink(const string &name, size_t index)
{
 return AddSymLink(name,index,InputSymLinks);
}

// ������� ������������� ������ �� ���� �� �����
void NAConnector::DelInputSymLink(const string &name)
{
 DelSymLink(name, InputSymLinks);
}

// ������� ��� ������������� ������ �� �������� ����
void NAConnector::DelInputSymLink(size_t index)
{
 DelSymLink(index, InputSymLinks);
}

// ������� ��� ������������� ������
void NAConnector::DelInputSymLinks(void)
{
 DelSymLinks(InputSymLinks);
}

// ���������� ���� ������ ������
void NAConnector::GetInputSymLinksList(vector<NameT> &buffer) const
{
 GetSymLinksList(buffer,InputSymLinks);
}

// �������� ������������� ������ � ������ target
bool NAConnector::CopyInputSymLinks(NAConnector *target) const
{
 return CopySymLinks(target,InputSymLinks);
}
// --------------------------

// ----------------------
// ���������������� ������
// ----------------------
// ������������� ����� � ��������� ���� 'na'.
bool NAConnector::ConnectToItem(NAItem *na, int i_index, int &c_index)
{
 if(!na)
  return false;

 if((c_index < 0 || c_index >= int(NumInputs)) && AutoNumInputs == false)
  return false;

 if(i_index < 0 || i_index >= int(na->NumOutputs))
  return false;

 // ���� ������� ����� ��������������� ���������� ������ �����
 // � c_index<0 �� ��������� ����� ���� ���� ������������ � ����������� ����������
 if(c_index<0)
 {
  size_t i=0;
//  for(i=0;i<NumInputs;i++)
  for(i=0;i<CItemList.size();i++)
   if(!CItemList[i].Item)
	break;

  if(i == NumInputs)
  {
   NumInputs=NumInputs+1;
   c_index=NumInputs-1;
  }
  else
   c_index=i;
 }
 else // ���� c_index >= NumInputs �� ��������� ����� ������ �� ����������
 if(c_index >= int(NumInputs))
 {
  NumInputs=c_index+1;
 }

 if(!Build())
  return false;

 if(CItemList[c_index].Item == na)
 {
  if(CItemList[c_index].Index == i_index)
   return true;

  CItemList[c_index].Index = i_index;
  return true;
 }

 if(CItemList[c_index].Item)
  return false;

 CItemList[c_index].Item=na;
 CItemList[c_index].Index=i_index;
 return AConnectToItem(na);
}

// ��������� ����� � ��������� ���� 'na'
void NAConnector::DisconnectFromItem(NAItem *na)
{
 if(!na)
  return;

// Build();

 for(size_t i=0;i<CItemList.size();i++)
 {
  if(CItemList[i].Item == na)
  {
   DisconnectFromIndex(i);
  }
 }
}

// ��������� ����� � ��������� ���� ������������ �� ����� 'index'
void NAConnector::DisconnectFromIndex(int c_index)
{
 if(c_index<0 || c_index >=int(NumInputs))
  return;

// Build();

 ADisconnectFromItem(CItemList[c_index].Item);
 CItemList[c_index].Item=0;
 CItemList[c_index].Index=-1;
}

// ��������� �������� ����� ��������� ������������ �����
bool NAConnector::AConnectToItem(NAItem *na)
{
 return true;
}

// ��������� �������� ����� ��������� ���������� �����
void NAConnector::ADisconnectFromItem(NAItem *na)
{
}

// ��������� ��� ������� �����
void NAConnector::DisconnectAllItems(void)
{
// Build();
 for(size_t i=0;i<CItemList.size();i++)
  if(CItemList[i].Item)
   CItemList[i].Item->Disconnect(this);
}

// ��������� ��� ����� �������
// �������� ��� ���������� ����� � �������� �����
// brklevel - ������, ������������ �������� ����� ��������� �����������
void NAConnector::DisconnectByObject(const NAContainer *brklevel)
{
// Build();
 for(size_t i=0;i<CItemList.size();i++)
  if(CItemList[i].Item)
   if(!CItemList[i].Item->CheckOwner(brklevel))
	CItemList[i].Item->Disconnect(this);
}

// ���������� ���� ��������� (�������� ������ �� ����� ������
// ����� ����������).
void NAConnector::Activate(NAItem *na)
{
// Build();
}

// ���������� ������ �����������
LinksListT& NAConnector::GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const
{
 LinkT link;
 GetLongId(netlevel,link.second.Id);
 if(link.second.Id.GetSize()==0)
  return linkslist;

 for(size_t i=0;i<CItemList.size();i++)
 {
  if(CItemList[i].Item)
  {
   CItemList[i].Item->GetLongId(netlevel,link.first.Id);
   link.second.Index=i;
   link.first.Index=CItemList[i].Index;
   if(link.first.Id.GetSize() != 0)
   {
	LinksListCIterator I,J;
	I=linkslist.begin();
	J=linkslist.end();
	while(I != J)
	{
	 if(I->first == link.first && I->second == link.second)
	  break;
	 ++I;
	}

	if(I == J)
	 linkslist.insert(link);
	else
	{
	 continue;
	}
   }
  }
 }

 return linkslist;
}
// ----------------------


// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ���������� ����� ������������ ��������� item
size_t NAConnector::GetNumInputs(void) const
{
 return NumInputs;
}

// ������������� ����� ������������ ��������� item
bool NAConnector::SetNumInputs(size_t value)
{
 NumInputs=CItemList.size();
 if(value > NumInputs)
 {
  for(size_t i=value;i<NumInputs;++i)
   if(CItemList[i].Item)
	CItemList[i].Item->Disconnect(this);
 }

 int index=int(NumInputs);
 CItemList.resize(value);
 for(size_t i=index;i<value;i++)
 {
  CItemList[i].Item=0;
  CItemList[i].Index=-1;
 }

 Ready=false;
 NumInputs=CItemList.size();
 return true;
}
// --------------------------

// --------------------------
// ������� ������ ���������� �������������� ��������
// --------------------------
// ���������� ����� ������������� ������
size_t NAConnector::GetNumSymLinks(const map<NameT, size_t> &symlinks) const
{
 return symlinks.size();
}

// ���������� ������ �� ������������� ������
size_t NAConnector::GetSymLink(const string &name, const map<NameT, size_t> &symlinks) const
{
 map<NameT, size_t>::const_iterator I=symlinks.find(name);

 if(I == symlinks.end())
  return 0xFFFFFFFF;

 return I->second;
}

// ��������� ����� ������������� ������
// ���������� false ���� ����� ��� ��� ����������
bool NAConnector::AddSymLink(const string &name, size_t index, map<NameT, size_t> &symlinks)
{
 map<NameT, size_t>::iterator I=symlinks.find(name);

 if(I != symlinks.end())
  return false;

 symlinks[name]=index;
 return true;
}

// ������� ������������� ������ �� �����
void NAConnector::DelSymLink(const string &name, map<NameT, size_t> &symlinks)
{
 map<NameT, size_t>::iterator I=symlinks.find(name);

 if(I != symlinks.end())
  symlinks.erase(I);
}

// ������� ��� ������������� ������ �� �������
void NAConnector::DelSymLink(size_t index, map<NameT, size_t> &symlinks)
{
 map<NameT, size_t>::iterator I,J,K;

 I=symlinks.begin();
 J=symlinks.end();

 while(I != J)
 {
  if(I->second == index)
  {
   K=I; ++I;
   symlinks.erase(K);
  }
  else
   ++I;
 }
}

// ������� ��� ������������� ������
void NAConnector::DelSymLinks(map<NameT, size_t> &symlinks)
{
 symlinks.clear();
}

// ���������� ���� ������ ������
void NAConnector::GetSymLinksList(vector<NameT> &buffer, const map<NameT, size_t> &symlinks) const
{
 map<NameT, size_t>::const_iterator I,J;

 I=symlinks.begin();
 J=symlinks.end();
 buffer.resize(symlinks.size());
 size_t i=0;

 while(I != J)
 {
  buffer[i++]=I->first;
  ++I;
 }
}

// �������� ������������� ������ � ������ target
bool NAConnector::CopySymLinks(NAConnector *target, const map<NameT, size_t> &symlinks) const
{
 if(!target)
  return false;

 target->InputSymLinks=symlinks;
 return true;
}
// --------------------------

// --------------------------
// ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NAConnector::Default(void)
{
 NumInputs=1;
 AutoNumInputs=true;
 return NAContainer::Default();
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NAConnector::Build(void)
{
 return NAContainer::Build();
}
// --------------------------
			*/
/* *************************************************************************** */

/* *************************************************************************** */
// ������
/*
// --------------------------
// ������������ � �����������
// --------------------------
NAItem::NAItem(void)
// : NAConnector(name),
 : NumOutputs("NumOutputs",this,&NAItem::SetNumOutputs,&NAItem::GetNumOutputs)
{
 CNumOutputs=0;
}

NAItem::~NAItem(void)
{
 DisconnectAll();
}
// --------------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ���������� ����� ������������ ��������� item
size_t NAItem::GetNumOutputs(void) const
{
 return AssociatedConnectors.size();
}

// ������������� ����� ������������ ��������� item
bool NAItem::SetNumOutputs(size_t value)
{
 if(value == AssociatedConnectors.size())
  return true;

 if(value > AssociatedConnectors.size())
 {
  for(size_t i=value;i<AssociatedConnectors.size();i++)
   for(size_t j=0;j<AssociatedConnectors[i].size();j++)
	Disconnect(AssociatedConnectors[i][j]);
 }

 AssociatedConnectors.resize(value);
 CNumOutputs=value;
 Ready = false;
 return true;
}
// --------------------------

// ----------------------
// ���������� ���������������� ������
// ----------------------
// ������������� ����� � ����������� 'c'.
bool NAItem::Connect(NAConnector *c, int i_index, int c_index)
{
 if(c == 0)
  return false;

 if(!Build())
  return false;

 if(!c->ConnectToItem(this,i_index,c_index))
  return false;

 AssociatedConnectors[i_index].push_back(c);
 PAssociatedConnectors[i_index]=&AssociatedConnectors[i_index][0];
 NumAConnectors[i_index]=AssociatedConnectors[i_index].size();

 return true;
}

// ��������� ����� ������ ����� ������� � ����������� 'c'.
void NAItem::Disconnect(NAConnector *c)
{
 Build();

 c->DisconnectFromItem(this);

 for(size_t i=0;i<AssociatedConnectors.size();i++)
 {
  vector<NAConnector*>::iterator I=find(AssociatedConnectors[i].begin(),
										AssociatedConnectors[i].end(),
										c);
  while(I != AssociatedConnectors[i].end())
  {
   AssociatedConnectors[i].erase(I);
   NumAConnectors[i]=AssociatedConnectors[i].size();
   if(NumAConnectors[i]>0)
	PAssociatedConnectors[i]=&AssociatedConnectors[i][0];
   else
	PAssociatedConnectors[i]=0;

   I=find(AssociatedConnectors[i].begin(),AssociatedConnectors[i].end(),c);
  }
 }
}
// ----------------------

// ----------------------
// ���������������� ������
// ----------------------
// ���������� ������� ����� ����������.
size_t NAItem::GetNumAConnectors(int index) const
{
 return NumAConnectors[index];
}

// ��������� ����� ������ ����� ������� � ����������� �� Id 'id'.
bool NAItem::Disconnect(const UId &id)
{
 Build();

 for(size_t j=0;j<AssociatedConnectors.size();j++)
  for(size_t i=0;i<NumAConnectors[j];i++)
  {
   if(PAssociatedConnectors[j][i]->Id == id)
	{
	 Disconnect(PAssociatedConnectors[j][i]);
	  break;
	}
  }
 return true;
}

// ��������� ����� ������ ����� ������� �� �����
// ������������� ������������.
void NAItem::DisconnectAll(void)
{
 Build();
 for(size_t i=0;i<AssociatedConnectors.size();i++)
 {
  while(AssociatedConnectors[i].size() > 0)
  {
   Disconnect(AssociatedConnectors[i].back());
  }
  AssociatedConnectors[i].clear();
  PAssociatedConnectors[i]=0;
  NumAConnectors[i]=0;
 }
}

// ��������� ��� ����� �������
// �������� ��� ���������� ����� � �������� �����
// brklevel - ������, ������������ �������� ����� ��������� �����������
void NAItem::DisconnectBy(const NAContainer *brklevel)
{
 Build();

 vector<NAConnector*>::const_iterator I,J,K;

 for(size_t i=0;i<AssociatedConnectors.size();i++)
 {
  I=AssociatedConnectors[i].begin();
  J=AssociatedConnectors[i].end();
  while(I != J)
  {
   if(!(*I)->CheckOwner(brklevel))
	{
	 K=I; ++I;
	 Disconnect(*K);
	}
   else
	++I;
  }
 }
}

// ����������������� ��� ����� ����� item �� ����� connectors ������� ��������
// ������ �� ����� item
void NAItem::BuildLinks(void)
{
 PAssociatedConnectors.resize(NumOutputs);
 NumAConnectors.resize(NumOutputs);

 for(size_t i=0;i<NumOutputs;i++)
 {
  NumAConnectors[i]=AssociatedConnectors[i].size();
  if(NumAConnectors[i]>0)
   PAssociatedConnectors[i]=&AssociatedConnectors[i][0];

  for(size_t j=0;j<NumAConnectors[i];j++)
  {
   pair<int,int> indexes=PAssociatedConnectors[i][j]->GetCItemIndexes(this);
   PAssociatedConnectors[i][j]->ConnectToItem(this,indexes.first,indexes.second);
  }
 }
}

// ���������� ��������� �� ��������� �� ������ �����������
// �� ����� 'name'.
const NAConnector* NAItem::GetAConnector(const UId &id, int index) const
{
 for(size_t i=0;i<NumAConnectors[index];i++)
  if(PAssociatedConnectors[index][i]->Id == id)
   return PAssociatedConnectors[index][i];
 return 0;
}

// ����������  ��������� �� ������ �����������.
const NAConnector* NAItem::GetAConnectorByIndex(int output, int index) const
{
 return AssociatedConnectors[output][index];
}

// ���������� ������ �����������
LinksListT& NAItem::GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const
{
 LinkT link;

 GetLongId(netlevel,link.first.Id);
 if(link.first.Id.GetSize() == 0)
  return linkslist;


 for(size_t j=0;j<AssociatedConnectors.size();j++)
  for(size_t i=0;i<NumAConnectors[j];i++)
  {
   PAssociatedConnectors[j][i]->GetLongId(netlevel,link.second.Id);
   if(link.second.Id.GetSize() != 0)
   {
	pair<int,int> indexes=PAssociatedConnectors[j][i]->GetCItemIndexes(this);
	link.first.Index=indexes.first;
	link.second.Index=indexes.second;

	LinksListCIterator I,J;
	I=linkslist.begin();
	J=linkslist.end();
	while(I != J)
	{
	 if(I->first == link.first && I->second == link.second)
	  break;
	 ++I;
	}

	if(I == J)
	 linkslist.insert(link);
	else
	{
	 continue;
	}
//	linkslist.insert(link);
   }
  }

 return linkslist;
}

// ���������� ������ ����������� ����� ���������� � ���� �������� ���������
// � ��������� ���������� comp � ���� ��� �������� �����������
LinksListT& NAItem::GetFullItemLinks(LinksListT &linkslist, const NAItem *comp,
									 const NAContainer *netlevel) const
{
 LinkT link;

 if(!comp)
  return linkslist;

 GetLongId(netlevel,link.first.Id);
 if(link.first.Id.GetSize() == 0)
  return linkslist;


 for(size_t j=0;j<AssociatedConnectors.size();j++)
  for(size_t i=0;i<NumAConnectors[j];i++)
  {
   if(!PAssociatedConnectors[j][i]->CheckOwner(comp) && PAssociatedConnectors[j][i] != comp)
    continue;
   PAssociatedConnectors[j][i]->GetLongId(netlevel,link.second.Id);
   if(link.second.Id.GetSize() != 0)
   {
	pair<int,int> indexes=PAssociatedConnectors[j][i]->GetCItemIndexes(this);
	link.first.Index=indexes.first;
	link.second.Index=indexes.second;

	LinksListCIterator I,J;
	I=linkslist.begin();
	J=linkslist.end();
	while(I != J)
	{
	 if(I->first == link.first && I->second == link.second)
	  break;
	 ++I;
	}

	if(I == J)
	 linkslist.insert(link);
	else
	{
	 continue;
	}
//	linkslist.insert(link);
   }
  }

 for(size_t i=0;i<NumComponents;i++)
 {
  NAItem* item=dynamic_cast<NAItem*>(PComponents[i]);
  if(item)
   item->GetFullItemLinks(linkslist, comp, netlevel);
 }

 return linkslist;
}
// ----------------------


// --------------------------
// ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NAItem::Default(void)
{
 NumOutputs=1;
 return NAConnector::Default();
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NAItem::Build(void)
{
 if(IsReady())
  return true;

 BuildLinks();

 return NAConnector::Build();
}

// ���������� ��� ����������, ������������ � ������ ����� �������.
void NAItem::ActivateAll(void)
{
 Build();
 for(size_t j=0;j<AssociatedConnectors.size();j++)
  for(size_t i=0;i<NumAConnectors[j];i++)
   PAssociatedConnectors[j][i]->Activate(this);
}           */
/* *************************************************************************** */

/* *************************************************************************** */

// ������
/*
// --------------------------
// ������������ � �����������
// --------------------------
NADItem::NADItem(void)
// : NAItem(name),
 : OutputSize("OutputSize",this,&NADItem::SetVOutputSize,&NADItem::GetVOutputSize),
   DataOutputSize("DataOutputSize",this,&NADItem::SetVDataOutputSize,&NADItem::GetVDataOutputSize)
{
 // ��������� �� ������ ������� ������� ���������� �� ������� ������
 POutputData=0;

 // ��������� �� ������ ������� ������� ���������� �� ������� ������
 PInputData=0;

 // ��������� �� ������ ������� ������� �������� �������� ������
 PInputDataSize=0;

 // ��������� ����� ���� ������
 FullInputSize=0;

 // ����������� ������ ������� ������
 MinInputDataSize=0;

 // ������������ ������ ������� ������
 MaxInputSize=0;
}

NADItem::~NADItem(void)
{
// DisconnectAll();
}                       
// --------------------------

// --------------------------
// ������ ������� � ���������
// --------------------------

// ���������� ��������� �� ������ ������ Input �� ��������� �� item
// ���������� 0 ���� citem == 0 ��� �� ������ � ������ �����������
const NIOData* NADItem::GetInputData(NAItem *citem) const
{
 NIOData result;

 if(!citem)
  return 0;

 pair<int,int> indexes=GetCItemIndexes(citem);
 if(indexes.second < 0)
  return 0;

 return PInputData[indexes.second];
}

// ���������� ��������� �� ������ ������ Input �� �������
// �� ��������� ������ �� ������������
const NIOData* NADItem::GetInputData(size_t index) const
{
// if(!PInputData || index>=Input.size())
//  return 0;

 return PInputData[index];
}

// ���������� ������ ������� ������ Input �� �������
// �� ��������� ������ �� ������������
size_t NADItem::GetInputSize(size_t index) const
{
// if(!PInputDataSize || index>=Input.size())
//  return 0;

 return PInputDataSize[index];
}

// ���������� ��������� ������ ���� �������� ������
size_t NADItem::GetFullInputSize(void) const
{
 return FullInputSize;
}
// --------------------------


// ----------------------
// ������ ���������� ��������� �������
// ----------------------
size_t NADItem::GetOutputDataSize(int index) const
{
 return Output[index].Size;
}

bool NADItem::SetOutputDataSize(int index, size_t size, bool nobuild)
{
// if(!Build())
//  return false;

 if(index < 0)// || index >= int(Output.size()))
  return false;

 if(Output.size() > size_t(index))
 {
  if(Output[index].Size == size)
   return true;
 }
 else
  Output.resize(index+1);

 Output[index].Resize(size);

 if(!nobuild)
  Ready=false;
 return true;
}

bool NADItem::SetDataOutputSize(int index, size_t size)
{
// if(!Build())
//  return false;

 if(index < 0)// || index >= int(Output.size()))
  return false;

 if(Output.size() > size_t(index))
 {
  if(Output[index].DataSize == size)
   return true;
 }
 else
  Output.resize(index+1);

 Output[index].SetDataSize(size);

 Ready=false;
 return true;
}

// ��������� �������� �������� ������ �������
void NADItem::FillOutputData(int index, const void *data)
{
 if(!Ready && !Build())
  return;

 if(index < 0 || index >= int(Output.size()))
  return;

 NIOData &dest=Output[index];

 if(!data)
  memset(dest.Void,0,dest.ByteSize);
 else
  dest.Assign(dest.Size,data);
}

// ��������� ��� �������� ������� ��������� �������
void NADItem::FillOutputData(const void *data)
{
 if(!Ready && !Build())
  return;

 size_t size=Output.size();
 if(!size)
  return;

 NIOData* dest=&Output[0];
 for(size_t i=0;i<size;++i,++dest)
  if(!data)
  {
   if(dest->ByteSize && dest->Void)
	memset(dest->Void,0,dest->ByteSize);
  }
  else
   dest->Assign(dest->Size,data);
}
// ----------------------

// ----------------------
// ������ ������� � ��������� ���������
// ----------------------
// ������ �������� ��������
vector<size_t> NADItem::GetVOutputSize(void) const
{
 vector<size_t> result;

 size_t size=Output.size();
 result.resize(size);
 for(size_t i=0;i<size;i++)
  result[i]=Output[i].Size;

 return result;
}

bool NADItem::SetVOutputSize(const vector<size_t> value)
{
// if(!Build())
//  return false;

// if(Output.size() != value.size())
//  return false;

 size_t size=value.size();
 if(Output.size()<size)
  Output.resize(size);

 for(size_t i=0;i<size;i++)
  if(!SetOutputDataSize(i,value[i]))
   return false;

 return true;
}

// ������ ���������� ������� ������� ������� � ������
vector<size_t> NADItem::GetVDataOutputSize(void) const
{
 vector<size_t> result;

 size_t size=Output.size();
 result.resize(size);
 for(size_t i=0;i<size;i++)
  result[i]=Output[i].DataSize;

 return result;
}

bool NADItem::SetVDataOutputSize(const vector<size_t> value)
{
// if(Output.size() != value.size())
//  return false;

 size_t size=value.size();
 if(Output.size()<size)
  Output.resize(size);

 for(size_t i=0;i<size;i++)
  if(!SetDataOutputSize(i,value[i]))
   return false;

 return true;
}
// ----------------------

// ----------------------
// ���������������� ������
// ----------------------
// ������������� ����� � ��������� ���� 'na' �� ������ �� ������� index.
// ������������� ����� ���� na ��� ���������.
bool NADItem::ConnectToItem(NAItem *na, int i_index, int &c_index)
{
 NADItem* nad=dynamic_cast<NADItem*>(na);
 if(!nad)
  return false;

 if(!NAConnector::ConnectToItem(nad, i_index, c_index))
  return false;

// if(!nad->Build())
//  return false;

 InputSize[c_index]=nad->POutputData[i_index].Size;
 Input[c_index]=&nad->POutputData[i_index];

 UpdatePointers();
 CalcMinMaxInputsSize();
 return true;
}

// ��������� ����� � ��������� ���� ������������ �� ����� 'index'
void NADItem::DisconnectFromIndex(int c_index)
{
 if(c_index<0 || c_index >= int(Input.size()))
  return;

 InputSize[c_index]=0;
 Input[c_index]=0;

 NAConnector::DisconnectFromIndex(c_index);

 UpdatePointers();
 CalcMinMaxInputsSize();
}
// --------------------------

// --------------------------
// ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NADItem::Default(void)
{
 SetDataOutputSize(0,sizeof(real));
 SetOutputDataSize(0,1);

 return NAItem::Default();
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NADItem::Build(void)
{
 if(IsReady())
  return true;

 Output.resize(NumOutputs);
 Input.resize(NumInputs);
 InputSize.resize(NumInputs);
 UpdatePointers();

 if(!NAItem::Build())
  return false;

 return true;
}

// ����� �������� ����� ��� ������ ��������
bool NADItem::Reset(void)
{
 if(!NAContainer::Reset())
  return false;
 FillOutputData();

 return true;
}
// --------------------------

// ----------------------
// ��������������� ������
// ----------------------
// ��������� ��������� �� ������� ������ � �������
void NADItem::UpdatePointers(void)
{
 if(NumOutputs>0)
 {
  POutputData=&Output[0];
 }
 else
 {
  POutputData=0;
 }

 if(NumInputs>0)
 {
  // ��������� �� ������ ������� ������� ���������� �� ������� ������
  PInputData=&Input[0];

  // ��������� �� ������ ������� ������� �������� �������� ������
  PInputDataSize=&InputSize[0];
 }
 else
 {
  // ��������� �� ������ ������� ������� ���������� �� ������� ������
  PInputData=0;

  // ��������� �� ������ ������� ������� �������� �������� ������
  PInputDataSize=0;
 }

 // ��������� ����� ���� ������
 FullInputSize=0;
 for(size_t i=0;i<NumInputs;i++)
  FullInputSize+=PInputDataSize[i];
}


// ��������� ����������� � ������������ ������ �������� ������
void NADItem::CalcMinMaxInputsSize(void)
{
 vector<size_t>::const_iterator I;

 I=min_element(InputSize.begin(),InputSize.end());

 if(I != InputSize.end())
  MinInputDataSize=*I;
 else
  MinInputDataSize=0;

 I=max_element(InputSize.begin(),InputSize.end());

 if(I != InputSize.end())
  MaxInputSize=*I;
 else
  MaxInputSize=0;
}
// ----------------------
*/
/* *************************************************************************** */


/* *************************************************************************** */
/*
// --------------------------
// ������������ � �����������
// --------------------------
NANet::NANet(void)
// : NADItem(name)
{
}

NANet::~NANet(void)
{
}
// --------------------------

// --------------------------
// ������ ������� � ���������
// --------------------------
LinksListT& NANet::GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const
{
 GetLinks(this, linkslist, netlevel);

 return linkslist;
}
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
bool NANet::CheckComponentType(UEPtr<NAContainer> comp) const
{
 return (dynamic_cast<const NAItem*>(comp) ||
 dynamic_cast<const NANet*>(comp) || dynamic_cast<const NAConnector*>(comp))?true:false;
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������������
// --------------------------
// ��������� ����������� ���������������� ��������
// ��� ���������� ��������� ���������� � ���� ������
// ����� ����� ������ ������ ���� comp ���
// ������� �������� � ������ ���������
bool NANet::AAddComponent(UEPtr<UAContainer> comp, RDK::UIPointer* pointer)
{
 return true;
}

// ��������� ��������������� ���������������� ��������
// ��� �������� ��������� ���������� �� ����� �������
// ����� ����� ������ ������ ���� comp
// ���������� � ������ ���������
bool NANet::ADelComponent(UEPtr<UAContainer> comp)
{
 if(dynamic_cast<NAItem*>(comp))
  ((NAItem*)comp)->DisconnectBy(this);
 else
 if(dynamic_cast<NANet*>(comp))
  ((NANet*)comp)->BreakLinks(this);
 return true;
}
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ���� ������ � 'target' � ����������� ���� ���������
// � �������� ����������
// ���� 'stor' == 0, �� �������� �������� ��������������
// � ��� �� ��������� ��� ������������� ���� ������
bool NANet::Copy(NAContainer *target, NStorage *stor, bool copystate) const
{
 LinksListT linkslist;
 LinksListT oldlinkslist;

 if(!dynamic_cast<NANet*>(target))
  return false;

 if(NAContainer::Copy(target,stor,copystate))
  {
   ((NANet*)target)->BreakLinks();
   if(((NANet*)target)->CreateLinks(GetLinks(linkslist,this)))
    return true;
  }

 return false;
}
// --------------------------

// ----------------------
// ������ ���������� �������
// ----------------------
// ������������� ����� ����� ����� ������� �������� ����
// 'item' � ����������� 'connector'
bool NANet::CreateLink(const LinkSideT &item, const LinkSideT &connector)
{
 NAItem *pitem=dynamic_cast<NAItem*>(GetComponentL(item.Id));
 NAConnector *pconnector=dynamic_cast<NAConnector*>(GetComponentL(connector.Id));

 if(!pitem)
  return false;

 if(!pconnector)
  return false;

 if(!(pitem->Connect(pconnector,item.Index,connector.Index)))
  return false;

 return true;
}

// ������������� ����� ����� ����� ������� �������� ����
// 'item' � ����������� 'connector'
bool NANet::CreateLink(const NameT &item, int item_index,
						const NameT &connector, int connector_index)
{
 NAItem *pitem=dynamic_cast<NAItem*>(GetComponentL(item));
 NAConnector *pconnector=dynamic_cast<NAConnector*>(GetComponentL(connector));

 if(!pitem)
  return false;

 if(!pconnector)
  return false;

 if(!(pitem->Connect(pconnector,item_index,connector_index)))
  return false;

 return true;
}

// ������������� ��� ����� �� ������� 'linkslist'.
bool NANet::CreateLinks(const LinksListT &linkslist)
{
 bool res=true;

 LinksListCIterator K,I,J,endI;
 pair<LinksListCIterator,LinksListCIterator> b;

 NAItem *item;
 NAConnector *connector;
// NameT s1,s2;

 I=linkslist.begin();
 endI=linkslist.end();
 while(I != endI)
  {
   b=linkslist.equal_range(I->first);
   item=dynamic_cast<NAItem*>(GetComponentL(I->first.Id));
   if(!item)
    {
	 res=false;
     I=b.second;
     continue;
    }

   for(K=b.first; K != b.second; ++K)
    {
	 connector=dynamic_cast<NAConnector*>(GetComponentL(K->second.Id));
     if(!connector)
      {
       res=false;
       continue;
      }

	 if(!(item->Connect(connector,I->first.Index,K->second.Index)))
      {
	   res=false;
       continue;
      }
    }
   I=b.second;
  }

 return res;
}

// ��������� ��� ����� � ������� �������� ����, ����
// 'id' - ���� Id �������� ����.
// �����, ���� 'id' - Id ����������, �� ����� ���������
// ����� ����� ����������.
bool NANet::BreakLink(const LinkSideT &id)
{
 NAContainer *pointer=GetComponentL(id.Id);
 NAItem *item;
 NAConnector *connector;

 connector=dynamic_cast<NAConnector*>(pointer);
 if(connector)
  {
   connector->DisconnectAllItems();
   return true;
  }

 item=dynamic_cast<NAItem*>(pointer);
 if(item)
  {
   item->DisconnectAll();
   return true;
  }
 return false;
}

// ��������� ����� ����� ������� �������� ����, 'itemid' 
// � ����������� 'connectorid'
bool NANet::BreakLink(const LinkSideT &itemid, const LinkSideT &connectorid)
{
 NAItem *item=dynamic_cast<NADItem*>(GetComponentL(itemid.Id));
 NAConnector *connector=dynamic_cast<NAConnector*>(GetComponentL(connectorid.Id));

 if(!item)
  return false;
 if(!connector)
  return false;

 item->Disconnect(connector);

 return true;
}

// ��������� ����� ����� ������� �������� ����, 'itemid'
// � ����������� 'connectorid'
bool NANet::BreakLink(const NameT &itemname, int item_index,
						const NameT &connectorname, int connector_index)
{
 NAItem *item=dynamic_cast<NADItem*>(GetComponentL(itemname));
 NAConnector *connector=dynamic_cast<NAConnector*>(GetComponentL(connectorname));

 if(!item)
  return false;
 if(!connector)
  return false;

 item->Disconnect(connector);

 return true;
}

// ��������� ��� ����� ����
// �������� �� ���������� ����� � �������� �����
// brklevel - ������, ������������ �������� ����� ��������� �����������
void NANet::BreakLinks(const NAContainer* brklevel)
{
 for(size_t i=0;i<NumComponents;i++)
  {
   if(dynamic_cast<NADItem*>(PComponents[i]))
	((NAItem*)PComponents[i])->DisconnectBy(brklevel);
   else
   if(dynamic_cast<NANet*>(PComponents[i]))
    ((NANet*)PComponents[i])->BreakLinks(brklevel);
  }
}

// ��������� �������� ����� ����
bool NANet::BreakLinks(const LinksListT &linkslist)
{
 bool res=true;

 LinksListCIterator K,I,J,endI;
 pair<LinksListCIterator,LinksListCIterator> b;

 NAItem *item;
 NAConnector *connector;
// NameT s1,s2;

 I=linkslist.begin();
 endI=linkslist.end();
 while(I != endI)
  {
   b=linkslist.equal_range(I->first);
   item=dynamic_cast<NAItem*>(GetComponentL(I->first.Id));
   if(!item)
    {
	 res=false;
     I=b.second;
     continue;
    }

   for(K=b.first; K != b.second; ++K)
    {
	 connector=dynamic_cast<NAConnector*>(GetComponentL(K->second.Id));
     if(!connector)
      {
	   res=false;
       continue;
      }

	 item->Disconnect(connector);
    }
   I=b.second;
  }

 return res;
}

// ��������� ��� ���������� ����� ����.
void NANet::BreakLinks(void)
{
 for(size_t i=0;i<NumComponents;i++)
  if(dynamic_cast<NANet*>(PComponents[i]))
   ((NANet*)PComponents[i])->BreakLinks();
  else
  {
   if(dynamic_cast<NAItem*>(PComponents[i]))
	((NAItem*)PComponents[i])->DisconnectAll();
   if(dynamic_cast<NAConnector*>(PComponents[i]))
	((NAConnector*)PComponents[i])->DisconnectAllItems();
  }
}
// ----------------------

// --------------------------
// ������� ������ ������� � ���������
// --------------------------
LinksListT& NANet::GetLinks(const NAContainer *cont, LinksListT &linkslist, const NAContainer *netlevel) const
{

 {
  if(dynamic_cast<const NAItem*>(cont))
  {
   static_cast<const NAConnector*>(cont)->GetLinks(linkslist,netlevel);
   static_cast<const NAItem*>(cont)->GetLinks(linkslist,netlevel);
  }
  else
  if(dynamic_cast<const NAConnector*>(cont))
   static_cast<const NAConnector*>(cont)->GetLinks(linkslist,netlevel);
 }

 for(size_t i=0;i<cont->GetNumComponents();i++)
  GetLinks(cont->GetComponentByIndex(i), linkslist, netlevel);

 return linkslist;
}
// --------------------------
       */
}
#endif

