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
// Конструкторы и деструкторы
// --------------------------
NANet::NANet(void)
{
}

NANet::~NANet(void)
{
}
// --------------------------

// --------------------------
// Методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
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
// Глобальные свойства
// --------------------------
// Текущее время модели в секундах
real NAContainer::Time=0;
// --------------------------

// --------------------------
// Методы управления глобальными свойствами
// --------------------------
// Возвращает текущее время модели
const real& NAContainer::GetTime(void)
{
 return Time;
}

// Устанавливает текущее время модели
bool NAContainer::SetTime(real value)
{
 if(Time == value)
  return true;

 Time=value;
 return true;
}
// --------------------------

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NAContainer::NAContainer(void)
 : TimeStep("TimeStep",this,&NAContainer::SetTimeStep),
   Activity("Activity",this,&NAContainer::SetActivity),
   Name("Name",this,&NAContainer::SetName),
   Class("Class",this,&NAContainer::SetClass,&NAContainer::GetClass),
   Id("Id",this,&NAContainer::SetId),
   Coord("Coord",this)
{
 // Указатель на 0-й элемент вектора компонент
 PComponents=0;

 // Количество компонент в векторе компонент
 NumComponents=0;

 CalcCounter=0;

 TimeStep=OwnerTimeStep=DefaultTimeStep;
}


NAContainer::~NAContainer(void)
{
 DelAllComponents();
 UnLinkAllControllers();

 if(!BreakOwner())
  return;// Заглушка! Неустранимая ошибка, требуется исключение

 if(Storage)
  {
   dynamic_cast<NStorage*>(Storage)->PopObject(this);
  }
}
// --------------------------

// --------------------------
// Методы доступа к свойствам
// --------------------------
// Проверяет, является ли объект owner
// владельцем этого объекта на каком-либо уровне иерархии
bool NAContainer::CheckOwner(const NAContainer *owner) const
{
 if(Owner == 0 && Owner != owner)
  return false;

 if(Owner == owner)
  return true;

 return static_cast<NAContainer*>(Owner)->CheckOwner(owner);
}

// Возвращает полное имя объекта
// (включая имена всех владельцев).
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

// Возвращает  'длинное' имени объекта
// (исключая имя владельца 'mainowner').
// Метод возвращает пустую строку, если 'mainowner' - не является
// владельцем объекта ни на каком уровне иерархии.
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

// Возвращает полный Id объекта
// (включая Id всех владельцев).
ULongId& NAContainer::GetFullId(ULongId &buffer) const
{
 return RDK::UAContainer::GetFullId(buffer);
}

// Возвращает  'длинный' Id объекта
// (исключая имя владельца 'mainowner').
// Метод возвращает пустой вектор, если 'mainowner' - не является
// владельцем объекта ни на каком уровне иерархии.
ULongId& NAContainer::GetLongId(const NAContainer *mainowner, ULongId &buffer) const
{
 return RDK::UAContainer::GetLongId(mainowner,buffer);
}
// --------------------------

// --------------------------
// Методы управления свойствами
// --------------------------
// Удаляет владельца объекта
bool NAContainer::BreakOwner(void)
{
 if(Owner)
  return static_cast<NAContainer*>(Owner)->DelComponent(this,false);

 return true;
}

// Устанавливает указатель на главного владельца этим объектом
// Указатель устанавливается на число уровней дочерних компонент
// 'levels'. Если levels < 0 то устанавливается компонентам на всех уровнях
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
  // Устанавливаем главного владельца только тем дочерним компонентам
  // у которых он еще не задан
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

// Проверяет предлагаемое имя 'name' на уникальность в рамках
// данного объекта.
bool NAContainer::CheckName(const NameT &name)
{
// if(!Owner)
//  return true;

 if(CompsLookupTable.find(name) == CompsLookupTable.end())
  return true;

 return false;
}

// Проверяет предлагаемый Id 'id' на уникальность в рамках данного, объекта.
bool NAContainer::CheckId(const UId &id)
{
 return (id>LastId)?true:false;
}

#pragma warning (disable : 4996)
// Генерирует имя уникальное в компонентах этого объекта
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

   if(k == 0) // Заглушка!! Должно быть исключение - ресурсы исчерпаны
    return namebuffer;
  }

 return namebuffer;
}
#pragma warning (default : 4996)


