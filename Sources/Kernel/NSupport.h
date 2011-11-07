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

// Отключение предупреждений в VS
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
// Конструкторы и деструкторы
// --------------------------
//Конструктор инициализации
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
// Конструкторы и деструкторы
// --------------------------
//Конструктор инициализации.
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
// Данные
class NIOData
{
friend class NADItem;
public: // Данные
// Указатель на данные
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

protected: // Параметры
// Размер вектора данных
size_t Size;

// Размер данных в байтах
size_t ByteSize;

// Размер единичного данного в байтах
size_t DataSize;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NIOData(void);
NIOData(const NIOData &copy);
~NIOData(void);
// --------------------------

// --------------------------
// Методы доступа к параметрам
// --------------------------
// Размер вектора данных
size_t GetSize(void) const;

// Размер данных в байтах
size_t GetByteSize(void) const;

// Размер единичного данного в байтах
size_t GetDataSize(void) const;
// --------------------------

// --------------------------
// Методы
// --------------------------
// Выделение памяти
void Resize(size_t size);

// Выделение памяти и заполнение заданным байтом
void Assign(size_t size, char ch);

// Выделение памяти и заполнение заданной последовательностью
// длиной ByteSize
void Assign(size_t size, const void *data);

// Выделение памяти и заполнение заданной последовательностью
// длиной size с элементами длиной datasize
// Массив записывается начиная с индекса shift
// Выделяется память разером datasize*size+shift*datasize*shift
void Assign(size_t size, size_t datasize, const void *data, size_t shift=0);

// Заполнение заданной последовательностью
// в предположении что память уже выделена
// Массив записывается начиная с индекса shift
void Assign(size_t size, const void *data, size_t shift=0) const;

// Устанавливает размер единичного данного в байтах
bool SetDataSize(size_t size);
// --------------------------

// --------------------------
// Операторы
// --------------------------
// Оператор присваивания
NIOData& operator = (const NIOData &data);

// Оператор расширения массива
// Предполагает, что добавляемый массив имеет тот же формат
// Добавление происходит прямым копированием области памяти
NIOData& operator += (const NIOData &data);

// Оператор доступа
//inline char operator [] (int i);
// --------------------------
};
		 */

//typedef string ParamT;
typedef RDK::UVariableData NVariableData;
/*
// Описание одной из сторон связи между объектами
struct LinkSideT
{
// Id объекта
ULongId Id;

// Индекс связываемого входа/выхода
int Index;

// --------------------------
// Операторы
// --------------------------
friend bool operator < (const LinkSideT &linkside1, const LinkSideT &linkside2);
friend bool operator == (const LinkSideT &linkside1, const LinkSideT &linkside2);
friend bool operator != (const LinkSideT &linkside1, const LinkSideT &linkside2);
// --------------------------
};

// Описание одиночной связи
typedef pair<LinkSideT,LinkSideT> LinkT;

typedef multimap<LinkSideT,LinkSideT> LinksListT;
typedef multimap<LinkSideT,LinkSideT>::iterator LinksListIterator;
typedef multimap<LinkSideT,LinkSideT>::const_iterator LinksListCIterator;
*/
/*
// Хранилище образцов классов
typedef    map<UId, NAContainer*> ClassesStorageT;
typedef    map<UId, NAContainer*>::iterator ClassesStorageIterator;
typedef    map<UId, NAContainer*>::const_iterator ClassesStorageCIterator;

// Список существующих объектов определенного класса с флагом использования
// <экземпляр объекта, флаг true если занят или false если свободен>
typedef map<NAContainer*, bool> InstancesStorageT;
typedef map<NAContainer*, bool>::iterator InstancesStorageIterator;
typedef map<NAContainer*, bool>::const_iterator InstancesStorageCIterator;

// Хранилище объектов разбитое на группы по Id классов
typedef map<UId, InstancesStorageT> ObjectsStorageT;
typedef map<UId, InstancesStorageT>::iterator ObjectsStorageIterator;
typedef map<UId, InstancesStorageT>::const_iterator ObjectsStorageCIterator;
                             */
// Хранилище итераторов на свободные объекты заданных классов
//typedef map<UId, vector<RDK::InstancesStorageIterator> > FreeObjectsTableT;
//typedef map<UId, vector<RDK::InstancesStorageIterator> >::iterator FreeObjectsTableIterator;
//typedef map<UId, vector<RDK::InstancesStorageIterator> >::const_iterator FreeObjectsTableCIterator;


// Пара описывающая массив
typedef pair<real*,size_t> ArrayT;

// Пара описывающая константный массив
typedef pair<const real*,size_t> CArrayT;

// Описание одного объекта подключенного к заданному коннектору
/*struct CItemT
{
 // Указатель на объект
 NAItem* Item;

 // Индекс выхода объекта
 int Index;
};

// Хранилище объектов подключенных к заданному коннектору
typedef vector<CItemT> CItemListT;
typedef vector<CItemT>::iterator CItemListTIterator;
typedef vector<CItemT>::const_iterator CItemListTCIterator;

// Хранилище свойств параметра
struct NVariable
{
 // Id параметра
 UId Id;

 // Указатель на свойство
 UIProperty* Property;
};

// Хранилище свойств указателя
struct NPVariable
{
 // Id указателя
 UId Id;

 // Указатель на свойство
 RDK::UIPointer* Pointer;
};
                   */
// Константы
extern const TimeT DefaultTimeStep;
extern const NameT ForbiddenName;
extern const UId ForbiddenId;

// Буферы
extern Real RTemp;
extern NVariableData PTemp;

extern UId IdTemp;
extern ULongId LongIdTemp;
extern NameT NameTemp;

}

#endif

