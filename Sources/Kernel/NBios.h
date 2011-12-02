// ===========================================================
// Version:        3.0.5
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

#ifndef NBIOS_H
#define NBIOS_H

#include "NSupport.h"
#include "NController.h"
#include "rdk.h"

namespace NMSDK {

//using namespace MySDK;
class NStorage;
/*
class NAContainer: public RDK::UAContainer{};

class NAConnector: public RDK::UAConnector{};

class NAItem: public RDK::UAItem{};

class NADItem: public RDK::UADItem{};

class NANet: public RDK::UANet{};
  */
		  /*
class NANet: public RDK::UANet
{
public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NANet(void);
virtual ~NANet(void);
// --------------------------

// --------------------------
// ������ ���������� ������
// --------------------------
public:
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool Default(void);
// --------------------------
};
          */
/*
class NAContainer: public RDK::UAContainer
{
friend NStorage;
friend NController;

private: // ���������� ��������
// ������� ����� ������ � ��������
static real Time;

private: // ��������� ��������
// ������� ������������ ���� � Id ��������� �������
map<string,UId> CompsLookupTable;

// ������� ������������ ���� � Id ���������� �������
map<string,NVariable> ParamsLookupTable;

// ������� ������������ ���� � Id ������ ��������� �������
map<string,NVariable> StateLookupTable;

// ������� ��������� ���������� �� �������� ����������
map<UId,RDK::UIPointer*> PointerLookupTable;

// ������� ���������
vector<NAContainer*> Components;

// ������� ������������ ����������
vector<NController*> Controllers;

// ������� ������������ <���������� � ������� Components, ��������� ���������>
//map<NAContainer*,NAContainer**> ComponentPointers;

protected: // �������� ��������

public: // ������������� ��������
// ��� ����� � ����� �������
// �������� ��� = 1./TimeStep
RDK::ULProperty<TimeT, NAContainer> TimeStep;

// ���� ���������� �������
// true - ������ ������� ����� �����������
// false - ������ ������� ����� ��������������
RDK::ULProperty<bool, NAContainer>  Activity;

// ��� �������
RDK::ULProperty<NameT, NAContainer> Name;

// ����� ������� � ���������
UVLProperty<UId, NAContainer> Class;

// Id �������
RDK::ULProperty<UId, NAContainer> Id;

public: // ���������� ��������
// ���������� ���������� � ������������ ����
RDK::ULProperty<RDK::MVector<real>, NAContainer> Coord;


protected: // ��������� ����������
// ���� 'TimeStep' > 'Owner->TimeStep' �� 'CalcCounter' ��������
// ��������� �������� ��������� ��������.
// � ��������� ������ 'CalcCounter' �� �����������
TimeT CalcCounter;

// ������ �������� ���� ����� �������������
// ������� ��� �������� ���� ����� ����� �������
// ���� ������������� ������� �� ����������
TimeT OwnerTimeStep;

// ��������� �� 0-� ������� ������� ���������
NAContainer* *PComponents;

// ���������� ��������� � ������� ���������
size_t NumComponents;

// ��������, ����������� �� ���� ������ � ���������
//RDK::InstancesStorageIterator ObjectIterator;

public: // �������� ������
// --------------------------
// ������ ���������� ����������� ����������
// --------------------------
// ���������� ������� ����� ������
static const real& GetTime(void);

// ������������� ������� ����� ������
static bool SetTime(real value);
// --------------------------

// --------------------------
// ������������ � �����������
// --------------------------
NAContainer(void);
//NAContainer(const NameT &name);
virtual ~NAContainer(void);
// --------------------------

// --------------------------
// ������ ������� � ���������
// --------------------------
// ���������, �������� �� ������ owner
// ���������� ����� ������� �� �����-���� ������ ��������
bool CheckOwner(const NAContainer *owner) const;

// ���������� ��������� ��������� ����� �������
//NStorage* const GetStorage(void) const;

// ���������� ������ ��� �������
// (������� ����� ���� ����������)
NameT& GetFullName(NameT &buffer=NameTemp) const;

// ����������  '�������' ��� �������
// (�������� ��� ��������� 'mainowner').
// ����� ���������� ������ ������, ���� 'mainowner' - �� ��������
// ���������� ������� �� �� ����� ������ ��������
NameT& GetLongName(const NAContainer *mainowner, NameT &buffer=NameTemp) const;

// ���������� ������ Id �������
// (������� Id ���� ����������)
ULongId& GetFullId(ULongId &buffer=LongIdTemp) const;

// ����������  '�������' Id �������
// (�������� ��� ��������� 'mainowner')
// ����� ���������� ������ ������, ���� 'mainowner' - �� ��������
// ���������� ������� �� �� ����� ������ ��������
ULongId& GetLongId(const NAContainer *mainowner, ULongId &buffer=LongIdTemp) const;

// ���������� ��������� �������������� Id ���������
//UId GetLastId(void) const;
// --------------------------

// --------------------------
// ������ ���������� ����������
// --------------------------
// ������� ��������� �������
bool BreakOwner(void);

// ��������� ��������������� �� ����� ������� �������� ���������
// 'levels'. ���� levels < 0 �� ��������������� ����������� �� ���� �������
bool SetMainOwner(RDK::UAComponent* const mainowner);
bool SetMainOwner(RDK::UAComponent* const mainowner, int levels);

// ��������� ������������ ��� 'name' �� ������������ � ������ ������� �������
bool CheckName(const NameT &name);

// ��������� ������������ Id 'id' �� ������������ � ������ �������, �������.
bool CheckId(const UId &id);

// ���������� ��� ���������� � ����������� ����� �������
virtual NameT& GenerateName(const NameT &prefix, NameT &namebuffer);

// ���������� ���������� Id
virtual UId GenerateId(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ������������� �������� ���� ��������������
bool SetTimeStep(TimeT timestep);

// ������������� ���� ���������� �������
bool SetActivity(bool activity);

// ������������� ��� �������
bool SetName(const NameT &name);

UId GetClass(void) const;
protected:
bool SetClass(UId value);

public:
// ������������� Id �������
bool SetId(const UId &id);
// --------------------------

public:
// --------------------------
// ������ ������� � �������� �����������
// --------------------------
// ���������� ��� ��������� ���������� �� ��� Id
const NameT& GetComponentName(const UId &id) const;

// ���������� Id ��������� ���������� �� ��� �����
const UId& GetComponentId(const NameT &name) const;

// ���������� ��� ��������� �� ��� Id
const NameT& GetParameterName(const UId &id) const;

// ���������� Id ��������� �� ��� �����
const UId& GetParameterId(const NameT &name) const;

// ���������� ������ ��� ��������� ��� �������� NMSDK, � �������� '*'
NameT GetParameterLongName(const NameT &name) const;
NameT GetParameterLongName(const UId &id) const;

// ���������� ��� ���������� ��������� �� ��� Id
const NameT& GetStateName(const UId &id) const;

// ���������� Id ���������� ��������� �� ��� �����
const UId& GetStateId(const NameT &name) const;

// ���������� ������ ��� ���������� ��������� ��� �������� NMSDK, � �������� '*'
NameT GetStateLongName(const NameT &name) const;
NameT GetStateLongName(const UId &id) const;
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
//virtual NAContainer* New(const NameT &name);
virtual NAContainer* New(void)=0;

// ������� ����� ����� ������� � ����������� ���� ���������
// � �������� ����������.
// ���� 'stor' == 0, �� �������� �������� ��������������
// � ��� �� ��������� ��� ������������� ���� ������
virtual NAContainer* Alloc(const NameT &name, NStorage *stor=0, bool copystate=false);

// �������� ���� ������ � 'target' � ����������� ���� ���������
// � �������� ����������
// ���� 'stor' == 0, �� �������� �������� ��������������
// � ��� �� ��������� ��� ������������� ���� ������
virtual bool Copy(NAContainer *target, NStorage *stor=0, bool copystate=false) const;

// ������������ ������������ ����� ������� � ��� ���������
// ��� ����� �����������, ���� Storage == 0
virtual void Free(void);
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ���������� ����� �������� ���������
size_t GetNumComponents(void) const;

// ���������� ������ ����� �������� ���������
// (������� ��� ���������� �������� ���������)
size_t GetNumAllComponents(void) const;

// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
virtual bool CheckComponentType(UEPtr<NAContainer> comp) const;

// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� ��������� Id 'id'
virtual NAContainer* GetComponent(const UId &id) const;

// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� ��������� ����� 'name'
NAContainer* GetComponent(const NameT &name) const;

// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� �������� Id 'id'
NAContainer* GetComponentL(const ULongId &id) const;

// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� �������� ����� 'name'
NAContainer* GetComponentL(const NameT &name) const;

// ���������� ��������� �� �������� ���������, �������� � ����
// ������� �� ����������� ������ � ������ ���������
// ����� ���������� 0, ���� ������ ������� �� ������� �������
NAContainer* GetComponentByIndex(size_t index) const;

// ��������� �������� ��������� � ���� ������
// ���������� ��� Id ��� ForbiddenId ���� ���������� ��������
// ����� ���� ������� ��������� �� ��������� ����������
virtual UId AddComponent(NAContainer* comp, RDK::UIPointer* pointer=0);

// ������� �������� ��������� �� ����� �������.
// ��������� ��������� ������ ����������� ������ � ���� �������.
// ����� ������� 'id' - ������ ���� �������� Id
// ���������� �������
// ���� 'canfree' == true - ��������������� ������� ������� ������ � ���������
// ��� ������� ���. ����� ������ ����������� � ��������� � ��������� �����
// ���� ��������, ���� ��������� �� �����������
virtual bool DelComponent(const UId &id, bool canfree=true);

// ������� �������� ��������� �� ����� �������.
// ��������� ��������� ������ ����������� ������ � ���� �������.
// ����� ������� 'name' - ������ ���� �������� ������
// ���������� �������
// ���� 'canfree' == true - ��������������� ������� ������� ������ � ���������
// ��� ������� ���. ����� ������ ����������� � ��������� � ��������� �����
// ���� ��������, ���� ��������� �� �����������
bool DelComponent(const NameT &name, bool canfree=true);

// ������������� ������� ��� �������� ����������
void DelAllComponents(void);

// ���������� ������ ���� � Id ���������, ������������ ���������������
// � ���� �������
const map<NameT,UId>& GetComponentsList(void) const;

// �������� ��� ���������� ����� ������� � ������ 'comp', ���� ��������
// ���� ��������� stor != 0 �� ������������ ���
virtual bool CopyComponents(NAContainer* comp, NStorage* stor=0) const;
// --------------------------


// ----------------------
// ������ ���������� ����������������� ������������
// ----------------------
public:
// ���������� ������ ������� ��������������� ���� ����������� ����.
// 'sublevel' ����������� ����� ������� ����������� �������� ��� �������
// ���������� ����� ��������� � ������.
// ���� 'sublevel' == -1, �� ���������� �������������� ���� ����������� �������
// ��� ��������� ����.
// ���� 'sublevel' == 0, �� ���������� �������������� ����������� ������ ���� ����
// ��������������� ������� ������ �� ������������.
virtual RDK::ULongIdVector& GetConnectorsList(RDK::ULongIdVector &buffer,
						  int sublevel=-1, NAContainer *ownerlevel=0);

// ���������� ������ ������� ��������������� ���� ��������� ����.
// 'sublevel' ����������� ����� ������� ����������� �������� ��� �������
// �������� ����� ��������� � ������.
// ���� 'sublevel' == -1, �� ���������� �������������� ���� ��������� �������
// ��� ��������� ����.
// ���� 'sublevel' == 0, �� ���������� �������������� ��������� ������ ���� ����
// ��������������� ������� ������ �� ������������.
virtual RDK::ULongIdVector& GetItemsList(RDK::ULongIdVector &buffer,
							int sublevel=-1, NAContainer *ownerlevel=0);

// ���������� ������ ������� ��������������� ���� �������� ����.
// 'sublevel' ����������� ����� ������� ����������� �������� ��� �������
// ������� ����� ��������� � ������.
// ���� 'sublevel' == -1, �� ���������� �������������� ���� �������� �������
// ��� ��������� ����.
// ���� 'sublevel' == 0, �� ���������� �������������� �������� ������ ���� ����
// ��������������� ������� ������ �� ������������.
virtual RDK::ULongIdVector& GetNetsList(RDK::ULongIdVector &buffer,
							int sublevel=-1, NAContainer *ownerlevel=0);
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
bool Save(RDK::UClassRegistry &buffer);

// ��������� ������ �� ������
// ��� �������� ��������� ������������
// ��������� ����� ������� ��� storage, ���� �� �� 0
// ���� ������� ��������� �� ������, �� �� ������ ������
// ���� ���� paramsonly == true �� ������ ��������� ������ ����������
// ��� ���������� � ���� ��� ��� ������������ �������� ���������
bool Load(RDK::UClassRegistry &buffer, NStorage *storage=0, bool paramsonly=false);

// ��������� ��������� ������� � ������
bool SaveState(RDK::UClassRegistry &buffer);

// ��������� ��������� ������� �� ������
bool LoadState(RDK::UClassRegistry &buffer);
// --------------------------

// --------------------------
// ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool Default(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool Build(void);

// ����� �������� ����� ��� ������ ��������
virtual bool Reset(void);

// ��������� ������ ����� �������
virtual bool Calculate(void);
// --------------------------

// --------------------------
// ������� ������ ���������� ������������� ����������
// �������� ������������ ����� �� ���������� ������
// --------------------------
protected:
// ��������� ����� ����������
bool AddController(NController *controller, bool forchilds=false);

// ������� ���������� �� ������
bool DelController(NController *controller, bool forchilds=false);

// ������� ��� �����������
bool DelAllControllers(bool forchilds=false);

// ���������� ���������� ���� ������������
bool UnLinkAllControllers(bool forchilds=false);

// ���������, ���������� �� ���������� � ������
bool CheckController(NController *controller) const;

// ���������� ����� ������������
bool GetNumControllers(void) const;

// ���������� ���������� �� �������
NController* GetController(int index);
// --------------------------

protected:
// --------------------------
// ������� ������ ���������� ����������
// --------------------------
// ��������� ������� ������������ ��������� ������� 'oldname'
// ��� ���������� �� 'newname'
bool ModifyLookupComponent(const NameT &oldname, const NameT newname);

// ��������� ������� ������������ ��������� ������������ Id 'id'
// ��� ���������� � ������ 'name'
void SetLookupComponent(const NameT &name, const UId &id);

// ��������� ������� ������������ ��������� ������ ������
// ���������� � ������ 'name'
void DelLookupComponent(const NameT &name);
// --------------------------

// --------------------------
// ������� ������ ���������� �����������
// --------------------------
public:
// ��������� �������� � ������ 'name' � ������� �����������
// ���������� � ��������� ��� ���������� ������
// ������ ���������� � ������������� �������
UId AddLookupParameter(const NameT &name,UIProperty &property);

protected:
// ������� �������� � ������ 'name' �� ������� �����������
// ����������
bool DelLookupParameter(const NameT &name);

// ���������� ������ ��� ��������� ��� �������� NMSDK, � �������� '*'
NameT GetParameterLongName(const UIProperty &property) const;
// --------------------------

// --------------------------
// ������� ������ ���������� ����������
// --------------------------
public:
// ��������� ���������� ��������� � ������ 'name' � ������� �����������
// ���������� � ��������� �� ���������� ������
// ������ ���������� � ������������� �������
UId AddLookupState(const NameT &name,UIProperty &property);

protected:
// ������� ���������� ��������� � ������ 'name' �� ������� �����������
bool DelLookupState(const NameT &name);

// ���������� ������ ��� ���������� ��������� ��� �������� NMSDK, � �������� '*'
NameT GetStateLongName(const UIProperty &property) const;
// --------------------------

// --------------------------
// ������� ������ ���������� ���������� �����������
// --------------------------
public:
// ��������� ��������� � ������ 'name' � ������� �����������
// ���������� � ��������� �� ���������� ������
// ������ ���������� � ������������� �������
UId AddLookupPointer(RDK::UIPointer &pointer);

protected:
// ������� ��������� � ID 'id' �� ������� �����������
bool DelLookupPointer(const UId &id);

// ���������� ������ ��� ��������� ��� �������� NMSDK, � �������� '*'
NameT GetPointerLongName(const RDK::UIPointer &property) const;

// ������������ ����� � ������� ���������, ���������������� ��������� ���������
map<UId,RDK::UIPointer*>::const_iterator FindLookupPointer(const NAContainer *source) const;
// --------------------------

// --------------------------
// ������� ������ ���������� �������� ���������
// --------------------------
// ��������� ��������� 'comp' � ������� ���������
void AddComponentTable(NAContainer *comp, RDK::UIPointer* pointer=0);

// ������� ��������� 'comp' �� ������� ���������
void DelComponentTable(NAContainer *comp);
// --------------------------

// --------------------------
// ������� ������ ���������� ������������
// --------------------------
protected:
// ������� ��������� comp
// ����� ������������, ��� ��������� ����������� �������
bool DelComponent(NAContainer* comp, bool canfree);

// ��������� ����������� ���������������� ��������
// ��� ���������� ��������� ���������� � ���� ������
// ����� ����� ������ ������ ���� comp ���
// ������� �������� � ������ ���������
// ����� ���� ������� ��������� �� ��������� ����������
virtual bool AAddComponent(UEPtr<UAContainer> comp, RDK::UIPointer* pointer=0);

// ��������� ��������������� ���������������� ��������
// ��� �������� ��������� ���������� �� ����� �������
// ����� ����� ������ ������ ���� comp
// ���������� � ������ ���������
virtual bool ADelComponent(UEPtr<UAContainer> comp);
// --------------------------
};            */
							   /*
class NAConnector: public NAContainer
{
friend class NAItem;
friend class NADItem;
private: // ��������� ������
// ������ ���������� �� ������������ �������� ����
CItemListT CItemList;

protected: // ������������� ����� ������
// ������ ������������� ������ �� ����� <��� ������, ������ �����>
map<NameT, size_t> InputSymLinks;

public: // ������������� ��������
// ����� ��������� ������
//UVProperty<size_t, NAConnector> NumInputs;
UVLProperty<size_t, NAConnector> NumInputs;

// ������� ���������/���������� ������ ��������������� ���������� ����� ������
// ��� ����������� ������ item.
RDK::ULProperty<bool, NAContainer> AutoNumInputs;
//UProperty<bool, NAConnector> AutoNumInputs;

protected: // ���������� �������� ������� � ������� ������. Read only!
// ����� ������������ ��������� item
size_t NumInputs;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NAConnector(void);
virtual ~NAConnector(void);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ���� ������ � 'target' � ����������� ���� ���������
// � �������� ����������
// ���� 'stor' == 0, �� �������� �������� ��������������
// � ��� �� ��������� ��� ������������� ���� ������
virtual bool Copy(NAContainer *target, NStorage *stor=0, bool copystate=false) const;
// --------------------------

// --------------------------
// ������ ������� � ������
// --------------------------
// ���������� ������������ � ����� ���������� ������ �� �������
CItemT GetCItem(int c_index) const;

// ���������� ���� �������� <�����, ����> ����������� ����� item ��� <-1,-1>
// ���� ����� ����� �����������
pair<int,int> GetCItemIndexes(const NAItem *item) const;
// --------------------------

// --------------------------
// ������ ���������� �������������� ��������
// --------------------------
// ���������� ����� ������������� ������ �� �����
size_t GetNumInputSymLinks(void) const;

// ���������� ������ ����� �� ������������� ������
size_t GetInputSymLink(const string &name) const;

// ��������� ����� ������������� ������ �� ����
// ���������� false ���� ����� ��� ��� ����������
bool AddInputSymLink(const string &name, size_t index);

// ������� ������������� ������ �� ���� �� �����
void DelInputSymLink(const string &name);

// ������� ��� ������������� ������ �� �������� ����
void DelInputSymLink(size_t index);

// ������� ��� ������������� ������
void DelInputSymLinks(void);

// ���������� ������ ���� ������
void GetInputSymLinksList(vector<NameT> &buffer) const;

// �������� ������������� ������ � ������ target
bool CopyInputSymLinks(NAConnector *target) const;
// --------------------------

// ----------------------
// ���������������� ������
// ----------------------
protected:
// ������������� ����� � ��������� ���� 'na' �� ������ �� ������� index.
// ���������� false ���� na ��� ��������� � ����� �����.
// ��� �������� ����������� c_index �������� �������� ������ ������������� �����
virtual bool ConnectToItem(NAItem *na, int i_index, int &c_index);

// ��������� ����� � ��������� ���� 'na'
virtual void DisconnectFromItem(NAItem *na);

// ��������� ����� � ��������� ���� ������������ �� ����� 'index'
virtual void DisconnectFromIndex(int c_index);

// ��������� �������� ����� ��������� ������������ �����
virtual bool AConnectToItem(NAItem *na);

// ��������� �������� ����� ��������� ���������� �����
virtual void ADisconnectFromItem(NAItem *na);

public:
// ��������� ��� ������� �����
virtual void DisconnectAllItems(void);

// ��������� ��� ����� �������
// �������� ��� ���������� ����� � �������� �����
// brklevel - ������, ������������ �������� ����� ��������� �����������
virtual void DisconnectByObject(const NAContainer *brklevel);

public:
// ���������� ���� ��������� (�������� ��������� '���� �������'
// ����� ����������).
virtual void Activate(NAItem *na);

// ���������� ������ �����������
LinksListT& GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const;
// ----------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
protected:
// ���������� ����� ������������ ��������� item
size_t GetNumInputs(void) const;

// ������������� ����� ������������ ��������� item
bool SetNumInputs(size_t value);
// --------------------------

// --------------------------
// ������� ������ ���������� �������������� ��������
// --------------------------
protected:
// ���������� ����� ������������� ������
size_t GetNumSymLinks(const map<NameT, size_t> &symlinks) const;

// ���������� ������ �� ������������� ������
size_t GetSymLink(const string &name, const map<NameT, size_t> &symlinks) const;

// ��������� ����� ������������� ������
// ���������� false ���� ����� ��� ��� ����������
bool AddSymLink(const string &name, size_t index, map<NameT, size_t> &symlinks);

// ������� ������������� ������ �� �����
void DelSymLink(const string &name, map<NameT, size_t> &symlinks);

// ������� ��� ������������� ������ �� �������
void DelSymLink(size_t index, map<NameT, size_t> &symlinks);

// ������� ��� ������������� ������
void DelSymLinks(map<NameT, size_t> &symlinks);

// ���������� ���� ������ ������
void GetSymLinksList(vector<NameT> &buffer, const map<NameT, size_t> &symlinks) const;

// �������� ������������� ������ � ������ target
bool CopySymLinks(NAConnector *target, const map<NameT, size_t> &symlinks) const;
// --------------------------

// --------------------------
// ������ ���������� ������
// --------------------------
public:
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool Default(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool Build(void);
// --------------------------

};

class NAItem: public NAConnector
{
private: // �������� ��������
// ������ ����������� ������������ � ������� ����� �������
vector<vector<NAConnector*> > AssociatedConnectors;

public: // ������������� ��������
// ����� �������
UVLProperty<size_t, NAItem> NumOutputs;
//UVProperty<size_t, NAItem> NumOutputs;


protected: // ��������� ����������. Read Only!
// ��������� �� ������ ������� ������ ������������ �����������
vector<NAConnector**> PAssociatedConnectors;

// ����� ��������� ������ ������������ �����������
vector<size_t> NumAConnectors;

protected: // ���������� �������� ������� � ������� �������. Read only!
// ����� �������
size_t CNumOutputs;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NAItem(void);
virtual ~NAItem(void);
// --------------------------

protected:
// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ���������� ����� ������������ ��������� item
size_t GetNumOutputs(void) const;

// ������������� ����� ������������ ��������� item
bool SetNumOutputs(size_t value);
// --------------------------


public:
// ----------------------
// ���������������� ������
// ----------------------
// ������������� ����� � ����������� 'c'
virtual bool Connect(NAConnector *c, int i_index, int c_index=-1);

// ��������� ����� ������ ����� ������� � ����������� 'c'
virtual void Disconnect(NAConnector *c);

// ���������� ������� ����� ���������� ��� ��������� ������.
size_t GetNumAConnectors(int index) const;

// ��������� ����� ������ ����� ������� � ����������� �� Id 'id'.
virtual bool Disconnect(const UId &id);

// ��������� ����� ������ ����� ������� �� �����
// ������������� ������������.
void DisconnectAll(void);

// ��������� ��� ����� �������
// �������� ��� ���������� ����� � �������� �����
// brklevel - ������, ������������ �������� ����� ��������� �����������
virtual void DisconnectBy(const NAContainer *brklevel);

// ����������������� ��� ����� ����� item �� ����� connectors ������� ��������
// ������ �� ����� item
virtual void BuildLinks(void);

// ���������� ��������� �� ��������� �� ������ �����������
// �� Id 'id'.
const NAConnector* GetAConnector(const UId &id, int index) const;

// ����������  ��������� �� ������ �����������.
const NAConnector* GetAConnectorByIndex(int output, int index) const;

// ���������� ������ �����������
LinksListT& GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const;

// ���������� ������ ����������� ����� ���������� � ���� �������� ���������
// � ��������� ���������� comp � ���� ��� �������� �����������
LinksListT& GetFullItemLinks(LinksListT &linkslist, const NAItem *comp,
							const NAContainer *netlevel) const;
// ----------------------

public:
// --------------------------
// ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool Default(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool Build(void);

// ���������� ��� ����������, ������������ � ������ ����� �������.
virtual void ActivateAll(void);
// --------------------------
};

class NADItem: public NAItem
{
friend class NIOData;
private: // ��������� �������� ������
// ������ �������� ������
vector<NIOData> Output;

private: // ��������� ������� ������
// ������ ���������� �� ������� ������
vector<const NIOData*> Input;

// ������ �������� �������� ������
vector<size_t> InputSize;

public: // ������������� ��������
// ������ �������� ��������
//UVProperty<vector<size_t>, NADItem> OutputSize;
UVLProperty<vector<size_t>, NADItem> OutputSize;

// ������ ���������� ������� ������� ������� � ������
UVLProperty<vector<size_t>, NADItem> DataOutputSize;
//UVProperty<vector<size_t>, NADItem> DataOutputSize;

protected: // ���������� �������� ������� � ������� ������. Read only!
// ��������� �� ������ ������� ������� ���������� �� ������� ������
const NIOData** PInputData;

// ��������� �� ������ ������� ������� �������� �������� ������
size_t* PInputDataSize;

// ������ ������� �������� ������
//size_t NumInputs;

// ��������� ����� ���� ������
size_t FullInputSize;

// ����������� ������ ������� ������
size_t MinInputDataSize;

// ������������ ������ ������� ������
size_t MaxInputSize;

protected: // ���������� �������� ������� � ������� �������. Read only!
// ��������� �� ������ ������� ������� ���������� �� ������� ������
const NIOData* POutputData;


public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NADItem(void);
virtual ~NADItem(void);
// --------------------------

// --------------------------
// ������ ������� � ������
// --------------------------
// ���������� ������ �������� ������
inline const NIOData& GetOutputData(int index) const
{ return POutputData[index]; };

// ���������� ��������� �� ������ ������ Input �� ��������� �� item
// ���������� 0 ���� citem == 0 ��� �� ������ � ������ �����������
const NIOData* GetInputData(NAItem *citem) const;

// ���������� ��������� �� ������ ������ Input �� �������
// �� ��������� ������ �� ������������
const NIOData* GetInputData(size_t index) const;

// ���������� ������ ������� ������ Input �� �������
// �� ��������� ������ �� ������������
size_t GetInputSize(size_t index) const;

// ���������� ��������� ������ ���� �������� ������
size_t GetFullInputSize(void) const;
// --------------------------

// ----------------------
// ������ ���������� ��������� �������
// ----------------------
// ������������� ������ ������� �������� ������
size_t GetOutputDataSize(int index) const;
virtual bool SetOutputDataSize(int index, size_t size, bool nobuild=false);

// ���������� ������ ������� �������� ������ � ������
inline size_t GetByteOutputSize(int index) const
{ return Output[index].ByteSize; };

// ������������� ������ ���������� ������� ������� �������� ������ � ������
size_t GetDataOutputSize(int index) const
{ return Output[index].DataSize; };
bool SetDataOutputSize(int index, size_t size);

// ��������� �������� �������� ������ �������
void FillOutputData(int index, const void *data=0);

// ��������� ��� �������� ������� ��������� �������
void FillOutputData(const void *data=0);
// ----------------------

// ----------------------
// ������ ������� � ��������� ���������
// ----------------------
protected:
// ������ �������� ��������
vector<size_t> GetVOutputSize(void) const;
bool SetVOutputSize(const vector<size_t> value);

// ������ ���������� ������� ������� ������� � ������
vector<size_t> GetVDataOutputSize(void) const;
bool SetVDataOutputSize(const vector<size_t> value);
// ----------------------

// ----------------------
// ���������������� ������
// ----------------------
protected:
// ������������� ����� � ��������� ���� 'na' �� ������ �� ������� index.
// ���������� false ���� na ��� ��������� � ����� �����.
// ��� �������� ����������� c_index �������� �������� ������ ������������� �����
virtual bool ConnectToItem(NAItem *na, int i_index, int &c_index);

// ��������� ����� � ��������� ���� ������������ �� ����� 'index'
virtual void DisconnectFromIndex(int c_index);
// ----------------------

// --------------------------
// ������ ���������� ������
// --------------------------
public:
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool Default(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool Build(void);

// ����� �������� ����� ��� ������ ��������
virtual bool Reset(void);
// --------------------------

// ----------------------
// ��������������� ������
// ----------------------
private:
// ��������� ��������� �� ������� ������ � �������
void UpdatePointers(void);

// ��������� ����������� � ������������ ������ �������� ������
void CalcMinMaxInputsSize(void);
// ----------------------
};


class NANet: public NADItem
{
protected: // �������� ��������

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NANet(void);
virtual ~NANet(void);
// --------------------------

// --------------------------
// ������ ������� � ���������
// --------------------------
LinksListT& GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const;
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ���� ������ � 'target' � ����������� ���� ���������
// � �������� ����������
// ���� 'stor' == 0, �� �������� �������� ��������������
// � ��� �� ��������� ��� ������������� ���� ������
virtual bool Copy(NAContainer *target, NStorage *stor=0, bool copystate=false) const;
// --------------------------

// --------------------------
// ������ ������� � �����������
// --------------------------
// ����� ��������� �� ������������ ������� ������� ����
// � �������� ���������� ������� �������
// ����� ���������� 'true' � ������ ������������
// � 'false' � ������ ������������� ����
virtual bool CheckComponentType(UEPtr<NAContainer> comp) const;
// --------------------------

// --------------------------
// ������� ������ ���������� ������������
// --------------------------
protected:
// ��������� ����������� ���������������� ��������
// ��� ���������� ��������� ���������� � ���� ������
// ����� ����� ������ ������ ���� comp ���
// ������� �������� � ������ ���������
virtual bool AAddComponent(UEPtr<UAContainer> comp, RDK::UIPointer* pointer=0);

// ��������� ��������������� ���������������� ��������
// ��� �������� ��������� ���������� �� ����� �������
// ����� ����� ������ ������ ���� comp
// ���������� � ������ ���������
virtual bool ADelComponent(UEPtr<UAContainer> comp);
// --------------------------

// ----------------------
// ������ ���������� �������
// ----------------------
public:
// ������������� ����� ����� ����� ������� �������� ����
// 'item' � ����������� 'connector'
virtual bool CreateLink(const LinkSideT &itemid, const LinkSideT &connectorid);

// ������������� ����� ����� ����� ������� �������� ����
// 'item' � ����������� 'connector'
virtual bool CreateLink(const NameT &item, int item_index,
						const NameT &connector, int connector_index=-1);

// ������������� ��� ����� �� ������� 'linkslist'
virtual bool CreateLinks(const LinksListT &linkslist);

// ��������� ��� ����� � ������� �������� ����, ����
// 'id' - ���� Id �������� ����.
// �����, ���� 'id' - Id ����������, �� ����� ���������
// ����� ����� ����������
virtual bool BreakLink(const LinkSideT &id);

// ��������� ����� ����� ������� �������� ����, 'itemid'
// � ����������� 'connectorid'
virtual bool BreakLink(const LinkSideT &itemid, const LinkSideT &connectorid);

// ��������� ����� ����� ������� �������� ����, 'itemid'
// � ����������� 'connectorid'
virtual bool BreakLink(const NameT &itemname, int item_index,
						const NameT &connectorname, int connector_index);

// ��������� ��� ����� ����
// �������� �� ���������� ����� � �������� �����
// brklevel - ������, ������������ �������� ����� ��������� �����������
virtual void BreakLinks(const NAContainer* brklevel);

// ��������� �������� ����� ����
virtual bool BreakLinks(const LinksListT &linkslist);

// ��������� ��� ���������� ����� ����.
virtual void BreakLinks(void);
// ----------------------

// --------------------------
// ������� ������ ������� � ���������
// --------------------------
protected:
LinksListT& GetLinks(const NAContainer *cont, LinksListT &linkslist, const NAContainer *netlevel) const;
// --------------------------


};
*/
}
#endif

