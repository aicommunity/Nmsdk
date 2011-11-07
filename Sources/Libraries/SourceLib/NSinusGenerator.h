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

#ifndef NSINUS_GENERATOR_H
#define NSINUS_GENERATOR_H

#include "../BCL/NSource.h"


namespace NMSDK {

class NSinusGenerator: public NSource
{
public: // Общедоступные свойства
// Амплитуда синуса
RDK::ULProperty<real,NSinusGenerator> Amplitude;

// Частота генерации (Гц)
RDK::ULProperty<real,NSinusGenerator> Frequency;

protected: // Основные свойства

public: // Временные переменные
// Счетчик времени
RDK::ULProperty<real,NSinusGenerator> TimeCounter;


public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NSinusGenerator(void);
virtual ~NSinusGenerator(void);
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
virtual NSinusGenerator* New(void);
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

