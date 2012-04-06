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

#ifndef NENVIRONMENT_H
#define NENVIRONMENT_H

#include "rdk.h"
#include "NBios.h"
#include "NLibrary.h"
#include "../Libraries/BCL/NModel.h"
#include "../GUI/NGraphics.h"
#include "NController.h"

namespace NMSDK {

class NEnvironment: public RDK::UAContainerEnvironment
{
protected: // Параметры

protected: // Данные

protected: // Контроллеры
// Список действующих контроллеров
// <Контроллер, флаг, разрешающий удалять контроллер среде>
map<NController*, bool> Controllers;

protected: // Данные графического интерфеса пользователя
// Визуализаторы модели
map<ULongId, NGraphics*> Graphics;

public: // Public methods
// --------------------------
// Constructors & destructors
// --------------------------
NEnvironment(void);
virtual ~NEnvironment(void);
// --------------------------

// --------------------------
// Методы управления данными среды
// --------------------------
// Возвращает указатель на модель
RDK::UEPtr<NModel> GetModel(void);

// Уничтожает текущую модель
virtual bool DestroyModel(void);
// --------------------------

// --------------------------
// Методы управления моделью
// --------------------------
// Добавляет объект заданного класса в модель
// Возвращает указатель на добавленный объект
RDK::UEPtr<NAContainer> AddObject(const NameT &classname);

// Добавляет объект заданного класса 'classname' в модель
// в случае, если объект с именем 'objectname' не найден в модели
// Возвращает указатель на объект
// Метод не гарантирует задание имени 'objectname', если такое имя уже имеется в модели
RDK::UEPtr<NAContainer> AddObject(const NameT &objectname, const NameT &classname);
// --------------------------

// --------------------------
// Методы управления контроллерами
// --------------------------
// Добавляет контроллер
bool AddController(NController* controller, bool delenabled);

// Удаляет контроллер
bool DelController(NController* controller);

// Удаляет все контроллеры
bool DelAllControllers(void);

// Методы перечисления контроллеров
map<NController*, bool>::iterator GetFirstController(void);
map<NController*, bool>::iterator GetLastController(void);
// --------------------------

// --------------------------
// Операторы доступа к данным среды
// --------------------------
// Возвращает указатель на модель
RDK::UEPtr<NModel> const operator -> (void);

// Возвращает указатель на компонент модели по длинному имени
// Выбраный компонент становится текущим
// Если компонент не найден, то возвращает 0 и сбрасывает текущий компонент
RDK::UEPtr<NAContainer> operator () (const string &longname);

// Возвращает указатель на компонент модели по длинному идентификатору
// Выбраный компонент становится текущим
// Если компонент не найден, то возвращает 0 и сбрасывает текущий компонент
RDK::UEPtr<NAContainer> operator () (const ULongId &longid);

// Возвращает указатель на текущий компонент модели
RDK::UEPtr<NAContainer> operator () (void);
// --------------------------

// --------------------------
// Данные графического интерфеса пользователя
// --------------------------
// Возвращает список визуализаторов
const map<ULongId, NGraphics*>& GetGraphics(void) const;

// Возвращает визуализатор для заданного id
NGraphics* GetGraphics(const ULongId &id);

// Проверяет наличие визуализатора для заданной сети
bool CheckGraphics(const ULongId &id) const;

// Добавляет новый визуализатор
// Не делает ничего если визуализатор уже задан
// Возвращает созданный визуализатор
// Среда не берет на себя задачу освобождения памяти объекта
NGraphics* AddGraphics(const ULongId &id, NGraphics *graphics);

// Удаляет визуализатор сети id
bool DelGraphics(const ULongId &id);
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
protected:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool ADefault(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool ABuild(void);

// Сброс процесса счета.
virtual bool AReset(void);

// Выполняет расчет этого объекта
virtual bool ACalculate(void);
// --------------------------

// --------------------------
// Вспомогательные методы инициализации среды
// --------------------------
protected:
/*
// Загружает динамическую библиотеку с экземпляром хранилища и возвращает
// указатель на него.
// В базовой версии не делает ничего и возвращает 0.
virtual RDK::UAStorage* LoadStorageLibrary(const string &filename);

// Выгружает динамическую библиотеку с экземпляром хранилища.
// В базовой версии не делает ничего и возвращает true.
virtual bool UnLoadStorageLibrary(void);

// Загружает динамическую библиотеку с набором образцов классов
// в виде экземпляра хранилища и возвращает указатель на него.
// В базовой версии не делает ничего и возвращает 0.
virtual RDK::UAStorage* LoadClassLibrary(const string &libname, const string &filename);

// Выгружает динамическую библиотеку с набором образцов классов.
// В базовой версии не делает ничего и возвращает true.
virtual bool UnLoadClassLibrary(const string &libname);     */
// --------------------------
};

}
#endif
