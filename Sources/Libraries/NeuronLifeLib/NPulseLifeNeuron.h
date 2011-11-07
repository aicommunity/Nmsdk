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

#ifndef NPULSE_LIFE_NEURON_H
#define NPULSE_LIFE_NEURON_H

#include "../PulseLib/NPulseNeuron.h"
#include "NNeuronLife.h"

namespace NMSDK {

class NPulseLifeNeuron: public NPulseNeuron
{
public: // Параметры

public: // Данные
// Суммарный динамический вес возбуждающих связей
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryPosGd;

// Суммарный статический вес возбуждающих связей
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryPosGs;

// Суммарный результирующий вес возбуждающих связей
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryPosG;

// Суммарный динамический вес тормозных связей
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryNegGd;

// Суммарный статический вес тормозных связей
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryNegGs;

// Суммарный результирующий вес тормозных связей
RDK::ULStateProperty<real, NPulseLifeNeuron> SummaryNegG;

protected: // Временные переменные
NNeuronLife *NeuronLife;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseLifeNeuron(void);
virtual ~NPulseLifeNeuron(void);
// --------------------------

// --------------------------
// Методы доступа к временным переменным
// --------------------------
// Возвращает указатель на модель жизнеобеспечения
NNeuronLife* GetNeuronLife(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NPulseLifeNeuron* New(void);
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
// --------------------------

};

}
#endif
