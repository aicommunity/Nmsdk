// ===========================================================
// Version:        3.0.3
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

#ifndef NCRDirectCompareH
#define NCRDirectCompareH

#include "NACRClassifier.h"

namespace NMSDK {

class NCRDirectCompare: public NACRClassifier
{
public: // Общедоступные свойства
// Число входов сети
//RDK::ULProperty<size_t, NCRDirectCompare> NumInputs;

// Порог распознавания по максимуму суммы превышения
// в процентах от максимума входов (0,1)
RDK::ULProperty<real,NCRDirectCompare> MaxRecThreshold;

RDK::ULProperty<real,NCRDirectCompare> MinRecThreshold;

RDK::ULProperty<real,NCRDirectCompare> MiddleRecThreshold;

RDK::ULProperty<real,NCRDirectCompare> AbsoluteRecThreshold;

// Минимум разности достоверного результата (по разности двух максимумов)
RDK::ULProperty<real,NCRDirectCompare> ReliabilityDistance;

// Порог проверки достоверности результата по абсолютному значению максимума
RDK::ULProperty<real,NCRDirectCompare> ReliabilityValue;

// Тип распознавания
// 0 - по максимуму подобия по всей выборке
// 1 - по максимуму суммы превышения плавающего порога по всей выборке
// 2 - по максимуму суммы превышения фиксированного порога по всей выборке
// 3 - по числу превышений фиксированного порога по всей выборке
// 4 - аналогично 1 но с 2 уровнями работы
// 		выше max - по узкой полосе
//		ниже max - по широкой полосе
// 5 - Комплексный алгоритм
// 6 - Алгоритм по 5 максимумам
// 10 - ретрансляция входов на выход
RDK::ULProperty<int,NCRDirectCompare> RecognitionType;

protected: // Данные модели
//public:
// Ожидаемые вектора
vector<vector<vector<real> > > Samples;

// Вектор входов сети
//vector<real> Inputs;

// Вектор оригинальных выходов слоев сети
vector<real> NativeOutput;

protected: // Данные и параметры обучения сети

protected: // Временные переменные


public:
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRDirectCompare(void);
~NCRDirectCompare(void);
// --------------------------

protected:
// -----------------------------
// Методы управления общедоступными свойствами
// -----------------------------
// Устанавливает число входов всех скрытых слоев
//bool SetNumInputs(size_t numinputs);

// Порог распознавания по максимуму суммы превышения
bool SetMaxRecThreshold(real value);
// -----------------------------

// -----------------------------
// Методы доступа к данным модели
// -----------------------------
public:
// Вектор выборки
real GetSamples(int i, int j, int k) const;

// Вектор оригинальных выходов слоев сети
const vector<real>& GetNativeOutput(void) const;

// Вектор входов
//const vector<real>& GetInputs(void) const;
// -----------------------------

// ------------------------
// Методы счета
// ------------------------
public:
// Загружает настройки весов из файла с именем 'name'
virtual bool AFileLoad(fstream &file);

// Сохраняет настройки весов в файл с именем 'name'
virtual bool AFileSave(fstream &file);
// ------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual RDK::UAContainer* New(void);
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
protected:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool ACRDefault(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool ACRBuild(void);

// Сброс процесса счета.
virtual bool ACRReset(void);

// Выполняет расчет этого объекта на текущем шаге.
virtual bool ACRCalculate(void);
// --------------------------

// --------------------------
// Скрытые методы обучения сети
// --------------------------
protected:
// Сброс настроек обучение в исходное состояние
virtual void AResetTraining(void);

// Однократное обучение на заданном примере
virtual real ATrain(size_t exp_class);
// --------------------------

// ------------------------
// Скрытые методы счета
// ------------------------
public:
// Устанавливает значения входного вектора для распознавания
//virtual bool SetInput(const Real &input);
// ------------------------
};

}

//---------------------------------------------------------------------------
#endif
