// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NPAC_H
#define NPAC_H

#include "../BCL/NConnector.h"


namespace NMSDK {

class NPac: public NADItem
{
public: // Общедоступные свойства
// Амплитуда входных импульсов
RDK::UCLProperty<vector<Real>,NPac> PulseAmplitude;

// Постоянная времени выделения медиатора
RDK::UCLProperty<vector<Real>,NPac> SecretionTC;

// Постоянная времени распада медиатора
RDK::UCLProperty<vector<Real>,NPac> DissociationTC;

// Коэффициент усиления
RDK::UCLProperty<vector<Real>,NPac> Gain;

protected: // Основные свойства

protected: // Временные переменные
// Промежуточное значение эффективности синапса
RDK::UCLProperty<vector<Real>,NPac> PreOutput;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPac(void);
virtual ~NPac(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду импульсов
bool SetPulseAmplitude(vector<Real> value);

// Постоянная времени выделения медиатора
bool SetSecretionTC(vector<Real> value);

// Постоянная времени распада медиатора
bool SetDissociationTC(vector<Real> value);

// Усиление
bool SetGain(vector<Real> value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NPac* New(void);
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
