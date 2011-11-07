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

#ifndef NRECEPTOR_H
#define NRECEPTOR_H

#include "../BCL/NSource.h"


namespace NMSDK {

class NReceptor: public NSource
{
public: // Общедоступные свойства
// Коэффициент усиления входного сигнала
RDK::ULProperty<real,NReceptor> Gain;

// Рабочий диапазон входного сигнала
RDK::ULProperty<real,NReceptor> MinInputRange, MaxInputRange;

// Рабочий диапазон выходного сигнала
RDK::ULProperty<real,NReceptor> MinOutputRange, MaxOutputRange;

// Коэффициент масштабирования для режима 2
RDK::ULProperty<real,NReceptor> ExpCoeff;

// Слагаемое для режима 1
RDK::ULProperty<real,NReceptor> SumCoeff;

// Постоянная времени забывания границ входного диапазона
RDK::ULProperty<real,NReceptor> InputAdaptationArrestingTC;


// Режим адаптации диапазона входного сигнала
// 0 - без адаптации
// 1 - постоянное расширение диапазона
// 2 - расширение с забыванием, с постояной времени InputAdaptationArrestingTC
RDK::ULProperty<int,NReceptor> InputAdaptationMode;

// Режим адаптации диапазона входного сигнала
// 0 - без адаптации
// 1 - экспоненциальное преобразование входного сигнала x
// в интервал [0;Gain] y=(SumCoeff-exp(-ExpCoeff*x))*Gain
// 2 - аналогично 1, но формула y=exp(-Kx)*Gain
// 3 - аналогично 1, ExpCoeff вычисляется автоматически
// 4 - адаптация по формуле y=Gain*(1.0+input);
RDK::ULProperty<int,NReceptor> OutputAdaptationMode;



protected: // Основные свойства

protected: // Временные переменные
real InputRange;
real OutputRange;



public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NReceptor(void);
virtual ~NReceptor(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Коэффициент усиления входного сигнала
bool SetGain(real value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NReceptor* New(void);
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

