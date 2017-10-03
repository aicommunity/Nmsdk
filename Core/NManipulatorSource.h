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

#ifndef NMANIPULATOR_SOURCE_H
#define NMANIPULATOR_SOURCE_H

#include "../../Nmsdk-BasicLib/Core/NSource.h"


namespace NMSDK {

class RDK_LIB_TYPE NManipulatorSource: public NSource
{
public: // Общедоступные свойства
// угол разворота ротора
UProperty<double,NManipulatorSource, ptPubParameter> Angle;
// угловая скорость
UProperty<double,NManipulatorSource, ptPubParameter> Speed;
// момент двигателя
UProperty<double,NManipulatorSource, ptPubParameter> Force;

UProperty<double,NManipulatorSource, ptPubParameter> Movement;

protected: // Основные свойства


public: // Методы
bool UpdateOutputFlag;
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NManipulatorSource(void);
virtual ~NManipulatorSource(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает угол
bool SetAngle(const double &value);
// Устанавливает скорость
bool SetSpeed(const double &value);
// Устанавливает момент
bool SetForce(const double &value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NManipulatorSource* New(void);
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

