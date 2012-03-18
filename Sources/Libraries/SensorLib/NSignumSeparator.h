// ===========================================================
// Version:        1.0.1
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

#ifndef NAPC_H
#define NAPC_H

#include "../../Kernel/NBios.h"
#include "../BCL/NConnector.h"


namespace NMSDK {

class NSignumSeparator: public NANet
{
public: // Общедоступные свойства
// Выделяемый знак
// может принимать значения +-1
RDK::UCLProperty<Real,NSignumSeparator> Sign;

// Множитель выходного значения
RDK::UCLProperty<Real,NSignumSeparator> Gain;

protected: // Основные свойства

protected: // Временные переменные

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NSignumSeparator(void);
virtual ~NSignumSeparator(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Выделяемый знак
bool SetSign(real value);

// Множитель выходного значения
bool SetGain(real value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NSignumSeparator* New(void);
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
