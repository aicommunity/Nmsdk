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

#ifndef NPULSE_NEURON_H
#define NPULSE_NEURON_H

#include "../BCL/NNeuron.h"
#include "NPulseLTZone.h"
#include "../SourceLib/NConstGenerator.h"
#include "NPulseMembrane.h"

namespace NMSDK {

class NPulseNeuron: public NNeuron
{
public: // Статистика
// Число связей организованных этим нейроном на других (и себе)
RDK::ULStateProperty<real,NPulseNeuron> NumActiveOutputs;

// Число возбуждающих связей организованных другими нейронами на этом
RDK::ULStateProperty<real,NPulseNeuron> NumActivePosInputs;

// Число тормозных связей организованных другими нейронами на этом
RDK::ULStateProperty<real,NPulseNeuron> NumActiveNegInputs;

protected: // Временные переменные
//NPulseLTZone *LTZone;

public:
RDK::UEPointer<NPulseLTZone,NPulseNeuron> LTZone;

NConstGenerator *PosGenerator,*NegGenerator;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseNeuron(void);
virtual ~NPulseNeuron(void);
// --------------------------

// --------------------------
// Методы доступа к временным переменным
// --------------------------
// Возвращает указатель на модель низкопороговой зоны
NPulseLTZone* GetLTZone(void);

// Возвращает указатель на модель источника возбуждаюшего потенциала
NConstGenerator* GetPosGenerator(void);

// Возвращает указатель на модель источника тормозного потенциала
NConstGenerator* GetNegGenerator(void);
// --------------------------

// --------------------------
// Методы управления структурой объекта
// --------------------------
// Удлинняет заданный участок мембраны, добавляя к нему новый участок мембраны,
// и переключая входы заданного участка на входы нового
// Возвращает указатель на созданный участок
NPulseMembrane* ElongateDendrite(const UId &id, bool feedback=false);

// Разветвляет заданный участок мембраны, добавляя к точке его подключения
// дополнительно новый участок мембраны
// Возвращает указатель на созданный участок
NPulseMembrane* BranchDendrite(const UId &id, bool feedback=false);

// Удаляет заданный участок мембраны
// Если full == true, то удаляет и все другие участки, подключенные к нему
// Иначе перенаправляет связи со входов на свои выходы
bool EraseDendrite(const UId &id);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NPulseNeuron* New(void);
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
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
virtual bool CheckComponentType(UEPtr<NAContainer> comp) const;
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
