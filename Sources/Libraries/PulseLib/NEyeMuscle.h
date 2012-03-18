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

#ifndef NEYEMUSCLE_H
#define NEYEMUSCLE_H

#include "../../Kernel/NBios.h"

namespace NMSDK {

//using namespace MySDK;

class NEyeMuscle: public NANet
{
public: // Общедоступные свойства
// Коэффициенты
RDK::UCLProperty<Real,NEyeMuscle> MulCoeffs;

RDK::ULProperty<real,NEyeMuscle> K;

// Постоянные времени
RDK::UCLProperty<Real,NEyeMuscle> TC;

public: // Временные переменные
Real P1,P2,P3,L;

// Порог
Real Threshold;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NEyeMuscle(void);
virtual ~NEyeMuscle(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду синуса
bool SetAmplitude(real value);

// Устанавливает частоту генерации
bool SetFrequency(real value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NEyeMuscle* New(void);
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
// Дополнительные скрытые методы управления счетом
// --------------------------
protected:
// мускульное сокращение
real MuscularReduction(size_t k,real in);

// Пороговая функция
void ThresholdCount(size_t k);
// --------------------------
};

}
#endif

