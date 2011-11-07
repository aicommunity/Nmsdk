// ===========================================================
// Version:        1.0.1
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:			alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NDCEngineH
#define NDCEngineH
#include "../../Kernel/NBios.h"

//---------------------------------------------------------------------------
namespace NMSDK {

/* *************************************************************************** */
class NDCEngine: public NADItem
{
public: // Общедоступные свойства
// Электромагнитный коэффициент
RDK::ULProperty<real, NDCEngine> EMFactor;

// Индуктивность
RDK::ULProperty<real, NDCEngine> Inductance;

// Сопротивление
RDK::ULProperty<real, NDCEngine> Resistance;

// Электромеханическая постоянная времени
RDK::ULProperty<real, NDCEngine> Tm;

// Передаточное число
RDK::ULProperty<real, NDCEngine> ReductionRate;

// Внешний момент
RDK::ULProperty<real, NDCEngine> OutMoment;

protected: // Данные

protected: // Временные переменные
// Ток якоря
real Current;

// ЭДС якоря
real EMF;

// Угол поворота
real Angle;

// Момент развиваемый двигателем
real Moment;

// Угловая скорость
real AngleSpeed;

// Производная момента
real DiffMoment;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NDCEngine(void);
//NDCEngine(const string &name);
virtual ~NDCEngine(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NDCEngine* New(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Электромагнитный коэффициент
bool SetEMFactor(real value);

// Индуктивность
bool SetInductance(real value);

// Сопротивление
bool SetResistance(real value);

// Электромеханическая постоянная времени
bool SetTm(real value);

// Передаточное число
bool SetReductionRate(real value);
// --------------------------

// --------------------------
// Computation methods
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool ADefault(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool ABuild(void);

// Reset computation
virtual bool AReset(void);

// Execute math. computations of current object on current step
virtual bool ACalculate(void);
// --------------------------
};
/* *************************************************************************** */


}
//---------------------------------------------------------------------------
#endif
