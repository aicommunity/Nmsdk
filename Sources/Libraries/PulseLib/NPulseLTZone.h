// ===========================================================
// Version:        3.0.3
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

#ifndef NPULSE_LTZONE_H
#define NPULSE_LTZONE_H

#include "../../Kernel/NBios.h"


namespace NMSDK {

class NPulseNeuron;

class NPulseLTZone: public NANet
{
public: // Общедоступные свойства
// Постоянная времени
RDK::ULProperty<real,NPulseLTZone> TimeConstant;

// Порог нейрона
RDK::ULProperty<real,NPulseLTZone> Threshold;

// Амплитуда импульсов
RDK::ULProperty<real,NPulseLTZone> PulseAmplitude;

// Длительность импульса
RDK::ULProperty<real,NPulseLTZone> PulseLength;

// Интервал времени оценки частоты генерации
RDK::ULProperty<real,NPulseLTZone> AvgInterval;

public: // Данные
// Нейрон владелец мембраны канала
NPulseNeuron* Neuron;

protected: // Основные свойства

protected: // Временные переменные
// Суммарный потенциал
RDK::ULStateProperty<real,NPulseLTZone> NeuralPotential;

// Промежуточное значение потенциала
RDK::ULStateProperty<real,NPulseLTZone> PrePotential;

// Флаг наличия генерации
RDK::ULStateProperty<int,NPulseLTZone> PulseCounter;

// Средняя частота за заданный интервал времени
RDK::UCLStateProperty<list<real>,NPulseLTZone> AvgFrequencyCounter;

// Признак текущей генерации импульса
RDK::ULStateProperty<bool,NPulseLTZone> PulseFlag;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseLTZone(void);
virtual ~NPulseLTZone(void);
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает значение постоянной времени
bool SetTimeConstant(real value);

// Устанавливает порог нейрона
bool SetThreshold(real value);

// Устанавливает амплитуду импульсов
bool SetPulseAmplitude(real value);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NPulseLTZone* New(void);
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
virtual bool CheckComponentType(UEPtr<UAContainer> comp) const;
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
