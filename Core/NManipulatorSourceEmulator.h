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

#ifndef NMANIPULATOR_SOURCE_EMULATOR_H
#define NMANIPULATOR_SOURCE_EMULATOR_H

#include "NManipulatorSource.h"


namespace NMSDK {

class RDK_LIB_TYPE NManipulatorSourceEmulator: public NManipulatorSource
{
public: // Общедоступные свойства

protected: // Основные свойства


public: // Методы

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NManipulatorSourceEmulator(void);
virtual ~NManipulatorSourceEmulator(void);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NManipulatorSourceEmulator* New(void);
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

