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

#ifndef NPULSE_SYNAPSE_H
#define NPULSE_SYNAPSE_H

#include "../../Kernel/NBios.h"
#include "../BCL/NConnector.h"


namespace NMSDK {

class NPulseNeuron;

class NPulseSynapse: public NConnector
{
public: // Общедоступные свойства
// Амплитуда входных импульсов
RDK::ULProperty<real,NPulseSynapse> PulseAmplitude;

// Постоянная времени выделения медиатора
RDK::ULProperty<real,NPulseSynapse> SecretionTC;

// Постоянная времени распада медиатора
RDK::ULProperty<real,NPulseSynapse> DissociationTC;

// Коэффициент пресинаптического торможения
RDK::ULProperty<real,NPulseSynapse> InhibitionCoeff;

// Вес (эффективность синапса) синапса
RDK::ULProperty<real,NPulseSynapse> Resistance;

public: // Данные

protected: // Основные свойства

protected: // Временные переменные
// Промежуточное значение эффективности синапса
RDK::ULStateProperty<real,NPulseSynapse> PreOutput;

// Постоянные времени выделения и распада медиатора в единицах шага интегрирования
real VSecretionTC,VDissociationTC;

// Постоянная составляющая результатов вычислений
real OutputConstData;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseSynapse(void);
virtual ~NPulseSynapse(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду импульсов
bool SetPulseAmplitude(real value);

// Постоянная времени выделения медиатора
bool SetSecretionTC(real value);

// Постоянная времени распада медиатора
bool SetDissociationTC(real value);

// Коэффициент пресинаптического торможения
bool SetInhibitionCoeff(real value);

// Вес (эффективность синапса) синапса
bool SetResistance(real value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NPulseSynapse* New(void);
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
