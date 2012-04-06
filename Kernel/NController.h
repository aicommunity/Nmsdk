#ifndef NControllerH
#define NControllerH

#include "rdk.h"

namespace NMSDK {

//class NAContainer;
typedef RDK::UAContainer NAContainer;
typedef RDK::UController NController;

/*
class NController: public RDK::UModule
{
protected: // ���������
// ���� ���������� ���������� ����������
bool Enabled;

protected: // ������
// ��������� �� ����������
std::vector<NAContainer*> Components;

public:
// --------------------------
// ������������ � �����������
// --------------------------
NController(void);
virtual ~NController(void);
// --------------------------

// --------------------------
// ������ ���������� �����������
// --------------------------
// ���� ���������� ���������� ����������
bool IsEnabled(void) const;
bool IsEnabled(bool value);
// --------------------------

// --------------------------
// ������ ���������� �������
// --------------------------
// ���������� ����� ��������� � ������� ��������� ����������
size_t GetNumComponents(void) const;

// ���������� ��������� � �������� ��������� ���������� �� �������
NAContainer* GetComponents(size_t index);

// ���������� ������ ���������� �� ���������
int FindComponent(NAContainer* component) const;
// --------------------------

// --------------------------
// ������ ���������� �����������
// --------------------------
public:
// ��������� ��������� � �����������
virtual bool Link(NAContainer* component, bool forchilds=false);

// ���������� ��������� �� ����������
virtual bool UnLink(int index, bool forchilds=false);
virtual bool UnLink(NAContainer* component, bool forchilds=false);
virtual bool UnLinkAll(bool forchilds=false);

// ��������� ���������
virtual bool Update(void);
// --------------------------

// --------------------------
// ������� ������ ���������� �����������
// --------------------------
protected:
// ��������� ��������� � �����������
virtual bool ALink(NAContainer* component, bool forchilds=false)=0;

// ���������� ��������� �� ����������
virtual bool AUnLink(int index, bool forchilds=false)=0;

// ��������� ���������
virtual bool AUpdate(void)=0;
// --------------------------
};
      */
}

#endif
