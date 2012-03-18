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

#ifndef NCRDistanceH
#define NCRDistanceH

#include "NACRClassifier.h"

namespace NMSDK {

class NCRDistance: public NACRClassifier
{
public: // Общедоступные свойства
// Число входов сети
RDK::ULProperty<size_t, NCRDistance> NumLayerInputs;

// Флаг разрешения отсекания пиков выборки по дисперсии
// 0 - не отсекать
// 1 - заменять нулями
// 2 - заменять средними
RDK::ULProperty<int, NCRDistance> DispersionCroppingFlag;

// Максимально допустимое значение дисперсии
RDK::ULProperty<real, NCRDistance> MaxDispersionValue;

// Число максимальных компонент
RDK::UCLProperty<vector<size_t>,NCRDistance> NumMaxElements;

// Минимальное допустимое расстояние между компонентами
RDK::ULProperty<real,NCRDistance> MinElementsDistance;

// Порог распознавания по максимуму суммы превышения
// в процентах от максимума входов (0,1)
RDK::ULProperty<real,NCRDistance> MaxRecThreshold;

RDK::ULProperty<real,NCRDistance> MinRecThreshold;

// Тип распознавания
// 0 - по максимуму подобия по всей выборке
// 1 - по минимуму расстояния по всей выборке
// 2 - по среднему расстоянию для класса
// 3 - по среднему расстоянию по максимальным признакам для класса
// 4 - аналогично 3, но с весами для каждого признака
// 5 - по максимуму суммы превышения плавающего порога по всей выборке
// 6 - по максимуму суммы превышения фиксированного порога по всей выборке
// 7 - по числу превышений фиксированного порога по всей выборке
RDK::ULProperty<int,NCRDistance> RecognitionType;


protected: // Данные модели
//public:
// Исходные ожидаемые вектора
vector<vector<vector<real> > > PreSamples;

// Ожидаемые вектора
vector<vector<vector<real> > > Samples;

// Среднее ожидаемых векторов
vector<vector<real> > MiddleSamples;

// Дисперсия отклонений
vector<vector<real> > Dispersion;

// Список индексов средних
vector<vector<int> > MaxMiddleIndex;

// Вектор входов сети
vector<real> Inputs;

// Вектор оригинальных выходов слоев сети
vector<real> NativeOutput;

public:
// Список весов элементов вектора
// выборочно для класса
vector<vector<real> > Weights;

// Список максимальных компонент вектора
// выборочно для класса
vector<vector<real> > MaxClassElements;

// Список индексов максимальных компонент вектора
// выборочно для класса
vector<vector<size_t> > MaxClassElementsIndex;

// Список индексов запрещенных элементов
vector<int> DispersionBanIndexes;


protected: // Данные и параметры обучения сети
// Номер текущего примера в обучающей выборке
//size_t CurrentTrainingSample;

protected: // Временные переменные


public:
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRDistance(void);
~NCRDistance(void);
// --------------------------

protected:
// -----------------------------
// Методы управления общедоступными свойствами
// -----------------------------
// Устанавливает число входов всех скрытых слоев
bool SetNumLayerInputs(size_t numinputs);

// Устанавливает скорость обучения сети
bool SetTrainingRate(real tr);

// Порог распознавания по максимуму суммы превышения
bool SetMaxRecThreshold(real value);
// -----------------------------

// -----------------------------
// Методы доступа к данным модели
// -----------------------------
public:
// Вектор математического ожидания
real GetMiddleSamples(int i, int j) const;

// Вектор выборки
real GetSamples(int i, int j, int k) const;

// Вектор исходных данных выборки
real GetPreSamples(int i, int j, int k) const;

// Дисперсия отклонений
real GetDispersion(int i, int j) const;

// Стандартное отклонение
real GetSDeviation(int i, int j) const;

// Вектор оригинальных выходов слоев сети
const vector<real>& GetNativeOutput(void) const;

// Вектор входов
const vector<real>& GetInputs(void) const;
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
virtual NAContainer* New(void);
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

// Расчет средних ожидаемых векторов
void CalcMiddleSamples(void);

// Расчет максимальных элементов вектора
void CalcMaxElements(void);

// Отсечение выбросов в обучающей выборке по дисперсии
void CalcDispersionCropping(void);
// --------------------------

// ------------------------
// Скрытые методы счета
// ------------------------
public:
// Устанавливает значения входного вектора для распознавания
virtual bool SetInput(const Real &input);
// ------------------------
};

}

#endif
