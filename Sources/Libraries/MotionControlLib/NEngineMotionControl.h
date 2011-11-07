/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		1.0.0

This file - part of the project: NMSDK

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */
#ifndef NEngineMotionControlH
#define NEngineMotionControlH

#include "../Kernel/NBios.h"
#include "../Libraries/ReceiverLib/NReceptor.h"

namespace NMSDK {

class NEngineMotionControl: public NANet
{
public: // Публичные свойства
// Число управляющих элементов
RDK::ULProperty<size_t, NEngineMotionControl> NumMotionElements;

// Режим формирования сети
// 0 - Signum
// 1 - Range
// 2 - Branched Range
// 3 - Branched Range Crosslinks
// 4 - Branched Ind. Range
// 5 - Branched Ind. Range Crosslinks
RDK::ULProperty<int, NEngineMotionControl> CreationMode;

// Имя класса управляющего элемента
RDK::ULProperty<NameT, NEngineMotionControl> MotionElementClassName;

// Диапазон афферентных нейронов по каналу Ia
RDK::ULProperty<real, NEngineMotionControl> IaMin;
RDK::ULProperty<real, NEngineMotionControl> IaMax;

// Диапазон афферентных нейронов по каналу Ib
RDK::ULProperty<real, NEngineMotionControl> IbMin;
RDK::ULProperty<real, NEngineMotionControl> IbMax;

// Диапазон афферентных нейронов по каналу II
RDK::ULProperty<real, NEngineMotionControl> IIMin;
RDK::ULProperty<real, NEngineMotionControl> IIMax;

protected: // Временные переменные
vector<vector<NReceptor*> > receptor;


public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NEngineMotionControl(void);
virtual ~NEngineMotionControl(void);
// --------------------------

// --------------------------
// Методы управления параметрами
// --------------------------
protected:
// Число управляющих элементов
bool SetNumMotionElements(size_t value);

// Режим формирования сети
bool SetCreationMode(int value);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
public:
// Выделяет память для новой чистой копии объекта этого класса
virtual NEngineMotionControl* New(void);
// --------------------------

// --------------------------
// Proctected computation methods
// --------------------------
protected:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool ADefault(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool ABuild(void);

// Reset computation
virtual bool AReset(void);

// Execute math. computations of current object on current step
virtual bool ACalculate(void);
// --------------------------

// --------------------------
// Методы управления счетом
// --------------------------
public:
// Создает объект с желаемой структурой в соответствии с CreationMode
virtual bool Create(void);
// --------------------------

// --------------------------
// Вспомогательные методы
// --------------------------
protected:
// Формируем сеть управления двигателем с разделением информационного потока с датчиков
// на две полосы по знаку
NANet* CreateEngineControlSignumAfferent(void);

// Формируем сеть управления двигателем c разделением информационного потока с датчиков
// на полосы по амплитуде
NANet* CreateEngineControlRangeAfferent(bool crosslinks=false, bool crossranges=true);
// --------------------------

};

}
#endif
