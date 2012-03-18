// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:        http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NCRSampleH
#define NCRSampleH

#include "../Kernel/NBios.h"
#include "rdk.h"

//---------------------------------------------------------------------------
namespace NMSDK {

//using namespace RDK;

class NCRSample: public NANet
{
public: // Общедоступные свойства
// Размер выходного вектора выборки
RDK::ULProperty<size_t, NCRSample> VectorSize;

// Размер выборки
RDK::ULProperty<size_t, NCRSample> SampleSize;

// Режим работы
// 0 - Распознавание (входы объединяются в единый вектор выхода)
// 1 - Обучение (возвращается вектор выхода из обучающей базы)
RDK::ULProperty<int, NCRSample> Mode;

// Текущий элемент выборки
RDK::ULProperty<int, NCRSample> CurrentSample;

protected: // Данные состояний
// Массив выборки
//RDK::UCLStateProperty<vector<NIOData>, NCRSample> SampleData;
vector<pair<RDK::UItemData,int> > SampleData;

public:
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRSample(void);
~NCRSample(void);
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Текущий элемент выборки
bool SetCurrentSample(int value);

// Изменение размера выборки
bool SetSampleSize(size_t value);

// Изменение размера вектора выборки
bool SetVectorSize(size_t value);
// --------------------------

// --------------------------
// Методы управления выборкой
// --------------------------
// Пополняет выборку текущим вектором входов
bool Add(int class_index);

// Удаляет заданный элемент вектора входов по индекссу
bool Del(size_t index);

// Очищает выборку
void Clear(void);

// Возвращает индекс класса текущего вектора обучающей выборки
int GetCurrentClassIndex(void) const;

// Возвращает массив обучающей выборки
const vector<pair<RDK::UItemData,int> >& GetSampleData(void) const;
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

// Выполняет расчет этого объекта на текущем шаге.
virtual bool ACalculate(void);
// --------------------------
};

}
//---------------------------------------------------------------------------
#endif
