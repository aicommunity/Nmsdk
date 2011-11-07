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

#ifndef NLIFE_NET_H
#define NLIFE_NET_H

#include "../BCL/NNet.h"
#include "NNeuronLife.h"
#include "NPulseLifeNeuron.h"
#include "../PulseLib/NPulseHebbSynapse.h"

namespace NMSDK {

// Тип ансамбля нейронов
typedef vector<NPulseLifeNeuron*> NEnsemble;

// Тип связи между ансамблями
struct NEnsembleLink
{
// Ансамбль-источник сигнала
NameT In;

// Ансамбль-приемник сигнала
NameT Out;

// Мощность связи
real Power;

// ------------------------
// Операторы
// ------------------------
bool operator < (const NEnsembleLink &link);
// ------------------------
};

class NLifeNet: public NNet
{
public: // Общедоступные свойства
// Суммарная энергия сети
RDK::ULProperty<real,NLifeNet> AvailableEnergy;

// Флаг разрешающий нейронам деление
RDK::ULProperty<bool,NLifeNet> CellDivisionFlag;

// Запас энергии, по достижении которого клетка делится
RDK::ULProperty<real,NLifeNet> CellDivisionEnergy;

// Порог принятия решения об объединении нейронов в ансамбль
RDK::ULProperty<real,NLifeNet> EnsembleThreshold;

// Порог принятия решения о наличии связи между ансамблями
RDK::ULProperty<real,NLifeNet> EnsembleLinkThreshold;

// Режим отсчета порога принятия решения
// 0 - от нуля
// 1 - от среднего Gs синапсов данного нейрона
// 2 - от среднего Gs синапсов всех нейронов сети
RDK::ULProperty<int,NLifeNet> EnsembleThresholdMode;

// Интервал обсчета состояний ансамблей (в секундах)
// Если 0, то расчет ансамблей не производится
RDK::ULProperty<real,NLifeNet> EnsembleCalculationStep;

// Метод деления энергии между нейронами
// 0 - всем поровну
// 1 - приоритет у генерирующих нейронов
RDK::ULProperty<int,NLifeNet> EnergyBalanceMode;


public: // Переменные состояния
// Суммарное самочувствие нейронов сети
RDK::ULStateProperty<real,NLifeNet> SummaryFeeling;

// Суммарное расход энергии нейронами сети
RDK::ULStateProperty<real,NLifeNet> SummaryEnergy;

// Суммарный износ нейронов сети
RDK::ULStateProperty<real,NLifeNet> SummaryWearOut;

// Суммарная частота активности нейронов сети
RDK::ULStateProperty<real,NLifeNet> SummaryFrequency;

// Суммарная число живых нейронов сети
RDK::ULStateProperty<real,NLifeNet> SummaryLiveNeurons;

protected: // Данные
// Список систем жизнеобеспечения отдельных нейронов
vector<NNeuronLife*> NeuronsLife;

// Массив пар <мощность ансамбля,бета-ансамбль> нейронов
vector<pair<real, NEnsemble > > BetaEnsembles;

// Массив пар <мощность ансамбля,ансамбль> нейронов
vector<pair<real, NEnsemble > > Ensembles;

// Массив связей между ансамблями
// <Мощность связи, связь>
vector<NEnsembleLink> EnsembleLinks;

protected: // Временные переменные
// Список синапсов нейронов сети
map<NPulseLifeNeuron*,vector<NPulseHebbSynapse*> > SynapticMap;
typedef map<NPulseLifeNeuron*,vector<NPulseHebbSynapse*> >::iterator SynapticMapIterator;

int EnsembleCalculationCounter;


public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NLifeNet(void);
virtual ~NLifeNet(void);
// --------------------------

// --------------------------
// Методы управления данными
// --------------------------
// Возвращает число систем жизнеобеспечения нейронов
size_t GetNumNeuronsLife(void) const;

// Возвращает заданную систему жизнеобеспечения нейрона
NNeuronLife* GetNeuronLife(size_t i);

// Возвращает число бета-ансамблей нейронов
size_t GetNumBetaEnsembles(void) const;

// Возвращает заданный бета-ансамбль
const NEnsemble& GetBetaEnsemble(size_t i);

// Возвращает мощность заданного бета-ансамбля
real GetBetaEnsemblePower(size_t i) const;

// Возвращает число ансамблей нейронов
size_t GetNumEnsembles(void) const;

// Возвращает заданный ансамбль
const NEnsemble& GetEnsemble(size_t i);

// Возвращает мощность заданного ансамбля
real GetEnsemblePower(size_t i) const;

// Возвращает имя ансамбля по имени составляющих нейронов
NameT GetEnsembleName(size_t i) const;

// Возвращает абсолютное значение активности ансамбля
// (средняя частота всех нейронов ансамбля)
real GetEnsembleActivity(size_t i) const;

// Возвращает значение активности ансамбля
// относительно активности сети
real GetRelativeEnsembleActivity(size_t i) const;

// Возвращает число связей между ансамблями
size_t GetNumEnsembleLinks(void) const;

// Возвращает связь между ансамблями
const NEnsembleLink& GetEnsembleLink(size_t i) const;
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NLifeNet* New(void);
// --------------------------

// --------------------------
// Скрытые методы управления компонентами
// --------------------------
protected:
// Выполняет завершающие пользовательские действия
// при добавлении дочернего компонента в этот объект
// Метод будет вызван только если comp был
// успешно добавлен в список компонент
virtual bool AAddComponent(NAContainer* comp, RDK::UIPointer* pointer=0);

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
virtual bool ADelComponent(NAContainer* comp);
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

// Вычисляет ансамбли сети
bool CalcEnsembles(real threshold);

// Вычисляет связи между ансамблями сети
bool CalcEnsembleLinks(real threshold);
// --------------------------
};

}
#endif