// Генерирует уникальный Id.
UId NAContainer::GenerateId(void)
{
 return LastId+1;
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает величину шага интегрирования
bool NAContainer::SetTimeStep(TimeT timestep)
{
 if(timestep <= 0)
  return false;

 if(Owner)
  OwnerTimeStep=static_cast<NAContainer*>(Owner)->TimeStep();
 else
  OwnerTimeStep=timestep;

 // Обращение ко всем компонентам объекта
 for(size_t i=0;i<NumComponents;i++)
  PComponents[i]->OwnerTimeStep=timestep;

 return true;
}

// Устанавливает флаг активности объекта
bool NAContainer::SetActivity(bool activity)
{
 for(size_t i=0;i<NumComponents;i++)
  PComponents[i]->Activity=activity;

 if(activity)
  return Reset();

 return true;
}

// Устанавливает имя объекта.
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

// Устанавливает Id объекта.
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
// Методы доступа к таблицам соотвествий
// --------------------------
// Возвращает имя дочернего компонента по его Id
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

// Возвращает Id дочернего компонента по его имени
const UId& NAContainer::GetComponentId(const NameT &name) const
{
 map<NameT,UId>::const_iterator I=CompsLookupTable.find(name);
 if(I == CompsLookupTable.end())
  return ForbiddenId;
 else return I->second;
}

// Возвращает имя параметра по его Id
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

// Возвращает Id параметра по его имени
const UId& NAContainer::GetParameterId(const NameT &name) const
{
 map<NameT,NVariable>::const_iterator I=ParamsLookupTable.find(name);
 if(I == ParamsLookupTable.end())
  return ForbiddenId;
 else return I->second.Id;
}

// Возвращает полное имя параметра без префикса NMSDK, и суффикса '*'
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

// Возвращает имя переменной состояния по его Id
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

// Возвращает Id переменной состояния по его имени
const UId& NAContainer::GetStateId(const NameT &name) const
{
 map<NameT,NVariable>::const_iterator I=StateLookupTable.find(name);
 if(I == StateLookupTable.end())
  return ForbiddenId;
 else return I->second.Id;
}

// Возвращает полное имя переменной состояния без префикса NMSDK, и суффикса '*'
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
// Системные методы управления объектом
// --------------------------
// Создает копию этого объекта с сохранением всех компонент
// и значений параметров.
// Если 'stor' == 0, то создание объектов осуществляется
// в том же хранилище где располагается этот объект
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

// Копирует этот объект в 'target' с сохранением всех компонент
// и значений параметров
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

// Осуществляет освобождение этого объекта в его хранилище
// или вызов деструктора, если Storage == 0
void NAContainer::Free(void)
{
 if(Storage)
 {
  if(!BreakOwner())
   throw; // Заглушка, здесь должно быть исключение!!
  Storage->ReturnObject(this);
 }
 else
  delete this;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Возвращает число дочерних компонент
size_t NAContainer::GetNumComponents(void) const
{
 return NumComponents;
}


// Возвращает полное число дочерних компонент
// (включая все компоненты дочерних компонент)
size_t NAContainer::GetNumAllComponents(void) const
{
 size_t res=NumComponents;

 for(size_t i=0;i<NumComponents;i++)
  res+=PComponents[i]->GetNumAllComponents();

 return res;
}


// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NAContainer::CheckComponentType(UEPtr<NAContainer> comp) const
{
 return false;
}

// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по короткому Id 'id'
NAContainer* NAContainer::GetComponent(const UId &id) const
{
 if(id == ForbiddenId)
  return 0;

 for(size_t i=0;i<NumComponents;i++)
  if(id == PComponents[i]->Id())
   return PComponents[i];

 return 0;
}

// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по короткому имени 'name'.
NAContainer* NAContainer::GetComponent(const NameT &name) const
{
 return GetComponent(GetComponentId(name));
}


// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по ДЛИННОМУ Id 'id'.
NAContainer* NAContainer::GetComponentL(const ULongId &id) const
{
 return dynamic_cast<NAContainer*>(RDK::UAContainer::GetComponentL(id));
}

// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по ДЛИННОМУ имени 'name'.
NAContainer* NAContainer::GetComponentL(const NameT &name) const
{
 return dynamic_cast<NAContainer*>(RDK::UAContainer::GetComponentL(name));
}

// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по порядковому индеку в списке компонент
// Метод возвращает 0, если индекс выходит за границы массива
NAContainer* NAContainer::GetComponentByIndex(size_t index) const
{
 if(index >= NumComponents)
  return 0;

 return PComponents[index];
}

// Добавляет дочерний компонент в этот объект
// Возвращает его Id или ForbiddenId если добавление неудачно
// Может быть передан указатель на локальную переменную
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
 // Добавляем компонент в таблицу соответствий владельца
 SetLookupComponent(comp->Name(), comp->Id());

 // Добавление в базу компонент
 AddComponentTable(comp,pointer);

 comp->OwnerTimeStep=TimeStep();

 if(MainOwner)
  comp->SetMainOwner(MainOwner);

 if(!AAddComponent(comp,pointer))
  {
   // Откат
   // Удаляем компонент из таблицы соответствий владельца
   DelLookupComponent(comp->Name());

   // Удаление из базы компонент
   DelComponentTable(comp);

   comp->Owner=0;

   return ForbiddenId;
  }

 return comp->Id();
}

// Удаляет дочерний компонент из этого объекта.
// Удаляемый компонент должен содержаться именно в этом объекте.
// Таким образом 'id' - должно быть коротким Id
// удаляемого объекта
// Если 'canfree' == true - предпринимается попытка вернуть объект в хранилище
// или удалить его. Иначе объект сохраняется в хранилище в состоянии занят
// либо повисает, если хранилище не установлено
bool NAContainer::DelComponent(const UId &id, bool canfree)
{
 NAContainer *comp=GetComponent(id);

 if(!comp)
  return false;

 return DelComponent(comp, canfree);
}

// Удаляет дочерний компонент из этого объекта.
// Удаляемый компонент должен содержаться именно в этом объекте.
// Таким образом 'name' - должно быть коротким именем
// удаляемого объекта.
// Если 'canfree' == true - предпринимается попытка вернуть объект в хранилище
// или удалить его. Иначе объект сохраняется в хранилище в состоянии занят
// либо повисает, если хранилище не установлено
bool NAContainer::DelComponent(const NameT &name, bool canfree)
{
 return DelComponent(GetComponentId(name),canfree);
}

// Принудительно удаляет все дочерние компоненты
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


// Возвращает список имен и Id компонент, содержащихся непосредственно
// в этом объекте
const map<NameT,UId>& NAContainer::GetComponentsList(void) const
{ 
 return CompsLookupTable; 
}

// Копирует все компоненты этого объекта в объект 'comp', если возможно.
bool NAContainer::CopyComponents(NAContainer* comp, NStorage* stor) const
{
 NAContainer* bufcomp;

 if(!comp)
  return false;

 // Удаляем лишние компоненты из 'comp'
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
// Методы управления коммуникационными компонентами
// ----------------------
// Возвращает список длинных идентификаторов всех коннекторов сети.
// 'sublevel' опеределяет число уровней вложенности подсетей для которых
// коннекторы будут добавлены в список.
// если 'sublevel' == -1, то возвращает идентификаторы всех коннекторов включая
// все вложенные сети.
// если 'sublevel' == 0, то возвращает идентификаторы коннекторов только этой сети
// Предварительная очистка буфера не производится.
RDK::ULongIdVector& NAContainer::GetConnectorsList(RDK::ULongIdVector &buffer,
							int sublevel, NAContainer *ownerlevel)
{
 return RDK::UAContainer::GetConnectorsList(buffer,
							sublevel, ownerlevel);
}

// Возвращает список длинных идентификаторов всех элементов сети.
// 'sublevel' опеределяет число уровней вложенности подсетей для которых
// элементы будут добавлены в список.
// если 'sublevel' == -1, то возвращает идентификаторы всех элементов включая
// все вложенные сети.
// если 'sublevel' == 0, то возвращает идентификаторы элементов только этой сети
// Предварительная очистка буфера не производится.
RDK::ULongIdVector& NAContainer::GetItemsList(RDK::ULongIdVector &buffer,
							int sublevel, NAContainer *ownerlevel)
{
 return RDK::UAContainer::GetItemsList(buffer,
							sublevel, ownerlevel);
}

// Возвращает список длинных идентификаторов всех подсетей сети.
// 'sublevel' опеределяет число уровней вложенности подсетей для которых
// подсети будут добавлены в список.
// если 'sublevel' == -1, то возвращает идентификаторы всех подсетей включая
// все вложенные сети.
// если 'sublevel' == 0, то возвращает идентификаторы подсетей только этой сети
RDK::ULongIdVector& NAContainer::GetNetsList(RDK::ULongIdVector &buffer,
							int sublevel, NAContainer *ownerlevel)
{
 return RDK::UAContainer::GetNetsList(buffer,
							sublevel, ownerlevel);
}
// ----------------------

// --------------------------
// Методы доступа к параметрам
// --------------------------
// --------------------------

// --------------------------
// Методы доступа к переменным состояния
// --------------------------

// --------------------------

// --------------------------
// Методы управления текущим состоянием
// --------------------------
// Сохраняет объект в дерево
bool NAContainer::Save(RDK::UClassRegistry &buffer)
{
 return true;
}

// Загружает объект из дерева
// Для создания компонент используется
// хранилище этого объекта или storage, если он не 0
// Если никакое хранилище не задано, то не делает ничего
bool NAContainer::Load(RDK::UClassRegistry &buffer, NStorage *storage, bool paramsonly)
{
 // Текущая версия грузит только параметры

 return true;
}

// Сохраняет состояние объекта в дерево
bool NAContainer::SaveState(RDK::UClassRegistry &buffer)
{

 return true;
}

// Загружает состояние объекта из дерева
// Если какие-то из дочерних компонент не созданы, то их состояние не восстанавливается
// однако метод возвращает true.
// Если для каких-то дочерних компонент данные состояния отсутствуют, то
// метод возвращает false
bool NAContainer::LoadState(RDK::UClassRegistry &buffer)
{

 return true;
}
// --------------------------

// --------------------------
// Методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NAContainer::Default(void)
{
 Ready=false;
 for(size_t i=0;i<NumComponents;i++)
  if(!PComponents[i]->Default())
   return false;

 // Если существует прообраз в хранилище, то берем настройки параметров
 // из прообраза
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

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
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

// Сброс процесса счета.
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

// Выполняет расчет этого объекта 
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

 // Обрабатываем контроллеры
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
// Методы управления контроллерами интерфейса
// Удаление контроллеров лежит на вызывающем модуле
// --------------------------
// Добавляет новый контроллер
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

// Удаляет контроллер из списка
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

// Удаляет все контроллеры
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

// Инициирует отключение всех контроллеров
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


// Проверяет, существует ли контроллер в списке
bool NAContainer::CheckController(NController *controller) const
{
 if(find(Controllers.begin(),Controllers.end(),controller) != Controllers.end())
  return true;
 return false;
}

// Возвращает число контроллеров
bool NAContainer::GetNumControllers(void) const
{
 return Controllers.size();
}

// Возвращает контроллер по индексу
NController* NAContainer::GetController(int index)
{
 return Controllers[index];
}
// --------------------------

// --------------------------
// Скрытые методы управления свойствами
// --------------------------
// Обновляет таблицу соответствий компонент заменяя 'oldname'
// имя компонента на 'newname'
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

// Обновляет таблицу соответствий компонент устанавливая Id 'id'
// для компонента с именем 'name'
void NAContainer::SetLookupComponent(const NameT &name, const UId &id)
{
 CompsLookupTable[name]=id;
 if(LastId<id)
  LastId=id;
}

// Обновляет таблицу соответствий компонент удаляя запись
// компонента с именем 'name'
void NAContainer::DelLookupComponent(const NameT &name)
{
 map<NameT,UId>::iterator I=CompsLookupTable.find(name);

 if(I == CompsLookupTable.end())
  return; 

 CompsLookupTable.erase(name);
}
// --------------------------

// --------------------------
// Скрытые методы управления параметрами
// --------------------------
// Добавляет параметр с именем 'name' в таблицу соотвествий
// параметров и назначает ему корректный индекс
// Должна вызываться в конструкторах классов
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

// Удаляет параметр с именем 'name' из таблицы соотвествий
// параметров
bool NAContainer::DelLookupParameter(const NameT &name)
{
 map<NameT,NVariable>::iterator I=ParamsLookupTable.find(name);

 if(I == ParamsLookupTable.end())
  return false; 

 ParamsLookupTable.erase(I);
 return true;
}


// Возвращает полное имя параметра без префикса NMSDK, и суффикса '*'
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
// Скрытые методы управления состоянием
// --------------------------
// Добавляет переменную состояния с именем 'name' в таблицу соотвествий
// параметров и назначает ей корректный индекс
// Должна вызываться в конструкторах классов
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

// Удаляет переменную состояния с именем 'name' из таблицы соотвествий
bool NAContainer::DelLookupState(const NameT &name)
{
 map<NameT,NVariable>::iterator I=StateLookupTable.find(name);

 if(I == StateLookupTable.end())
  return false;

 StateLookupTable.erase(I);
 return true;
}

// Возвращает полное имя переменной состояния без префикса NMSDK, и суффикса '*'
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
// Скрытые методы управления локальными указателями
// --------------------------
// Добавляет указатель в таблицу соотвествий
// Должна вызываться в конструкторах классов
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

// Удаляет указатель с ID 'id' из таблицы соотвествий
bool NAContainer::DelLookupPointer(const UId &id)
{
 map<UId,RDK::UIPointer*>::iterator I=PointerLookupTable.find(id);

 if(I == PointerLookupTable.end())
  return true;

 PointerLookupTable.erase(I);
 return true;
}

// Возвращает полное имя указателя без префикса NMSDK, и суффикса '*'
NameT NAContainer::GetPointerLongName(const RDK::UIPointer &property) const
{
 return "";
}

// Осуществляет поиск в таблице указателя, соответствующего заданному источнику
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
// Скрытые методы управления таблицей компонент
// --------------------------
// Добавляет компонент 'comp' в таблицу компонент
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

// Удаляет компонент 'comp' из таблицы компонент
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
// Скрытые методы управления компонентами
// --------------------------
// Удаляет компонент comp
// Метод предполагает, что компонент принадлежит объекту
bool NAContainer::DelComponent(NAContainer* comp, bool canfree)
{
 if(!ADelComponent(comp))
  return false;

 if(comp->GetMainOwner() == MainOwner)
  comp->SetMainOwner(0);

 // Удаление из базы компонент
 // Удаляем компонент из таблицы соответствий владельца
 DelLookupComponent(comp->Name());

 // Удаление из базы компонент
 DelComponentTable(comp);

 comp->Owner=0;

 if(canfree)
  comp->Free();
 return true;
}


// Выполняет завершающие пользовательские действия
// при добавлении дочернего компонента в этот объект
// Метод будет вызван только если comp был
// успешно добавлен в список компонент
bool NAContainer::AAddComponent(UEPtr<UAContainer> comp, RDK::UIPointer* pointer)
{
 return true;
}

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
bool NAContainer::ADelComponent(UEPtr<UAContainer> comp)
{
 return true;
}
// --------------------------

/* *************************************************************************** */



/* *************************************************************************** */
/*
// --------------------------
// Конструкторы и деструкторы
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
// Системные методы управления объектом
// --------------------------
// Копирует этот объект в 'target' с сохранением всех компонент
// и значений параметров
// Если 'stor' == 0, то создание объектов осуществляется
// в том же хранилище где располагается этот объект
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
// Методы доступа к данным
// --------------------------
// Возвращает подключенный к этому коннектору объект по индексу
CItemT NAConnector::GetCItem(int c_index) const
{
 return CItemList[c_index];
}

// Возвращает пару индексов <выход, вход> подключения этого item или <-1,-1>
// если такая связь отсутствует
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
// Методы управления символическими ссылками
// --------------------------
// Возвращает число символических ссылок на входы
size_t NAConnector::GetNumInputSymLinks(void) const
{
 return GetNumSymLinks(InputSymLinks);
}

// Возвращает индекс входа по символической ссылке
size_t NAConnector::GetInputSymLink(const string &name) const
{
 return GetSymLink(name, InputSymLinks);
}

// Добавляет новую символическую ссылку на вход
// Возвращает false если такое имя уже существует
bool NAConnector::AddInputSymLink(const string &name, size_t index)
{
 return AddSymLink(name,index,InputSymLinks);
}

// Удаляет символическую ссылку на вход по имени
void NAConnector::DelInputSymLink(const string &name)
{
 DelSymLink(name, InputSymLinks);
}

// Удаляет все символические ссылки на заданный вход
void NAConnector::DelInputSymLink(size_t index)
{
 DelSymLink(index, InputSymLinks);
}

// Удаляет все символические ссылки
void NAConnector::DelInputSymLinks(void)
{
 DelSymLinks(InputSymLinks);
}

// Возвращает весь список ссылок
void NAConnector::GetInputSymLinksList(vector<NameT> &buffer) const
{
 GetSymLinksList(buffer,InputSymLinks);
}

// Копирует символические ссылки в объект target
bool NAConnector::CopyInputSymLinks(NAConnector *target) const
{
 return CopySymLinks(target,InputSymLinks);
}
// --------------------------

// ----------------------
// Коммуникационные методы
// ----------------------
// Устанавливает связь с элементом сети 'na'.
bool NAConnector::ConnectToItem(NAItem *na, int i_index, int &c_index)
{
 if(!na)
  return false;

 if((c_index < 0 || c_index >= int(NumInputs)) && AutoNumInputs == false)
  return false;

 if(i_index < 0 || i_index >= int(na->NumOutputs))
  return false;

 // Если включен режим автоматического добавления нового входа
 // и c_index<0 то добавляем новый вход либо подключаемся к наименьшему свободному
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
 else // Если c_index >= NumInputs то расширяем число входов до требуемого
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

// Разрывает связь с элементом сети 'na'
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

// Разрывает связь с элементом сети подключенным ко входу 'index'
void NAConnector::DisconnectFromIndex(int c_index)
{
 if(c_index<0 || c_index >=int(NumInputs))
  return;

// Build();

 ADisconnectFromItem(CItemList[c_index].Item);
 CItemList[c_index].Item=0;
 CItemList[c_index].Index=-1;
}

// Выполняет действия после физически установленой связи
bool NAConnector::AConnectToItem(NAItem *na)
{
 return true;
}

// Выполняет действия после физически разорваной связи
void NAConnector::ADisconnectFromItem(NAItem *na)
{
}

// Разрывает все текущие связи
void NAConnector::DisconnectAllItems(void)
{
// Build();
 for(size_t i=0;i<CItemList.size();i++)
  if(CItemList[i].Item)
   CItemList[i].Item->Disconnect(this);
}

// Разрывает все связи объекта
// исключая его внутренние связи и обратные связи
// brklevel - объект, относительно которого связи считаются внутренними
void NAConnector::DisconnectByObject(const NAContainer *brklevel)
{
// Build();
 for(size_t i=0;i<CItemList.size();i++)
  if(CItemList[i].Item)
   if(!CItemList[i].Item->CheckOwner(brklevel))
	CItemList[i].Item->Disconnect(this);
}

// Активирует этот коннектор (посылает запрос на прием данных
// этому коннектору).
void NAConnector::Activate(NAItem *na)
{
// Build();
}

// Возвращает список подключений
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
// Методы управления общедоступными свойствами
// --------------------------
// Возвращает число подключенных элементов item
size_t NAConnector::GetNumInputs(void) const
{
 return NumInputs;
}

// Устанавливает число подключенных элементов item
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
// Скрытые методы управления символическими ссылками
// --------------------------
// Возвращает число символических ссылок
size_t NAConnector::GetNumSymLinks(const map<NameT, size_t> &symlinks) const
{
 return symlinks.size();
}

// Возвращает индекс по символической ссылке
size_t NAConnector::GetSymLink(const string &name, const map<NameT, size_t> &symlinks) const
{
 map<NameT, size_t>::const_iterator I=symlinks.find(name);

 if(I == symlinks.end())
  return 0xFFFFFFFF;

 return I->second;
}

// Добавляет новую символическую ссылку
// Возвращает false если такое имя уже существует
bool NAConnector::AddSymLink(const string &name, size_t index, map<NameT, size_t> &symlinks)
{
 map<NameT, size_t>::iterator I=symlinks.find(name);

 if(I != symlinks.end())
  return false;

 symlinks[name]=index;
 return true;
}

// Удаляет символическую ссылку по имени
void NAConnector::DelSymLink(const string &name, map<NameT, size_t> &symlinks)
{
 map<NameT, size_t>::iterator I=symlinks.find(name);

 if(I != symlinks.end())
  symlinks.erase(I);
}

// Удаляет все символические ссылки по индексу
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

// Удаляет все символические ссылки
void NAConnector::DelSymLinks(map<NameT, size_t> &symlinks)
{
 symlinks.clear();
}

// Возвращает весь список ссылок
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

// Копирует символические ссылки в объект target
bool NAConnector::CopySymLinks(NAConnector *target, const map<NameT, size_t> &symlinks) const
{
 if(!target)
  return false;

 target->InputSymLinks=symlinks;
 return true;
}
// --------------------------

// --------------------------
// Методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NAConnector::Default(void)
{
 NumInputs=1;
 AutoNumInputs=true;
 return NAContainer::Default();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NAConnector::Build(void)
{
 return NAContainer::Build();
}
// --------------------------
			*/
/* *************************************************************************** */

/* *************************************************************************** */
// Методы
/*
// --------------------------
// Конструкторы и деструкторы
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
// Методы управления общедоступными свойствами
// --------------------------
// Возвращает число подключенных элементов item
size_t NAItem::GetNumOutputs(void) const
{
 return AssociatedConnectors.size();
}

// Устанавливает число подключенных элементов item
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
// Защищенные коммуникационные методы
// ----------------------
// Устанавливает связь с коннектором 'c'.
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

// Разрывает связь выхода этого объекта с коннектором 'c'.
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
// Коммуникационные методы
// ----------------------
// Возвращает текущее число соединений.
size_t NAItem::GetNumAConnectors(int index) const
{
 return NumAConnectors[index];
}

// Разрывает связь выхода этого объекта с коннектором по Id 'id'.
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

// Разрывает связь выхода этого объекта со всеми
// подключенными коннекторами.
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

// Разрывает все связи объекта
// исключая его внутренние связи и обратные связи
// brklevel - объект, относительно которого связи считаются внутренними
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

// Переустанавливает все связи этого item со всеми connectors которые получают
// данные от этого item
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

// Возвращает указатель на коннектор из списка подключений
// по имени 'name'.
const NAConnector* NAItem::GetAConnector(const UId &id, int index) const
{
 for(size_t i=0;i<NumAConnectors[index];i++)
  if(PAssociatedConnectors[index][i]->Id == id)
   return PAssociatedConnectors[index][i];
 return 0;
}

// Возвращает  коннектор из списка подключений.
const NAConnector* NAItem::GetAConnectorByIndex(int output, int index) const
{
 return AssociatedConnectors[output][index];
}

// Возвращает список подключений
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

// Возвращает список подключений этого компонента и всех дочерних компонент
// к заданному компоненту comp и всем его дочерним компонентам
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
// Методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NAItem::Default(void)
{
 NumOutputs=1;
 return NAConnector::Default();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NAItem::Build(void)
{
 if(IsReady())
  return true;

 BuildLinks();

 return NAConnector::Build();
}

// Активирует все коннекторы, подключенные к выходу этого объекта.
void NAItem::ActivateAll(void)
{
 Build();
 for(size_t j=0;j<AssociatedConnectors.size();j++)
  for(size_t i=0;i<NumAConnectors[j];i++)
   PAssociatedConnectors[j][i]->Activate(this);
}           */
/* *************************************************************************** */

/* *************************************************************************** */

// Методы
/*
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NADItem::NADItem(void)
// : NAItem(name),
 : OutputSize("OutputSize",this,&NADItem::SetVOutputSize,&NADItem::GetVOutputSize),
   DataOutputSize("DataOutputSize",this,&NADItem::SetVDataOutputSize,&NADItem::GetVDataOutputSize)
{
 // Указатель на первый элемент массива указателей на вектора входов
 POutputData=0;

 // Указатель на первый элемент массива указателей на вектора входов
 PInputData=0;

 // Указатель на первый элемент массива размеров векторов входов
 PInputDataSize=0;

 // Суммарное число всех входов
 FullInputSize=0;

 // Минимальный размер вектора входов
 MinInputDataSize=0;

 // Максимальный размер вектора входов
 MaxInputSize=0;
}

NADItem::~NADItem(void)
{
// DisconnectAll();
}                       
// --------------------------

// --------------------------
// Методы доступа к свойствам
// --------------------------

// Возвращает указатель на вектор входов Input по указателю на item
// Возвращает 0 если citem == 0 или не найден в списке подключений
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

// Возвращает указатель на вектор входов Input по индексу
// Не проверяет индекс на корректность
const NIOData* NADItem::GetInputData(size_t index) const
{
// if(!PInputData || index>=Input.size())
//  return 0;

 return PInputData[index];
}

// Возвращает размер вектора входов Input по индексу
// Не проверяет индекс на корректность
size_t NADItem::GetInputSize(size_t index) const
{
// if(!PInputDataSize || index>=Input.size())
//  return 0;

 return PInputDataSize[index];
}

// Возвращает суммарный размер всех векторов входов
size_t NADItem::GetFullInputSize(void) const
{
 return FullInputSize;
}
// --------------------------


// ----------------------
// Методы управления выходными данными
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

// Заполняет заданный выходной вектор данными
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

// Заполняет все выходные вектора заданными данными
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
// Методы доступа к системным свойствам
// ----------------------
// Размер выходных векторов
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

// Размер единичного данного вектора выходов в байтах
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
// Коммуникационные методы
// ----------------------
// Устанавливает связь с элементом сети 'na' со входом по индексу index.
// Переназначает связь если na уже подключен.
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

// Разрывает связь с элементом сети подключенным ко входу 'index'
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
// Методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NADItem::Default(void)
{
 SetDataOutputSize(0,sizeof(real));
 SetOutputDataSize(0,1);

 return NAItem::Default();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
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

// Сброс процесса счета без потери настроек
bool NADItem::Reset(void)
{
 if(!NAContainer::Reset())
  return false;
 FillOutputData();

 return true;
}
// --------------------------

// ----------------------
// Вспомогательные методы
// ----------------------
// Обновляет указатели на массивы входов и выходов
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
  // Указатель на первый элемент массива указателей на вектора входов
  PInputData=&Input[0];

  // Указатель на первый элемент массива размеров векторов входов
  PInputDataSize=&InputSize[0];
 }
 else
 {
  // Указатель на первый элемент массива указателей на вектора входов
  PInputData=0;

  // Указатель на первый элемент массива размеров векторов входов
  PInputDataSize=0;
 }

 // Суммарное число всех входов
 FullInputSize=0;
 for(size_t i=0;i<NumInputs;i++)
  FullInputSize+=PInputDataSize[i];
}


// Вычисляет минимальный и максимальный размер векторов входов
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
// Конструкторы и деструкторы
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
// Методы доступа к свойствам
// --------------------------
LinksListT& NANet::GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const
{
 GetLinks(this, linkslist, netlevel);

 return linkslist;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NANet::CheckComponentType(UEPtr<NAContainer> comp) const
{
 return (dynamic_cast<const NAItem*>(comp) ||
 dynamic_cast<const NANet*>(comp) || dynamic_cast<const NAConnector*>(comp))?true:false;
}
// --------------------------

// --------------------------
// Скрытые методы управления компонентами
// --------------------------
// Выполняет завершающие пользовательские действия
// при добавлении дочернего компонента в этот объект
// Метод будет вызван только если comp был
// успешно добавлен в список компонент
bool NANet::AAddComponent(UEPtr<UAContainer> comp, RDK::UIPointer* pointer)
{
 return true;
}

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
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
// Системные методы управления объектом
// --------------------------
// Копирует этот объект в 'target' с сохранением всех компонент
// и значений параметров
// Если 'stor' == 0, то создание объектов осуществляется
// в том же хранилище где располагается этот объект
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
// Методы управления связями
// ----------------------
// Устанавливает новую связь между выходом элемента сети
// 'item' и коннектором 'connector'
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

// Устанавливает новую связь между выходом элемента сети
// 'item' и коннектором 'connector'
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

// Устанавливает все связи из массива 'linkslist'.
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

// Разрывает все связи с выходом элемента сети, если
// 'id' - есть Id элемента сети.
// Иначе, если 'id' - Id коннектора, то метод разрывает
// связи этого коннектора.
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

// Разрывает связь между выходом элемента сети, 'itemid' 
// и коннектором 'connectorid'
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

// Разрывает связь между выходом элемента сети, 'itemid'
// и коннектором 'connectorid'
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

// Разрывает все связи сети
// исключая ее внутренние связи и обратные связи
// brklevel - объект, относительно которого связи считаются внутренними
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

// Разрывает заданные связи сети
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

// Разрывает все внутренние связи сети.
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
// Скрытые методы доступа к свойствам
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

