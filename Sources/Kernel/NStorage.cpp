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
}

NStorage::~NStorage(void)
{
}
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

