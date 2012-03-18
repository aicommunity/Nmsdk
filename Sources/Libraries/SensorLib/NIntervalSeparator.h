// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NINTERVAL_SEPARATOR_H
#define NINTERVAL_SEPARATOR_H

#include "../../Kernel/NBios.h"
#include "../BCL/NConnector.h"


namespace NMSDK {

class NIntervalSeparator: public NANet
{
public: // Общедоступные свойства
// Нижняя граница выделяемого интервала
RDK::UCLProperty<Real,NIntervalSeparator> MinRange;

// Верхняя граница выделяемого интервала
RDK::UCLProperty<Real,NIntervalSeparator> MaxRange;

// Режим разделения
// 0 - если значение попадает в заданный интервал, то оно и возврашается, иначе 0
// 1 - если значение попадает в заданный интервал, то возврашается значение минус
// нижняя граница интервала, иначе 0
// 2 - если значение превышает нижнюю границу, то оно и возвращается, иначе 0
// 3 - если значение ниже верхней границы, то оно и возвращается, иначе 0
// 4 - если значение превышает нижнюю границу, то возврашается значение минус
// 5 - если значение превышает нижнюю границу, то возврашается значение минус
// нижняя граница интервала;если значение превышает верхнюю границу, то возвращается
// верхняя граница минус нижняя граница
RDK::UCLProperty<vector<int>,NIntervalSeparator> Mode;

// Множитель выходного значения
RDK::UCLProperty<Real,NIntervalSeparator> Gain;



protected: // Основные свойства

protected: // Временные переменные

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NIntervalSeparator(void);
virtual ~NIntervalSeparator(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Нижняя граница выделяемого интервала
bool SetMinRange(real value);

// Верхняя граница выделяемого интервала
bool SetMaxRange(real value);

// Режим разделения
bool SetMode(int value);

// Множитель выходного значения
bool SetGain(real value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NIntervalSeparator* New(void);
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
