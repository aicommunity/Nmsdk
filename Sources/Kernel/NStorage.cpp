#ifndef NSTORAGE_CPP
#define NSTORAGE_CPP

#include <algorithm>
#include "NStorage.h"

namespace NMSDK{

/* *************************************************************************** */
// Class NStorage
/* *************************************************************************** */
// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NStorage::NStorage(void)
{
// LastClassId=0;
}

NStorage::~NStorage(void)
{
// ClearObjectsStorage();
// ClearClassesStorage();
}
// --------------------------

// --------------------------
// Методы управления свойствами
// --------------------------
// Возвращает последний использованный Id классов
/*IdT NStorage::GetLastClassId(void) const
{
 return LastClassId;
} */
// --------------------------

// --------------------------
// Методы доступа к таблицам соотвествий
// --------------------------
// Возвращает имя класса по его Id
/*const NameT& NStorage::GetClassName(const IdT &id) const
{
 map<NameT,IdT>::const_iterator I=ClassesLookupTable.begin(),
								 J=ClassesLookupTable.end();
 while(I != ClassesLookupTable.end())
  {
   if(I->second == id)
	return I->first;
   ++I;
  }
 return ForbiddenName;
}                  */

// Возвращает Id класса по его имени
/*const IdT& NStorage::GetClassId(const NameT &name) const
{
 map<NameT,IdT>::const_iterator I=ClassesLookupTable.find(name);
 if(I == ClassesLookupTable.end())
  return ForbiddenId;
 else return I->second;
} */
// --------------------------

// --------------------------
// Методы управления хранилищем классов
// --------------------------
// Добавляет образец класса объекта в хранилище
/*bool NStorage::AddClass(const NameT &classname, MySDK::UComponent *classtemplate)
{
 IdT id;

 if(!classtemplate || classname == "")
  return false;

 id=AddLookupClass(classname);
 if(id == ForbiddenId)
  return false;

 if(classtemplate->GetOwner())
  if(!static_cast<NAContainer*>(classtemplate->GetOwner())->DelComponent(static_cast<NAContainer*>(classtemplate),false))
   return false;

 if(classtemplate->GetStorage())
  classtemplate->GetStorage()->PopObject(classtemplate);

 ClassesStorage[id]=classtemplate;
 static_cast<NAContainer*>(classtemplate)->Activity=false;
 classtemplate->SetClass(id);

 return true;
}              */

// Удаляет образец класса объекта из хранилища
// Возвращает false если classid не найден,
// или присутствуют объекты этого класса
/*bool NStorage::DelClass(const IdT &classid)
{
 ClassesStorageIterator I=ClassesStorage.find(classid);

 if(I == ClassesStorage.end())
  return false;

 if(ObjectsStorage[classid].size() > 0)
  return false;

 delete I->second;
 ClassesStorage.erase(I);

 map<NameT,IdT>::iterator oI=ClassesLookupTable.begin(),
                                 oJ=ClassesLookupTable.end();
 while(oI != oJ)
  {
   if(oI->second == classid)
    {
     ClassesLookupTable.erase(oI);
     break;
    }
   ++oI;
  }

 return true;
}             */

// Проверяет наличие образца класса объекта в хранилище
/*bool NStorage::CheckClass(const IdT &classid) const
{
 if(ClassesStorage.find(classid) == ClassesStorage.end())
  return false;

 return true;
}                */

// Возвращает образец класса
/*NAContainer* const NStorage::GetClass(const IdT &classid) const
{
 ClassesStorageCIterator I=ClassesStorage.find(classid);

 if(I == ClassesStorage.end())
  return 0;

 return I->second;
} */

// Возвращает список имен всех классов хранилища
// Буфер 'buffer' будет очищен от предыдущих значений
/*void NStorage::GetClassNameList(vector<NameT> &buffer) const
{
 map<NameT,IdT>::const_iterator I,J;
 NameT* pbuffer=0;

 I=ClassesLookupTable.begin();
 J=ClassesLookupTable.end();
 buffer.resize(ClassesLookupTable.size());

 if(buffer.size()>0)
  pbuffer=&buffer[0];
 while(I != J)
  {
   *pbuffer++=I->first;
   ++I;
  }
}     */
/*
// Удаляет все не используемые образцы классов из хранилища
void NStorage::FreeClassesStorage(void)
{
 ClassesStorageIterator I,J,K;

 I=ClassesStorage.begin();
 J=ClassesStorage.end();

 while(I != J)
  {
   if(ObjectsStorage[I->first].size() == 0)
    {
     K=I; ++I;
     DelClass(K->first);
    }
   else
    ++I;
  }
}

// Удаляет все образцы классов из хранилища
// Возвращает false если в хранилище присутствуют объекты
bool NStorage::ClearClassesStorage(void)
{
 ClassesStorageIterator I,J;

 I=ClassesStorage.begin();
 J=ClassesStorage.end();

 while(I != J)
  {
   if(ObjectsStorage[I->first].size() != 0)
    return false;
   ++I;
  }

 ClassesLookupTable.clear();

 I=ClassesStorage.begin();
 while(I != J)
  {
   delete I->second;
   ++I;
  }

 ClassesStorage.clear();
 return true;
}              */
// --------------------------

// --------------------------
// Методы управления хранилищем объектов
// --------------------------
// Извлекает объект из хранилища
// Возвращает указатель на свободный объект по имени класса
// Выбранный объект помечается как занятый в хранилище
// Флаг 'Activity' объекта выставляется в true
// Если свободного объекта не существует он создается и добавляется
// в хранилище

RDK::UEPtr<RDK::UAComponent> NStorage::TakeObject(const UId &classid, const RDK::UAComponent *prototype)
{
 return RDK::UAContainerStorage::TakeObject(classid,prototype);
// return dynamic_pointer_cast<NAContainer>(RDK::UAContainerStorage::TakeObject(classid,prototype));
/* MySDK::ClassesStorageIterator CI=ClassesStorage.find(classid);
 if(CI == ClassesStorage.end())
  return 0;

 MySDK::FreeObjectsTableIterator tI=FreeObjectsTable.find(classid);
 if(tI != FreeObjectsTable.end())
 {
  if(tI->second.size()>0)
  {
   MySDK::InstancesStorageIterator oI=tI->second.back();
   NAContainer* res=static_cast<NAContainer*>(oI->first);
   if(!static_cast<NAContainer*>(CI->second)->Copy(res,this))
	return 0;

   oI->second=true;
   res->Activity=true;
   tI->second.resize(tI->second.size()-1);
   return res;
  }
 }



 // Если свободного объекта не нашли
 NAContainer *obj=static_cast<NAContainer*>(CI->second)->New();
 if(!obj)
  return 0;

 obj->Name=static_cast<NAContainer*>(CI->second)->Name();

 // В случае, если объект создается непосредственно как копия из хранилища...
 if(!prototype)
 {
  if(!static_cast<NAContainer*>(CI->second)->Copy(obj,this))
  {
   delete obj;
   obj=0;
   return 0;
  }
 }
 else
 {
  // В случае, если объект создается из хранилища как часть более сложного
  // объекта
  if(!static_cast<const NAContainer*>(prototype)->Copy(obj,this))
  {
   delete obj;
   obj=0;
   return 0;
  }
 }

 if(!PushObject(classid,obj))
  {
   delete obj;
   obj=0;
   return 0;
  }

 obj->ObjectIterator=ObjectsStorage[classid].insert(pair<NAContainer*,bool>(obj,true)).first;
// ObjectsStorage[classid][obj]=true;
 obj->Activity=true;
// obj->Class=GetClassName(classid);
 obj->Class=classid;

 return obj;   */
}

RDK::UEPtr<RDK::UAComponent> NStorage::TakeObject(const NameT &classname, const RDK::UAComponent *prototype)
{
 return RDK::UAContainerStorage::TakeObject(classname,prototype);
// return dynamic_pointer_cast<NAContainer>(RDK::UAContainerStorage::TakeObject(classname,prototype));
}
		/*
NAContainer* NStorage::TakeObject(const IdT &classid, const NAContainer *prototype)
{
 return static_cast<NAContainer*>(TakeObject(classid,static_cast<const MySDK::UComponent*>(prototype)));
}

NAContainer* NStorage::TakeObject(const string &classname, const NAContainer *prototype)
{
 return static_cast<NAContainer*>(TakeObject(classname,static_cast<const MySDK::UComponent*>(prototype)));
}      */

// Возвращает объект в хранилище
// Выбранный объект помечается как свободный в хранилище
// Флаг 'Activity' объекта выставляется в false
// Если объект не существует в хранилище - возвращается false
/*bool NStorage::ReturnObject(MySDK::UComponent *object)
{
 if(!object)
  return false;

 static_cast<NAContainer*>(object)->ObjectIterator->second=false;
 static_cast<NAContainer*>(object)->Activity=false;
 object->SetOwner(0); // возможно это не так? еще не проверено
 MySDK::FreeObjectsTableIterator tI=FreeObjectsTable.find(object->GetClass());
 if(tI != FreeObjectsTable.end())
 {
  tI->second.push_back(static_cast<NAContainer*>(object)->ObjectIterator);
 }

 // Возвращаем все содержимое компонента
 for(size_t i=0;i<static_cast<NAContainer*>(object)->GetNumComponents();i++)
  if(!ReturnObject(static_cast<NAContainer*>(object)->GetComponentByIndex(i)))
   return false;

 return true;
}
						 */
// Добавляет уже созданный объект в хранилище
// Если объект уже принадлежит иному хранилищу то возвращает false
/*bool NStorage::PushObject(const IdT &classid, NAContainer *object)
{
 if(!object || classid == ForbiddenId || object->GetStorage())
  return false;

 ClassesStorageIterator cI=ClassesStorage.find(classid);
 if(cI == ClassesStorage.end())
  return false;

 ObjectsStorage[classid][object]=true;//(object->GetOwner())?true:false;
 object->Storage=this;
 return true;
} */

// Выводит уже созданный объект из хранилища и возвращает
// его classid
// В случае ошибки возвращает ForbiddenId
/*IdT NStorage::PopObject(MySDK::UComponent *object)
{
 if(!object)
  return ForbiddenId;

 MySDK::ObjectsStorageIterator oI,oJ;
 MySDK::InstancesStorageIterator I,J;

 oI=ObjectsStorage.begin();
 oJ=ObjectsStorage.end();

 while(oI != oJ)
  {
   I=oI->second.begin();
   J=oI->second.end();
   while(I !=J)
    {
     if(I->first == object)
      {
	   object->SetStorage(0);

	   // удаляем из таблицы свободных компонент если необходимо
	   if(!static_cast<NAContainer*>(object)->ObjectIterator->second)
	   {
		MySDK::FreeObjectsTableIterator tI,tJ;
		tI=FreeObjectsTable.find(object->GetClass());
		if(tI != FreeObjectsTable.end())
		{
		 vector<MySDK::InstancesStorageIterator>::iterator table_item=find(tI->second.begin(),tI->second.end(),static_cast<NAContainer*>(object)->ObjectIterator);
		 if(table_item != tI->second.end())
		  tI->second.erase(table_item);
		}
       }
	   oI->second.erase(I);

	   static_cast<NAContainer*>(object)->ObjectIterator=J;
       return oI->first;
      }
     ++I;
    }
   ++oI;
  }

 return ForbiddenId;
}          */

/*
// Перемещает объект в другое хранилище
bool NStorage::MoveObject(NAContainer *object, NStorage *newstorage)
{
 if(!newstorage)
  return false;

 return newstorage->PushObject(PopObject(object),object);
}

// Проверяет существует ли объект 'object' в хранилище
bool NStorage::CheckObject(const NAContainer *object) const
{
 if(!object)
  return false;
 ObjectsStorageCIterator oI,oJ;
 InstancesStorageCIterator I,J;

 oI=ObjectsStorage.begin();
 oJ=ObjectsStorage.end();

 while(oI != oJ)
  {
   I=oI->second.begin();
   J=oI->second.end();
   while(I !=J)
    {
     if(I->first == object)
      {
       return true;
      }
     ++I;
    }
   ++oI;
  }

 return false;
}          */
					/*
// Возвращает Id класса, отвечающий объекту 'object'
IdT NStorage::FindClass(const NAContainer *object) const
{
 if(!object)
  return ForbiddenId;

 return object->Class;
}                     */
/*
// Вычисляет суммарное число объектов в хранилище
size_t NStorage::CalcNumObjects(void) const
{
 NAContainer *obj;
 size_t result=0;

 ObjectsStorageCIterator oI,oJ;
 InstancesStorageCIterator I,J,K;

 oI=ObjectsStorage.begin();
 oJ=ObjectsStorage.end();

 while(oI != oJ)
  {
   I=oI->second.begin();
   J=oI->second.end();
   while(I !=J)
	{
	 ++result;
	 ++I;
	}
   ++oI;
  }
 return result;
}

size_t NStorage::CalcNumObjects(const IdT &classid) const
{
 ObjectsStorageCIterator oI=ObjectsStorage.find(classid);

 if(oI != ObjectsStorage.end())
  return oI->second.size();

 return 0;
}

size_t NStorage::CalcNumObjects(const string &classname) const
{
 return CalcNumObjects(GetClassId(classname));
}


// Удалаяет все свободные объекты из хранилища
void NStorage::FreeObjectsStorage(void)
{
 NAContainer *obj;

 ObjectsStorageIterator oI,oJ;
 InstancesStorageIterator I,J,K;

 oI=ObjectsStorage.begin();
 oJ=ObjectsStorage.end();

 while(oI != oJ)
  {
   I=oI->second.begin();
   J=oI->second.end();
   while(I !=J)
	{
	 if(I->second == false)
	  {
	   K=I; ++I;
	   obj=K->first;
	   obj->Storage=0;
	   oI->second.erase(K);
	   delete obj;
	  }
	 else
	  ++I;
	}
   ++oI;
  }

 FreeObjectsTableIterator tI,tJ;
 tI=FreeObjectsTable.begin();
 tJ=FreeObjectsTable.end();
 while(tI != tJ)
 {
  tI->second.resize(0);
  ++tI;
 }
}

// Удаляет все объекты из хранилища
void NStorage::ClearObjectsStorage(void)
{
 NAContainer *obj;

 ObjectsStorageIterator oI,oJ;
 InstancesStorageIterator I,J,K;

 oI=ObjectsStorage.begin();
 oJ=ObjectsStorage.end();

 while(oI != oJ)
  {
   I=oI->second.begin();
   J=oI->second.end();
   while(I != J)
    {
     K=I; ++I;
     obj=K->first;
     obj->Storage=0;
     oI->second.erase(K);
     delete obj;
    }
   ++oI;
  }

 FreeObjectsTableIterator tI,tJ;
 tI=FreeObjectsTable.begin();
 tJ=FreeObjectsTable.end();
 while(tI != tJ)
 {
  tI->second.resize(0);
  ++tI;
 }
}             */
// --------------------------

// --------------------------
// Скрытые методы таблицы соответствий классов
// --------------------------
/*
// Добавляет класс с именем 'name' в таблицу соответствий
IdT NStorage::AddLookupClass(const NameT &name)
{
 if(ClassesLookupTable.find(name) != ClassesLookupTable.end())
  return ForbiddenId;

 ClassesLookupTable.insert(make_pair(name,++LastClassId));

 return LastClassId;
}

// Удаляет класс с именем 'name' из таблицы соотвествий
bool NStorage::DelLookupClass(const NameT &name)
{
 map<NameT,IdT>::iterator I=ClassesLookupTable.find(name);

 if(I == ClassesLookupTable.end())
  return false;

 ClassesLookupTable.erase(I);
 return true;
}           */
// --------------------------
/* *************************************************************************** */



}
#endif

