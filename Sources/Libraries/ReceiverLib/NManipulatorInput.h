// ===========================================================
// Version:        3.0.2
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:        alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NMANIPULATOR_INPUT_H
#define NMANIPULATOR_INPUT_H

#include "../BCL/NSource.h"


namespace NMSDK {

class NManipulatorInput: public NSource
{
public: // Общедоступные свойства
// подаваемое напряжение
RDK::ULProperty<real,NManipulatorInput> Voltage;

protected: // Основные свойства


public: // Методы
bool UpdateOutputFlag;
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NManipulatorInput(void);
virtual ~NManipulatorInput(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает подаваемое напряжение
bool SetVoltage(real value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NManipulatorInput* New(void);
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
protected:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool ADefault(void);


// Сброс процесса счета.
virtual bool AReset(void);

// Выполняет расчет этого объекта
virtual bool ACalculate(void);
// --------------------------
};

}
#endif

