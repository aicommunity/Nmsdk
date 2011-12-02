#ifndef NStorageH
#define NStorageH

#include "NBios.h"
#include "rdk.h"

namespace NMSDK{

class NStorage: public RDK::UAContainerStorage
{
private: // ��������� ��������
// ������� ������������ ���� � Id �������� �������
//map<string,IdT> ClassesLookupTable;

protected: // �������� ��������
// ������ ��������� ������� ��������
//ClassesStorageT ClassesStorage;

// ������ ��������
//ObjectsStorageT ObjectsStorage;

// ��������� �������������� Id �������� �������
//IdT LastClassId;

protected: // ��������� ����������
// ������� ���������� �� ��������� ������� �������
//FreeObjectsTableT FreeObjectsTable;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NStorage(void);
virtual ~NStorage(void);
// --------------------------

// --------------------------
// ������ ���������� ����������
// --------------------------
// ���������� ��������� �������������� Id �������
//IdT GetLastClassId(void) const;
// --------------------------

// --------------------------
// ������ ������� � �������� �����������
// --------------------------
// ���������� ��� ������ �� ��� Id
//const string& GetClassName(const UId &id) const;

// ���������� Id ������ �� ��� �����
//const UId& GetClassId(const string &name) const;
// --------------------------

// --------------------------
// ������ ���������� ���������� �������
// --------------------------
// ��������� ������� ������ ������� � ���������
//bool AddClass(const string &classname, RDK::UAComponent *classtemplate);

// ������� ������� ������ ������� �� ���������
// ���������� false ���� classid �� ������,
// ��� ������������ ������� ����� ������
//bool DelClass(const UId &classid);

// ��������� ������� ������� ������ ������� � ���������
//bool CheckClass(const UId &classid) const;

// ���������� ������� ������
//NAContainer* const GetClass(const UId &classid) const;

// ���������� ������ ���� ���� ������� ���������
// ����� 'buffer' ����� ������ �� ���������� ��������
//void GetClassNameList(vector<string> &buffer) const;

// ������� ��� �� ������������ ������� ������� �� ���������
//void FreeClassesStorage(void);

// ������� ��� ������� ������� �� ���������
// ���������� false ���� � ��������� ������������ �������
//bool ClearClassesStorage(void);
// --------------------------

// --------------------------
// ������ ���������� ���������� ��������
// --------------------------
// ��������� ������ �� ���������
// ���������� ��������� �� ��������� ������ �� ����� ������
// ��������� ������ ���������� ��� ������� � ���������
// ���� 'Activity' ������� ������������ � true
// ���� ���������� ������� �� ���������� �� ��������� � �����������
// � ���������
RDK::UEPtr<RDK::UAComponent> TakeObject(const UId &classid, const RDK::UAComponent *prototype=0);
RDK::UEPtr<RDK::UAComponent> TakeObject(const string &classname, const RDK::UAComponent *prototype=0);

// ���������� ������ � ���������
// ��������� ������ ���������� ��� ��������� � ���������
// ���� 'Activity' ������� ������������ � false
// ���� ������ �� ���������� � ��������� - ������������ false
//bool ReturnObject(RDK::UAComponent *object);

// ��������� ��� ��������� ������ � ���������
// ���� ������ ��� ����������� ����� ��������� �� ���������� false
//bool PushObject(const UId &classid, NAContainer *object);

// ������� ��� ��������� ������ �� ��������� � ����������
// ��� classid
// � ������ ������ ���������� ForbiddenId
//UId PopObject(RDK::UAComponent *object);

// ���������� ������ � ������ ���������
//bool MoveObject(NAContainer *object, NStorage *newstorage);

// ��������� ���������� �� ������ 'object' � ���������
//bool CheckObject(const NAContainer *object) const;

// ���������� Id ������, ���������� ������� 'object'
//UId FindClass(const NAContainer *object) const;

// ��������� ��������� ����� �������� � ���������
//size_t CalcNumObjects(void) const;
//size_t CalcNumObjects(const UId &classid) const;
//size_t CalcNumObjects(const string &classname) const;

// �������� ��� ��������� ������� �� ���������
//void FreeObjectsStorage(void);

// ������� ��� ������� �� ���������
//void ClearObjectsStorage(void);
// --------------------------

// --------------------------
// ������� ������ ������� ������������ �������
// --------------------------
protected:
// ��������� ����� � ������ 'name' � ������� ������������
//UId AddLookupClass(const string &name);

// ������� ����� � ������ 'name' �� ������� �����������
//bool DelLookupClass(const string &name);
// --------------------------
};



}

#endif
