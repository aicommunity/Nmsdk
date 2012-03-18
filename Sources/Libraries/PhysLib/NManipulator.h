// ===========================================================
// Version:        1.0.0
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

#ifndef NManipulatorH
#define NManipulatorH
#include "../../Kernel/NBios.h"

//---------------------------------------------------------------------------
namespace NMSDK {

/* *************************************************************************** */
class NManipulator: public NANet
{
public: // Общедоступные свойства
// Электромагнитный коэффициент
RDK::ULProperty<real, NManipulator> EMFactor;

// Индуктивность
RDK::ULProperty<real, NManipulator> Inductance;

// Сопротивление
RDK::ULProperty<real, NManipulator> Resistance;

protected: // Данные
// Отрисовка состояния манипулятора
//RDK::UBitmap StatePicture;

protected: // Временные переменные
// Ток якоря
real Current;

// Класс рисования
RDK::UGraphics Graphics;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NManipulator(void);
virtual ~NManipulator(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NManipulator* New(void);
// --------------------------

// --------------------------
// Методы управления данными
// --------------------------
// Отрисовка состояния манипулятора
//const RDK::UBitmap& GetStatePicture(void) const;
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
