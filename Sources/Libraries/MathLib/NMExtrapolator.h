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

#ifndef NMExtrapolatorH
#define NMExtrapolatorH

#include "../../Kernel/NBios.h"
#include "rdk.h"
//---------------------------------------------------------------------------

namespace NMSDK {

class NMExtrapolator: public NANet
{
public: // Общедоступные свойства
// Время прогноза, с
RDK::ULProperty<RDK::UTime,NMExtrapolator> PredictionTime;

// Число уровней сети
RDK::ULProperty<size_t,NMExtrapolator> NumLevels;

protected: // Внутренние данные
// Коэффициенты треугольника паскаля
vector<size_t> PascalCoeffs;

protected: // Временные переменные
// История сигнала
RDK::UQueue<Real> History;
//vector<Real> History2;

// Счетчик пополнения истории
int HistoryCounter;

public:
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NMExtrapolator(void);
virtual ~NMExtrapolator(void);
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Время прогноза, с
bool SetPredictionTime(RDK::UTime ptime);

// Число уровней сети
bool SetNumLevels(size_t value);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NAContainer* New(void);
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
// Скрытые методы счета
// --------------------------
protected:
// Вычисляет коэффициенты треугольника паскаля
void CalcPascalCoeff(size_t level, vector<size_t> &coeffs);
// --------------------------
};

}

#endif
