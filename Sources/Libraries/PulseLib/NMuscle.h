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

#ifndef NMUSCLE_H
#define NMUSCLE_H

#include "../../Kernel/NBios.h"
#include "../BCL/NItem.h"
#include "../ReceiverLib/NReceptor.h"

namespace NMSDK {

//using namespace MySDK;

class NMuscle: public NANet
{
public: // Общедоступные свойства
// Коэффициенты
RDK::UCLProperty<Real,NMuscle> MulCoeffs;

RDK::UCLProperty<Real,NMuscle> Param;

// Постоянные времени
RDK::UCLProperty<Real,NMuscle> TC;

// Масса
RDK::ULProperty<real,NMuscle> Mass;

// Порог
RDK::ULProperty<real,NMuscle> Threshold;

// Величина ускорения свободного падения
RDK::ULProperty<real,NMuscle> G;

public: // Временные переменные
real y[15], yOld[15], mr[7], mrOld[7],vereteno1, vereteno2, goldgi;
real MaxActionPower;
bool FirstStep;

// Указатель на вход по длине
NReceptor *LengthInput;
/*
// Указатель на вход по внешней силе
NReceptor *ExternalForce;

// Указатели на дополнительные выходы
// Активная сила
NItem *ActivePower;

// Длина
NItem *Length;

// Веретена
NItem *Spindle1, *Spindle2;

// Сухожильный орган Гольджи
NItem *Tendon;
             */
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NMuscle(void);
virtual ~NMuscle(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду синуса
//bool SetAmplitude(real value);

// Устанавливает частоту генерации
//bool SetFrequency(real value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NMuscle* New(void);
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
// Скрытые методы управления компонентами
// --------------------------
protected:
// Выполняет завершающие пользовательские действия
// при добавлении дочернего компонента в этот объект
// Метод будет вызван только если comp был
// успешно добавлен в список компонент
virtual bool AAddComponent(UEPtr<UAContainer> comp, UEPtr<UIPointer> pointer=0);

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
virtual bool ADelComponent(UEPtr<UAContainer> comp);
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
// Апериодическое звено
real AperiodicSection(real in, real inOld, real param1, real param2);

// Порог
real CompareThreshold(real);

// мускульное сокращение
real MuscularReduction(real);

// Инерционный элемент ОС мышцы
real MuscleFeedback(real x_new, real x_old, real y_old,
					  real k, real T1, real T2);
// --------------------------
};

}
#endif

