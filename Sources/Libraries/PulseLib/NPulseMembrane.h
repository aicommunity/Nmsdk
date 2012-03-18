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

#ifndef NPULSE_MEMBRANE_H
#define NPULSE_MEMBRANE_H

#include "../../Kernel/NBios.h"
#include "NPulseChannel.h"


namespace NMSDK {

class NPulseNeuron;

class NPulseMembrane: public NANet
{
public: // Основные свойства
// Коэффициент обратной связи
RDK::ULProperty<real,NPulseMembrane> FeedbackGain;

public: // Данные
// Значение обратной связи
RDK::ULStateProperty<real,NPulseMembrane> Feedback;

protected: // Временные переменные
// Ионные механизмы деполяризации
vector<NPulseChannel*> PosChannels;

// Ионные механизмы гиперполяризации
vector<NPulseChannel*> NegChannels;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseMembrane(void);
virtual ~NPulseMembrane(void);
// --------------------------

// --------------------------
// Методы управления временными перменными
// --------------------------
// Ионные механизмы деполяризации
size_t GetNumPosChannels(void) const;
NPulseChannel* GetPosChannel(size_t i);

// Ионные механизмы гиперполяризации
size_t GetNumNegChannels(void) const;
NPulseChannel* GetNegChannel(size_t i);
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Коэффициент обратной связи
bool SetFeedbackGain(real value);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NPulseMembrane* New(void);
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
};

}
#endif

