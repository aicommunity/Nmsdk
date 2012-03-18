#ifndef NStorageH
#define NStorageH

#include "NBios.h"
#include "rdk.h"

namespace NMSDK{

class NStorage: public RDK::UAContainerStorage
{
private: // ��������� ��������

protected: // �������� ��������

protected: // ��������� ����������

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NStorage(void);
virtual ~NStorage(void);
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
RDK::UEPtr<RDK::UAComponent> TakeObject(const UId &classid, const UEPtr<UAComponent> prototype=0);
RDK::UEPtr<RDK::UAComponent> TakeObject(const string &classname, const UEPtr<UAComponent> prototype=0);

};



}

#endif
