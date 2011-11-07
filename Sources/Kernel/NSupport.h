// ===========================================================
// Version:        3.0.3
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

#ifndef NSUPPORT_H
#define NSUPPORT_H

// ���������� �������������� � VS
#pragma warning( disable : 4355)
#pragma warning( disable : 4800)

//#pragma warning( disable: 4786 )

#include <list>
#include <string>
#include <map>
#include <vector>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cstring>
#include <functional>
#include "rdk.h"
//#include "RDK::ULProperty.h"
//#include "NPointer.h"

namespace NMSDK {

using namespace std;
//using namespace RDK;
using RDK::UId;
using RDK::ULongId;
using RDK::NameT;

//class NAContainer;
//class NAConnector;
//class NANet;
//class NAItem;
typedef RDK::UAContainer NAContainer;

typedef RDK::UAConnector NAConnector;

typedef RDK::UAItem NAItem;

typedef RDK::UADItem NADItem;

typedef RDK::UANet NANet;

         /*
template<typename T, typename OwnerT>
class RDK::ULProperty: public RDK::ULocalProperty<T,OwnerT>
{
public:
public:
// --------------------------
// ������������ � �����������
// --------------------------
//����������� �������������
RDK::ULProperty(const string &name, OwnerT * const owner, RDK::UVProperty<T,OwnerT>::SetterT setmethod=0)
 : ULocalProperty<T,OwnerT>(name, owner, setmethod)
{  };

RDK::ULProperty(const string &name, OwnerT * const owner, RDK::UVProperty<T,OwnerT>::SetterRT setmethod)
 : ULocalProperty<T,OwnerT>(name, owner, setmethod)
{  };
// -----------------------------
};

template<typename TC, typename OwnerT>
class RDK::UCLProperty: public RDK::UCLocalProperty<TC,OwnerT>{};

template<typename T, typename OwnerT>
class UVLProperty: public RDK::UVLocalProperty<T,OwnerT>
{
public:
// --------------------------
// ������������ � �����������
// --------------------------
//����������� �������������.
UVLProperty(const string &name, OwnerT * const owner, RDK::UVProperty<T,OwnerT>::SetterT setmethod ,
								RDK::UVProperty<T,OwnerT>::GetterT getmethod)
 : UVLocalProperty<T,OwnerT>(name, owner, setmethod, getmethod) {  };
UVLProperty(const string &name, OwnerT * const owner, RDK::UVProperty<T,OwnerT>::SetterRT setmethod ,
	RDK::UVProperty<T,OwnerT>::GetterT getmethod)
 : UVLocalProperty<T,OwnerT>(name, owner, setmethod, getmethod)
{  };
// -----------------------------

};

template<typename T, typename OwnerT>
class RDK::ULStateProperty: public RDK::ULocalStateProperty<T,OwnerT>{};

template<typename TC, typename OwnerT>
class RDK::UCLStateProperty: public RDK::UCLocalStateProperty<TC,OwnerT>{};
       */
typedef double real;
typedef vector<real> Real;
typedef vector<real>::iterator RealIterator;
typedef vector<real>::const_iterator RealCIterator;

//typedef unsigned long int SizeT;
typedef long int IndexT;
typedef int TimeT;
//typedef std::string NameT;
//typedef char BoolT;
/*
// ������
class NIOData
{
friend class NADItem;
public: // ������
// ��������� �� ������
union
{
  void *Void;
  char *Char;
  unsigned char *UChar;
  short *Short;
  unsigned short *UShort;
  int *Int;
  unsigned int *UInt;
  long long *Long;
  unsigned long long *ULong;
  float *Float;
  double *Double;
  long double *LDouble;
  real *Real;
};

protected: // ���������
// ������ ������� ������
size_t Size;

// ������ ������ � ������
size_t ByteSize;

// ������ ���������� ������� � ������
size_t DataSize;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NIOData(void);
NIOData(const NIOData &copy);
~NIOData(void);
// --------------------------

// --------------------------
// ������ ������� � ����������
// --------------------------
// ������ ������� ������
size_t GetSize(void) const;

// ������ ������ � ������
size_t GetByteSize(void) const;

// ������ ���������� ������� � ������
size_t GetDataSize(void) const;
// --------------------------

// --------------------------
// ������
// --------------------------
// ��������� ������
void Resize(size_t size);

// ��������� ������ � ���������� �������� ������
void Assign(size_t size, char ch);

// ��������� ������ � ���������� �������� �������������������
// ������ ByteSize
void Assign(size_t size, const void *data);

// ��������� ������ � ���������� �������� �������������������
// ������ size � ���������� ������ datasize
// ������ ������������ ������� � ������� shift
// ���������� ������ ������� datasize*size+shift*datasize*shift
void Assign(size_t size, size_t datasize, const void *data, size_t shift=0);

// ���������� �������� �������������������
// � ������������� ��� ������ ��� ��������
// ������ ������������ ������� � ������� shift
void Assign(size_t size, const void *data, size_t shift=0) const;

// ������������� ������ ���������� ������� � ������
bool SetDataSize(size_t size);
// --------------------------

// --------------------------
// ���������
// --------------------------
// �������� ������������
NIOData& operator = (const NIOData &data);

// �������� ���������� �������
// ������������, ��� ����������� ������ ����� ��� �� ������
// ���������� ���������� ������ ������������ ������� ������
NIOData& operator += (const NIOData &data);

// �������� �������
//inline char operator [] (int i);
// --------------------------
};
		 */

//typedef string ParamT;
typedef RDK::UVariableData NVariableData;
/*
// �������� ����� �� ������ ����� ����� ���������
struct LinkSideT
{
// Id �������
ULongId Id;

// ������ ������������ �����/������
int Index;

// --------------------------
// ���������
// --------------------------
friend bool operator < (const LinkSideT &linkside1, const LinkSideT &linkside2);
friend bool operator == (const LinkSideT &linkside1, const LinkSideT &linkside2);
friend bool operator != (const LinkSideT &linkside1, const LinkSideT &linkside2);
// --------------------------
};

// �������� ��������� �����
typedef pair<LinkSideT,LinkSideT> LinkT;

typedef multimap<LinkSideT,LinkSideT> LinksListT;
typedef multimap<LinkSideT,LinkSideT>::iterator LinksListIterator;
typedef multimap<LinkSideT,LinkSideT>::const_iterator LinksListCIterator;
*/
/*
// ��������� �������� �������
typedef    map<UId, NAContainer*> ClassesStorageT;
typedef    map<UId, NAContainer*>::iterator ClassesStorageIterator;
typedef    map<UId, NAContainer*>::const_iterator ClassesStorageCIterator;

// ������ ������������ �������� ������������� ������ � ������ �������������
// <��������� �������, ���� true ���� ����� ��� false ���� ��������>
typedef map<NAContainer*, bool> InstancesStorageT;
typedef map<NAContainer*, bool>::iterator InstancesStorageIterator;
typedef map<NAContainer*, bool>::const_iterator InstancesStorageCIterator;

// ��������� �������� �������� �� ������ �� Id �������
typedef map<UId, InstancesStorageT> ObjectsStorageT;
typedef map<UId, InstancesStorageT>::iterator ObjectsStorageIterator;
typedef map<UId, InstancesStorageT>::const_iterator ObjectsStorageCIterator;
                             */
// ��������� ���������� �� ��������� ������� �������� �������
//typedef map<UId, vector<RDK::InstancesStorageIterator> > FreeObjectsTableT;
//typedef map<UId, vector<RDK::InstancesStorageIterator> >::iterator FreeObjectsTableIterator;
//typedef map<UId, vector<RDK::InstancesStorageIterator> >::const_iterator FreeObjectsTableCIterator;


// ���� ����������� ������
typedef pair<real*,size_t> ArrayT;

// ���� ����������� ����������� ������
typedef pair<const real*,size_t> CArrayT;

// �������� ������ ������� ������������� � ��������� ����������
/*struct CItemT
{
 // ��������� �� ������
 NAItem* Item;

 // ������ ������ �������
 int Index;
};

// ��������� �������� ������������ � ��������� ����������
typedef vector<CItemT> CItemListT;
typedef vector<CItemT>::iterator CItemListTIterator;
typedef vector<CItemT>::const_iterator CItemListTCIterator;

// ��������� ������� ���������
struct NVariable
{
 // Id ���������
 UId Id;

 // ��������� �� ��������
 UIProperty* Property;
};

// ��������� ������� ���������
struct NPVariable
{
 // Id ���������
 UId Id;

 // ��������� �� ��������
 RDK::UIPointer* Pointer;
};
                   */
// ���������
extern const TimeT DefaultTimeStep;
extern const NameT ForbiddenName;
extern const UId ForbiddenId;

// ������
extern Real RTemp;
extern NVariableData PTemp;

extern UId IdTemp;
extern ULongId LongIdTemp;
extern NameT NameTemp;

}

#endif

