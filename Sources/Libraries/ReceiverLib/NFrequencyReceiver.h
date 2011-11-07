// ===========================================================
// Version:        3.0.2
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NFrequencyReceiverH
#define NFrequencyReceiverH
#include "../BCL/NReceiver.h"

//---------------------------------------------------------------------------
namespace NMSDK {

/* *************************************************************************** */
class NFrequencyReceiver: public NReceiver
{
public: // Общедоступные свойства
// Наблюдаемый интервал частот
RDK::ULProperty<real, NFrequencyReceiver> LeftRange,RightRange;

// Шаг по частоте
RDK::ULProperty<real, NFrequencyReceiver> FrequencyStep;

protected: // Данные
// Суммарное число импульсов
RDK::ULProperty<size_t, NFrequencyReceiver> PulseCounter;

// Буфер результатов
Real XResults,YResults;

protected: // Временные переменные
real PrevPulseStartTime;
real PrevPulseStopTime;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NFrequencyReceiver(void);
virtual ~NFrequencyReceiver(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NFrequencyReceiver* New(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает левую границу наблюдаемого интервала частот
bool SetLeftRange(real range);

// Устанавливает правую границу наблюдаемого интервала частот
bool SetRightRange(real range);

// Устанавливает шаг по частоте
bool SetFrequencyStep(real step);
// --------------------------

// --------------------------
// Watch results control methods
// --------------------------
public:
// Return number of results points
size_t GetResultsSize(void) const;

// Return iterator pointed to farthest X result
const Real& GetXResult(void) const;
real GetXResult(int i) const;

// Return iterator pointed to farthest Y result
const Real& GetYResult(void) const;
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
