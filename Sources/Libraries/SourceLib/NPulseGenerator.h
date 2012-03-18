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

#ifndef NPULSE_GENERATOR_H
#define NPULSE_GENERATOR_H

#include "../BCL/NSource.h"


namespace NMSDK {

class NPulseGenerator: public NSource
{
public: // Общедоступные свойства
// Частота генерации (Гц) (Математическое ожидание)
RDK::ULProperty<real,NPulseGenerator> Frequency;

// Длительность импульса (с)
RDK::ULProperty<real,NPulseGenerator> PulseLength;

// Амплитуда импульса
RDK::ULProperty<real,NPulseGenerator> Amplitude;

// Отклонение частоты
// (Задает диапазон, не является стандартным отклонением!)
RDK::ULProperty<real,NPulseGenerator> FrequencyDeviation;

protected: // Основные свойства

public: // Временные переменные
// Счетчик импульса
RDK::ULStateProperty<RDK::UTime,NPulseGenerator> PulseCounter;

// Случайное значение текущей частоты
RDK::ULStateProperty<real,NPulseGenerator> RandomFrequency;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseGenerator(void);
virtual ~NPulseGenerator(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает частоту импульсов
bool SetFrequency(real value);

// Устанавливает длительность импульса
bool SetPulseLength(real value);

// Устанавливает амплитуду импульсов
bool SetAmplitude(real value);

// Устанавливает случайное отклонение частоты
// (Задает диапазон, не является стандартным отклонением!)
bool SetFrequencyDeviation(real value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NPulseGenerator* New(void);
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
virtual bool CheckComponentType(UEPtr<NAContainer> comp) const;
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

