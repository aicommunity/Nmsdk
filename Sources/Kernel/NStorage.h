#ifndef NStorageH
#define NStorageH

#include "NBios.h"
#include "rdk.h"

namespace NMSDK{

class NStorage: public RDK::UAContainerStorage
{
private: // Системные свойства
// Таблица соответствий имен и Id образцов классов
//map<string,IdT> ClassesLookupTable;

protected: // Основные свойства
// Список доступных классов объектов
//ClassesStorageT ClassesStorage;

// Список объектов
//ObjectsStorageT ObjectsStorage;

// Последний использованный Id образцов классов
//IdT LastClassId;

protected: // Временные переменные
// Таблица итераторов на свободные объекты классов
//FreeObjectsTableT FreeObjectsTable;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NStorage(void);
virtual ~NStorage(void);
// --------------------------

// --------------------------
// Методы управления свойствами
// --------------------------
// Возвращает последний использованный Id классов
//IdT GetLastClassId(void) const;
// --------------------------

// --------------------------
// Методы доступа к таблицам соотвествий
// --------------------------
// Возвращает имя класса по его Id
//const string& GetClassName(const UId &id) const;

// Возвращает Id класса по его имени
//const UId& GetClassId(const string &name) const;
// --------------------------

// --------------------------
// Методы управления хранилищем классов
// --------------------------
// Добавляет образец класса объекта в хранилище
//bool AddClass(const string &classname, RDK::UAComponent *classtemplate);

// Удаляет образец класса объекта из хранилища
// Возвращает false если classid не найден,
// или присутствуют объекты этого класса
//bool DelClass(const UId &classid);

// Проверяет наличие образца класса объекта в хранилище
//bool CheckClass(const UId &classid) const;

// Возвращает образец класса
//NAContainer* const GetClass(const UId &classid) const;

// Возвращает список имен всех классов хранилища
// Буфер 'buffer' будет очищен от предыдущих значений
//void GetClassNameList(vector<string> &buffer) const;

// Удаляет все не используемые образцы классов из хранилища
//void FreeClassesStorage(void);

// Удаляет все образцы классов из хранилища
// Возвращает false если в хранилище присутствуют объекты
//bool ClearClassesStorage(void);
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
RDK::UEPtr<RDK::UAComponent> TakeObject(const UId &classid, const RDK::UAComponent *prototype=0);
RDK::UEPtr<RDK::UAComponent> TakeObject(const string &classname, const RDK::UAComponent *prototype=0);

// Возвращает объект в хранилище
// Выбранный объект помечается как свободный в хранилище
// Флаг 'Activity' объекта выставляется в false
// Если объект не существует в хранилище - возвращается false
//bool ReturnObject(RDK::UAComponent *object);

// Добавляет уже созданный объект в хранилище
// Если объект уже принадлежит иному хранилищу то возвращает false
//bool PushObject(const UId &classid, NAContainer *object);

// Выводит уже созданный объект из хранилища и возвращает
// его classid
// В случае ошибки возвращает ForbiddenId
//UId PopObject(RDK::UAComponent *object);

// Перемещает объект в другое хранилище
//bool MoveObject(NAContainer *object, NStorage *newstorage);

// Проверяет существует ли объект 'object' в хранилище
//bool CheckObject(const NAContainer *object) const;

// Возвращает Id класса, отвечающий объекту 'object'
//UId FindClass(const NAContainer *object) const;

// Вычисляет суммарное число объектов в хранилище
//size_t CalcNumObjects(void) const;
//size_t CalcNumObjects(const UId &classid) const;
//size_t CalcNumObjects(const string &classname) const;

// Удалаяет все свободные объекты из хранилища
//void FreeObjectsStorage(void);

// Удаляет все объекты из хранилища
//void ClearObjectsStorage(void);
// --------------------------

// --------------------------
// Скрытые методы таблицы соответствий классов
// --------------------------
protected:
// Добавляет класс с именем 'name' в таблицу соответствий
//UId AddLookupClass(const string &name);

// Удаляет класс с именем 'name' из таблицы соотвествий
//bool DelLookupClass(const string &name);
// --------------------------
};



}

#endif
