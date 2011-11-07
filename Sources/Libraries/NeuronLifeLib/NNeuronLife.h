// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NNEURON_LIFE_H
#define NNEURON_LIFE_H

#include "../../Kernel/NBios.h"
#include "../MathLib/NSum.h"


namespace NMSDK {

class NNeuronLife: public NADItem
{
public: // Общедоступные свойства
// Статический порог нейрона
RDK::ULProperty<real,NNeuronLife> Threshold;

// Критическое значение энергии, используемое для расчета к-та мотивации
// тормозных синапсов
RDK::ULProperty<real,NNeuronLife> CriticalEnergy;

//переменные для расчета Износа

// Ожидаемое значение максимального градиента выхода нейрона
RDK::ULProperty<real,NNeuronLife> MaxPotentialGradient;

RDK::ULProperty<real,NNeuronLife> WearOutConstPositive;

RDK::ULProperty<real,NNeuronLife> WearOutConstNegative;

RDK::ULProperty<real,NNeuronLife> Kw;

//переменные для расчета самочувствия
RDK::ULProperty<real,NNeuronLife> Emax;

RDK::ULProperty<real,NNeuronLife> En;

RDK::ULProperty<real,NNeuronLife> Kq;

//переменные для расчета запаса энергии
RDK::ULProperty<real,NNeuronLife> Ee0;
RDK::ULProperty<real,NNeuronLife> Es;
RDK::ULProperty<real,NNeuronLife> Eh0;
RDK::ULProperty<real,NNeuronLife> Econst;
RDK::ULProperty<real,NNeuronLife> Ecr;
RDK::ULProperty<real,NNeuronLife> WearOutcr;
RDK::ULProperty<real,NNeuronLife> EnergyWearOutCritical;
//RDK::ULProperty<real,NNeuronLife> E;    //?
//RDK::ULProperty<real,NNeuronLife> N;   //?
RDK::ULProperty<real,NNeuronLife> EyConst;
RDK::ULProperty<real,NNeuronLife> EyBonusPos;
RDK::ULProperty<real,NNeuronLife> EyBonusNeg;

// Номинальный предел усвояемости энергии
RDK::ULProperty<real,NNeuronLife> EnergyComprehensibility;



//Переменные для расчета порога
RDK::ULProperty<real,NNeuronLife> Kdp;
RDK::ULProperty<real,NNeuronLife> Pdmax;
RDK::ULProperty<real,NNeuronLife> Qd;
RDK::ULProperty<real,NNeuronLife> Khp0;
RDK::ULProperty<real,NNeuronLife> Khp1;

RDK::ULProperty<real,NNeuronLife> Qsummax;

// Ожидаемый бонус к подаче энергии
RDK::ULProperty<real,NNeuronLife> EnergyBonus;

public: // Данные с внешним управлением
// Запас Энергии
RDK::ULStateProperty<real,NNeuronLife> Energy;


protected: // Временные переменные
// Износ нейрона
RDK::ULStateProperty<real,NNeuronLife> WearOut;

// Порог нейрона
RDK::ULStateProperty<real,NNeuronLife> ThresholdLife;

RDK::ULStateProperty<real,NNeuronLife> ThresholdWearOut;

RDK::ULStateProperty<real,NNeuronLife> ThresholdFeel;

//Самочувствие
RDK::ULStateProperty<real,NNeuronLife> Feel;

RDK::ULStateProperty<real,NNeuronLife> Qsum;

RDK::ULStateProperty<real,NNeuronLife> Esum;

//RDK::ULStateProperty<real,NNeuronLife> UsumOld;

//RDK::ULStateProperty<real,NNeuronLife> UsumProizv;

RDK::ULStateProperty<real,NNeuronLife> EsumOld;

RDK::ULStateProperty<real,NNeuronLife> EsumProizv;

// Прибавка энергии за шаг
RDK::ULStateProperty<real,NNeuronLife> Ea;

// Расход энергии за шаг на генерацию импульса
RDK::ULStateProperty<real,NNeuronLife> Ey;

// Расход энергии за шаг на поддержание запаса энергии
RDK::ULStateProperty<real,NNeuronLife> Ee;

// Расход энергии за шаг на противодействие износу
RDK::ULStateProperty<real,NNeuronLife> Eh;

// Производная - прибавка энергии за шаг
RDK::ULStateProperty<real,NNeuronLife> dEa;

// Производная - расход энергии за шаг на генерацию импульса
RDK::ULStateProperty<real,NNeuronLife> dEy;

// Производная - расход энергии за шаг на поддержание запаса энергии
RDK::ULStateProperty<real,NNeuronLife> dEe;

// Производная - расход энергии за шаг на противодействие износу
RDK::ULStateProperty<real,NNeuronLife> dEh;

// ПРоизводная текущего запаса энергии
RDK::ULStateProperty<real,NNeuronLife> dE;



RDK::ULStateProperty<real,NNeuronLife> Usum;

// Суммарный потенциал
//RDK::ULStateProperty<real,NNeuronLife> NeuralPotential;

// Промежуточное значение потенциала
//RDK::ULStateProperty<real,NNeuronLife> PrePotential;

// Флаг наличия генерации
//RDK::ULStateProperty<int,NNeuronLife> PulseCounter;

public: // Указатели на внутренние компоненты
// Сумматор внешнего EnergyBonus
RDK::UEPointer<NSum, NNeuronLife> ExternalEnergyBonus;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NNeuronLife(void);
virtual ~NNeuronLife(void);
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
bool SetThreshold(real value);

// Устанавливает ожидаемое значение максимального градиента выхода нейрона
bool SetMaxPotentialGradient(real value);

bool SetEmax(real value);

bool SetEn(real value);

bool SetPdmax(real value);

bool SetQsummax(real value);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NNeuronLife* New(void);
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
virtual bool CheckComponentType(const NAContainer* comp) const;
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

virtual bool ACalcWearOut(void);

virtual bool ACalcThresholdLife(void);

virtual bool ACalcEnergy(void);

virtual bool ACalcFeel(void);

real FeelDiff(real kq, real ediff, real en);

//virtual bool ACalcEnergy(void);
};

}
#endif
