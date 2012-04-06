#ifndef NStorageH
#define NStorageH

#include "NBios.h"
#include "rdk.h"

namespace NMSDK{

class NStorage: public RDK::UAContainerStorage
{
private: // Системные свойства

protected: // Основные свойства

protected: // Временные переменные

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NStorage(void);
virtual ~NStorage(void);
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
RDK::UEPtr<RDK::UAComponent> TakeObject(const UId &classid, const UEPtr<UAComponent> prototype=0);
RDK::UEPtr<RDK::UAComponent> TakeObject(const string &classname, const UEPtr<UAComponent> prototype=0);

};



}

#endif
