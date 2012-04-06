#ifndef NSTORAGE_CPP
#define NSTORAGE_CPP

#include <algorithm>
#include "NStorage.h"

namespace NMSDK{

/* *************************************************************************** */
// Class NStorage
/* *************************************************************************** */
// ������
// --------------------------
// ������������ � �����������
// --------------------------
NStorage::NStorage(void)
{
}

NStorage::~NStorage(void)
{
}
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
RDK::UEPtr<RDK::UAComponent> NStorage::TakeObject(const UId &classid, const UEPtr<UAComponent> prototype)
{
 return RDK::UAContainerStorage::TakeObject(classid,prototype);
}

RDK::UEPtr<RDK::UAComponent> NStorage::TakeObject(const NameT &classname, const UEPtr<UAComponent> prototype)
{
 return RDK::UAContainerStorage::TakeObject(classname,prototype);
}
/* *************************************************************************** */



}
#endif

