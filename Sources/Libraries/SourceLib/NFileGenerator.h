// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NFILE_GENERATOR_H
#define NFILE_GENERATOR_H

#include "../BCL/NSource.h"
#include "rdk.h"

namespace NMSDK {

class NFileGenerator: public NSource
{
public: // Общедоступные свойства
// Имя файла с данными
RDK::ULProperty<string,NFileGenerator> FileName;

protected: // Основные свойства

protected: // Данные
RDK::UIniFile<char> Ini;

// 2D массив входов на каждый момент времени
map<real,vector<RDK::UItemData> > Data;

public: // Временные переменные
// Итератор, указывающий на текущий момент времени
map<real,vector<RDK::UItemData> >::iterator CurrentIndex;

// Момент времени начала очередной итерации
real DataStartTime;


public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NFileGenerator(void);
virtual ~NFileGenerator(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает имя файла с данными
bool SetFileName(const string &value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NFileGenerator* New(void);
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
virtual bool CheckComponentType(const NAContainer* comp) const;
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
};

}
#endif

