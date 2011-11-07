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

#ifndef NCRPERSEPTRON_H
#define NCRPERSEPTRON_H

#include "NACRClassifier.h"

namespace NMSDK {

real Sigmoid(real x);

class NCRPerseptron: public NACRClassifier
{
public: // Общедоступные свойства
// Число слоев сети
RDK::ULProperty<size_t,NCRPerseptron> NumLayers;

// Число входов сети
RDK::UCLProperty<vector<size_t>, NCRPerseptron> NumInputs;

// Скорость обучения
RDK::ULProperty<real, NCRPerseptron> TrainingRate;

// Момент сети
RDK::ULProperty<real, NCRPerseptron> Moment;

// Автоопределение размера слоев
RDK::ULProperty<bool,NCRPerseptron> AutoSetLayerInputs;


protected: // Данные модели
// Матрицы весовых коэффициентов слоев
vector<vector<vector<real> > > Weights;

// Вектор входов сети
vector<real> Inputs;

// Вектор выходов слоев сети
vector<vector<real> > Outputs;

protected: // Временные переменные
vector<vector<vector<real> > > dWeights;

public:
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRPerseptron(void);
~NCRPerseptron(void);
// --------------------------

// -----------------------------
// Методы доступа к данным
// -----------------------------
public:
real GetWeight(size_t layer, size_t col, size_t row);

real GetInputs(size_t row);
real GetOutputs(size_t layer, size_t row);
// -----------------------------

protected:
// -----------------------------
// Методы управления общедоступными свойствами
// -----------------------------
// Устанавливает число слоев сети
bool SetNumLayers(size_t num);

// Устанавливает число входов всех скрытых слоев
bool SetNumInputs(const vector<size_t> &numinputs);

// Устанавливает скорость обучения сети
bool SetTrainingRate(real tr);

// Устанавливает момент сети
bool SetMoment(real m);

// Автоопределение размера слоев
bool SetAutoSetLayerInputs(bool value);
// -----------------------------

// ------------------------
// Методы счета
// ------------------------
public:
// Загружает настройки из файла 'name'
virtual bool AFileLoad(fstream &file);

// Сохраняет настройки в файл 'name'
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
// --------------------------

// ------------------------
// Скрытые методы счета
// ------------------------
public:
// Устанавливает значения входного вектора для распознавания
virtual bool SetInput(const Real &input);

protected:
// Производит расчет заданного слоя
void CalcLayer(vector<real> &in_x, vector<real> &out_q,
                        vector<vector<real> > &weights,
                        real(*ActiveFunc)(real x));

// Производит расчет всей сети
void CalcNetwork(vector<real> &inputs);
// ------------------------
};

}
#endif

