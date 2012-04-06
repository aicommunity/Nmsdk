/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002-2009.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		2.0.0

This file - part of the project: NMSDK

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NENVIRONMENT_CPP
#define NENVIRONMENT_CPP

#include "NEnvironment.h"
//#include "NParserUtility.h"

namespace NMSDK {

// --------------------------
// Constructors & destructors
// --------------------------
NEnvironment::NEnvironment(void)
 : RDK::UAContainerEnvironment()
{
}

NEnvironment::~NEnvironment(void)
{
}
// --------------------------

// --------------------------
// Методы управления данными среды
// --------------------------
// Возвращает указатель на модель
RDK::UEPtr<NModel> NEnvironment::GetModel(void)
{
 return RDK::static_pointer_cast<NModel>(Model);
}

// Уничтожает текущую модель
bool NEnvironment::DestroyModel(void)
{
 if(!Model)
  return true;

// GetModel()->Free();
 return RDK::UAContainerEnvironment::DestroyModel();
}
// --------------------------

// --------------------------
// Методы управления контроллерами
// --------------------------
// Добавляет контроллер
bool NEnvironment::AddController(NController* controller, bool delenabled)
{
 map<NController*, bool>::iterator I=Controllers.find(controller);

 if(I != Controllers.end())
  return true;

 if(!controller)
  return false;

 Controllers[controller]=delenabled;
 return true;
}

// Удаляет контроллер
bool NEnvironment::DelController(NController* controller)
{
 map<NController*, bool>::iterator I=Controllers.find(controller);

 if(I != Controllers.end())
 {
  if(I->second)
   delete I->first;
  Controllers.erase(I);
 }

 return true;
}

// Удаляет все контроллеры
bool NEnvironment::DelAllControllers(void)
{
 map<NController*, bool>::iterator I,J;

 I=Controllers.begin();
 J=Controllers.end();
 while(I != J)
 {
  if(I->second)
   delete I->first;
  ++I;
 }
 Controllers.clear();
 return true;
}

// Методы перечисления контроллеров
map<NController*, bool>::iterator NEnvironment::GetFirstController(void)
{
 return Controllers.begin();
}

map<NController*, bool>::iterator NEnvironment::GetLastController(void)
{
 return Controllers.end();
}
// --------------------------

// --------------------------
// Операторы доступа к данным среды
// --------------------------
// Возвращает указатель на модель
RDK::UEPtr<NModel> const NEnvironment::operator -> (void)
{
 return GetModel();
}

// Возвращает указатель на компонент модели по длинному имени
// Выбраный компонент становится текущим
// Если компонент не найден, то возвращает 0 и сбрасывает текущий компонент
RDK::UEPtr<NAContainer> NEnvironment::operator () (const string &longname)
{
 if(!Model)
  CurrentComponent=0;
 else
  CurrentComponent=GetModel()->GetComponentL(longname);

 return RDK::static_pointer_cast<NAContainer>(CurrentComponent);
}

// Возвращает указатель на компонент модели по длинному идентификатору
// Выбраный компонент становится текущим
// Если компонент не найден, то возвращает 0 и сбрасывает текущий компонент
RDK::UEPtr<NAContainer> NEnvironment::operator () (const ULongId &longid)
{
 if(!Model)
  CurrentComponent=0;
 else
  CurrentComponent=GetModel()->GetComponentL(longid);

 return RDK::static_pointer_cast<NAContainer>(CurrentComponent);
}

// Возвращает указатель на текущий компонент модели
RDK::UEPtr<NAContainer> NEnvironment::operator () (void)
{
 return RDK::static_pointer_cast<NAContainer>(CurrentComponent);
}
// --------------------------

// --------------------------
// Данные графического интерфеса пользователя
// --------------------------
// Возвращает список визуализаторов
const map<ULongId, NGraphics*>& NEnvironment::GetGraphics(void) const
{
 return Graphics;
}

// Возвращает визуализатор для заданного id
NGraphics* NEnvironment::GetGraphics(const ULongId &id)
{
 map<ULongId, NGraphics*>::iterator I;
 I=Graphics.find(id);
 if(I == Graphics.end())
  return 0;

 return I->second;
}

// Проверяет наличие визуализатора для заданной сети
bool NEnvironment::CheckGraphics(const ULongId &id) const
{
 map<ULongId, NGraphics*>::const_iterator I;
 I=Graphics.find(id);
 if(I == Graphics.end())
  return false;

 return true;
}

// Добавляет новый визуализатор
// Не делает ничего если визуализатор уже задан
// Возвращает созданный визуализатор
// Среда не берет на себя задачу освобождения памяти объекта
NGraphics* NEnvironment::AddGraphics(const ULongId &id, NGraphics *graphics)
{
 map<ULongId, NGraphics*>::iterator I;
 I=Graphics.find(id);
 if(I != Graphics.end())
  return I->second;

 if(!graphics)
  return 0;

 Graphics[id]=graphics;
 return graphics;
}

// Удаляет визуализатор сети id
bool NEnvironment::DelGraphics(const ULongId &id)
{
 map<ULongId, NGraphics*>::iterator I;
 I=Graphics.find(id);
 if(I != Graphics.end())
  Graphics.erase(I);

 return true;
}
// --------------------------

// --------------------------
// Методы инициализации среды
// --------------------------
// --------------------------

// --------------------------
// Методы доступа к флагам состояний
// --------------------------
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NEnvironment::ADefault(void)
{
 if(!RDK::UAContainerEnvironment::ADefault())
  return false;

 NAContainer::SetTime(0);
 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NEnvironment::ABuild(void)
{
 if(!RDK::UAContainerEnvironment::ABuild())
  return false;

 return true;
}

// Сброс процесса счета.
bool NEnvironment::AReset(void)
{
 if(!RDK::UAContainerEnvironment::AReset())
  return false;

 NAContainer::SetTime(0);
 return true;
}

// Выполняет расчет этого объекта
bool NEnvironment::ACalculate(void)
{
 if(!RDK::UAContainerEnvironment::ACalculate())
  return false;

 return true;
}
// --------------------------

// --------------------------
// Вспомогательные методы инициализации среды
// --------------------------
// Загружает динамическую библиотеку с экземпляром хранилища и возвращает
// указатель на него.
// В базовой версии не делает ничего и возвращает 0.
/*RDK::UAStorage* NEnvironment::LoadStorageLibrary(const string &filename)
{
 return 0;
}

// Выгружает динамическую библиотеку с экземпляром хранилища.
// В базовой версии не делает ничего и возвращает true.
bool NEnvironment::UnLoadStorageLibrary(void)
{
 return true;
}

// Загружает динамическую библиотеку с набором образцов классов
// в виде экземпляра хранилища и возвращает указатель на него.
// В базовой версии не делает ничего и возвращает 0.
RDK::UStorage* NEnvironment::LoadClassLibrary(const string &libname, const string &filename)
{
 return 0;
}

// Выгружает динамическую библиотеку с набором образцов классов.
// В базовой версии не делает ничего и возвращает true.
bool NEnvironment::UnLoadClassLibrary(const string &libname)
{
 return true;
}               */
// --------------------------

// --------------------------
// Методы управления моделью
// --------------------------
// Добавляет объект заданного класса в модель
// Возвращает указатель на добавленный объект
RDK::UEPtr<NAContainer> NEnvironment::AddObject(const NameT &classname)
{
 RDK::UEPtr<NAContainer> comp=0;

 if(!Storage || !Model)
  return 0;

 comp=RDK::static_pointer_cast<NAContainer>(GetStorage()->TakeObject(classname));

 if(!comp)
  return 0;

 if(!GetModel()->AddComponent(comp))
 {
  comp->Free();
//  Storage->ReturnObject(RDK::static_pointer_cast<RDK::UAComponent>(comp));
  return 0;
 }
 return comp;
}


// Добавляет объект заданного класса 'classname' с заданным именем 'objectname'
// в модель в случае, если объект с именем 'objectname' не найден в модели
// Возвращает указатель на объект
// Метод не гарантирует задание имени 'objectname', если такое имя уже имеется в модели
RDK::UEPtr<NAContainer> NEnvironment::AddObject(const NameT &objectname, const NameT &classname)
{
 if(!Model)
  return 0;

 RDK::UEPtr<NAContainer> comp=GetModel()->GetComponent(objectname);

 if(!comp)
 {
  comp=AddObject(classname);
  if(!comp)
   return 0;

  comp->SetName(objectname);
 }

 return RDK::dynamic_pointer_cast<NAContainer>(comp);
}
// --------------------------


}
#endif
