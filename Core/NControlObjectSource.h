// ===========================================================
// Version:        3.0.2
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:        alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NCONTROL_OBJECT_SOURCE_H
#define NCONTROL_OBJECT_SOURCE_H

#include "../../Nmsdk-BasicLib/Core/NSource.h"


namespace NMSDK {

/// Deprecated.
class RDK_LIB_TYPE NControlObjectSource: public NSource
{
public: // Общедоступные свойства
// Замена индексов выходов ОУ
// индекс массива - индеск выхода ОУ, значение ячейки массива - индекс выхода
// этого источника
RDK::UProperty<MDVector<int>,NControlObjectSource, ptPubParameter> DataIndexes;

// смещение данных с датчиков ОУ
RDK::UProperty<MDMatrix<double>,NControlObjectSource, ptPubParameter> DataShift;

// Умножение выходных данных
RDK::UProperty<MDMatrix<double>,NControlObjectSource, ptPubParameter> DataMul;

protected: // Основные свойства
// Входные данные
RDK::UProperty<MDMatrix<double>,NControlObjectSource, ptPubInput> Input;

// Выходные данные
RDK::UProperty<MDMatrix<double>,NControlObjectSource, ptPubOutput> Output;


public: // Методы
bool UpdateOutputFlag;
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NControlObjectSource(void);
virtual ~NControlObjectSource(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает угол
bool SetDataShift(const MDMatrix<double> &value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NControlObjectSource* New(void);
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
protected:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool ADefault(void);


// Сброс процесса счета.
virtual bool AReset(void);

// Выполняет расчет этого объекта
virtual bool ACalculate(void);
// --------------------------
};

}
#endif

