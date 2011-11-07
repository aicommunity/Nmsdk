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

#ifndef NSUPPORT_CPP
#define NSUPPORT_CPP

#include "NSupport.h"

namespace NMSDK {


const TimeT DefaultTimeStep=(TimeT)2000;
const NameT ForbiddenName="";
const UId ForbiddenId=0;

// ������
Real RTemp;
NVariableData PTemp;

UId IdTemp;
ULongId LongIdTemp;
NameT NameTemp;

/*
// --------------------------
// ������������ � �����������
// --------------------------
NIOData::NIOData(void)
{
 Void=0;

 // ������ ������ � ������
 Size=ByteSize=0;
 DataSize=sizeof(real);
}

NIOData::NIOData(const NIOData &copy)
{
 Void=0;

 // ������ ������ � ������
 Size=ByteSize=0;
 DataSize=sizeof(int);

 DataSize=copy.DataSize;
 Resize(copy.Size);
 memcpy(Void,copy.Void,copy.ByteSize);
}

NIOData::~NIOData(void)
{
 if(Void)
 {
  delete [] Void;
  Void=0;
 }
}
// --------------------------

// --------------------------
// ������ ������� � ����������
// --------------------------
// ������ ������� ������
size_t NIOData::GetSize(void) const
{
 return Size;
}

// ������ ������ � ������
size_t NIOData::GetByteSize(void) const
{
 return ByteSize;
}

// ������ ���������� ������� � ������
size_t NIOData::GetDataSize(void) const
{
 return DataSize;
}
// --------------------------

// --------------------------
// ������
// --------------------------
// ��������� ������
void NIOData::Resize(size_t size)
{
 if(size == Size)
  return;

 if(!size && Void)
 {
  delete []Void;
  Void=0;
  Size=0;
  return;
 }

 void *tmp=new char[size*DataSize];
 memcpy(tmp,Void,((size<Size)?size:Size)*DataSize);
 delete []Void;
 Size=size;
 ByteSize=Size*DataSize;
 Void=tmp;
}

// ��������� ������ � ���������� �������� ������
void NIOData::Assign(size_t size, char ch)
{
 Resize(size);

 if(ByteSize)
  memset(Void,ch,ByteSize);
}


// ��������� ������ � ���������� �������� �������������������
// ������ ByteSize
void NIOData::Assign(size_t size, const void *data)
{
 Resize(size);

 if(ByteSize)
 {
  char *p=Char;
  for(size_t i=0;i<Size;i++,p+=DataSize)
   memcpy(p,data,DataSize);
 }
}

// ��������� ������ � ���������� �������� �������������������
// ������ size � ���������� ������ datasize
// ������ ������������ ������� � ������� shift
// ���������� ������ ������� datasize*size+shift*datasize*shift
void NIOData::Assign(size_t size, size_t datasize, const void *data, size_t shift)
{
 if(datasize < 1)
  return;

 if(DataSize != datasize || Size != size)
 {
  DataSize=datasize;
  Resize(0);
  Resize(size+shift);
 }

 if(Size)
  memcpy(Char+shift*DataSize,data,size*DataSize);
}

// ���������� �������� �������������������
// � ������������� ��� ������ ��� ��������
// ������ ������������ ������� � ������� shift
void NIOData::Assign(size_t size, const void *data, size_t shift) const
{
 if(Size)
  memcpy(Char+shift*DataSize,data,size*DataSize);
}


// ������������� ������ ���������� ������� � ������
bool NIOData::SetDataSize(size_t size)
{
 if(size < 1)
  return false;

 if(DataSize == size)
  return true;

 DataSize=size;
 Resize(0);
 Resize(Size);
 return true;
}
// --------------------------

// --------------------------
// ���������
// --------------------------
// �������� ������������
NIOData& NIOData::operator = (const NIOData &data)
{
 Resize(0);
 DataSize=data.DataSize;
 Resize(data.Size);
 memcpy(Void,data.Void,data.ByteSize);
 return *this;
}

// �������� ���������� �������
// ������������, ��� ����������� ������ ����� ��� �� ������
// ���������� ���������� ������ ������������ ������� ������
NIOData& NIOData::operator += (const NIOData &data)
{
 if(data.ByteSize == 0)
  return *this;
 size_t shift=ByteSize;
 Resize(Size+data.ByteSize/DataSize);
 memcpy(Char+shift,data.Void,data.ByteSize);

 return *this;
}

/*
// �������� �������
inline char NIOData::operator [] (int i)
{
 return Char[i];
}      */
// --------------------------


/* *************************************************************** */
/*
// --------------------------
// ���������
// --------------------------
bool operator < (const LinkSideT &linkside1, const LinkSideT &linkside2)
{
 return (linkside1.Id<linkside2.Id)
 	|| (linkside1.Id == linkside2.Id && linkside1.Index < linkside2.Index);
}

bool operator == (const LinkSideT &linkside1, const LinkSideT &linkside2)
{
 return (linkside1.Id == linkside2.Id) & (linkside1.Index == linkside2.Index);
}

bool operator != (const LinkSideT &linkside1, const LinkSideT &linkside2)
{
 return (!(linkside1 == linkside2));
}

// --------------------------
       */
/* *************************************************************** */

}

#endif

