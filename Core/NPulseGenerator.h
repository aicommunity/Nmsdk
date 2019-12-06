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

#include "../../Nmsdk-BasicLib/Core/NSource.h"

namespace NMSDK {

class RDK_LIB_TYPE NPulseGenerator: public NSource
{
public: // Параметры
// Частота генерации (Гц) (Математическое ожидание)
RDK::ULProperty<double,NPulseGenerator> Frequency;

// Длительность импульса (с)
RDK::ULProperty<double,NPulseGenerator> PulseLength;

// Амплитуда импульса
RDK::ULProperty<double,NPulseGenerator> Amplitude;

// Отклонение частоты
// (Задает диапазон, не является стандартным отклонением!)
RDK::ULProperty<double,NPulseGenerator> FrequencyDeviation;

// Интервал времени оценки частоты генерации
RDK::ULProperty<double,NPulseGenerator> AvgInterval;

public: // Переменные состояния
// Счетчик импульса
RDK::ULProperty<int,NPulseGenerator,ptPubState> PulseCounter;

// Случайное значение текущей частоты
RDK::ULProperty<double,NPulseGenerator,ptPubState> RandomFrequency;

// Средняя частота за заданный интервал времени
RDK::UCLProperty<list<double>,NPulseGenerator,ptPubState> AvgFrequencyCounter;

protected:

double OldFrequency;

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
bool SetFrequency(const double &value);

// Устанавливает длительность импульса
bool SetPulseLength(const double &value);

// Устанавливает амплитуду импульсов
bool SetAmplitude(const double &value);

// Устанавливает случайное отклонение частоты
// (Задает диапазон, не является стандартным отклонением!)
bool SetFrequencyDeviation(const double &value);
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
virtual bool CheckComponentType(UEPtr<UContainer> comp) const;
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

