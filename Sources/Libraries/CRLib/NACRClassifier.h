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

#ifndef NACRCLASSIFIER_H
#define NACRCLASSIFIER_H


#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <string>
#include <vector>
#include <list>
#include <ctime>

#include "../../Kernel/NBios.h"

namespace NMSDK {

//using namespace MySDK;

// Оценки качества этапа распознавания
typedef double ExpectancyT;

class NACRClassifier: public NADItem
{
public: // Общедоступные свойства
// Максимально допустимая ошибка обучения
RDK::ULProperty<real, NACRClassifier>  TrainEpsilon;

// Предельное число шагов обучения
RDK::ULProperty<size_t, NACRClassifier>  TrainMaxStepsNum;

// Граничные величины входных значений классификатора
RDK::ULProperty<real, NACRClassifier>  MinInputValue, MaxInputValue;

// Граничные величины выходных значений классификатора
RDK::ULProperty<real, NACRClassifier>  MinOutputValue, MaxOutputValue;

// Желаемый выходной диапазон классификатора
RDK::ULProperty<real, NACRClassifier>  DesiredMinOutputValue, DesiredMaxOutputValue;

// Граничные величины допустимого показателя качества
RDK::UCLProperty<Real, NACRClassifier>  MinQualityRate, MaxQualityRate;

// Имя файла загрузки/сохранения состояния обучения
RDK::ULProperty<string, NACRClassifier>  TrainFileName;

// Признак разрешения автоматической настройки показателя качества
// по результатам обучения
RDK::ULProperty<bool, NACRClassifier>  AutoQualityRate;

// Признак разрешения автоматического выравнивания выходов до ожидаемого максимума
// MaxOutputValue делением на максимальный элемент выхода
RDK::ULProperty<bool, NACRClassifier>  AutoAlignmentOutput;

public: // Свойства результаты вычислений
// Ошибка обучения
RDK::ULProperty<real, NACRClassifier>  TrainingError;

// Число примеров в обучающей выборке
RDK::ULProperty<int, NACRClassifier> NumTrainSamples;

// Показатель качества <значения показателя, номер выхода классификатора>
RDK::ULProperty<pair<real,int>, NACRClassifier>  QualityRate;

// Смаштабированные результаты вычислений
RDK::UCLProperty<Real, NACRClassifier>  ScaledResult;

// Вывод о успешности распознавания
RDK::ULProperty<bool, NACRClassifier>  IsSuccessed;

protected: // Флаги состояний
RDK::ULProperty<bool, NACRClassifier>  ModifiedFlag;

protected: // Временные переменные

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NACRClassifier(void);
virtual ~NACRClassifier(void);
// --------------------------

protected:
// -----------------------------
// Методы управления общедоступными свойствами
// -----------------------------
// Устанавливает максимально допустимую ошибку обучения
bool SetTrainEpsilon(real eps);

// Устанавливает предельное число шагов обучения
bool SetTrainMaxStepsNum(size_t lmaxsteps);

// Устанавливает граничные величины входных значений классификатора
bool SetMinInputValue(real value);
bool SetMaxInputValue(real value);

// Устанавливает граничные величины выходных значений классификатора
bool SetMinOutputValue(real value);
bool SetMaxOutputValue(real value);

// Устанавливает граничные величины допустимого показателя качества
bool SetMinQualityRate(const Real& value);
bool SetMaxQualityRate(const Real& value);

// Имя файла загрузки/сохранения состояния обучения
bool SetTrainFileName(string name);
// -----------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
protected:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool ADefault(void);
virtual bool ACRDefault(void)=0;

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool ABuild(void);
virtual bool ACRBuild(void)=0;

// Сброс процесса счета.
virtual bool AReset(void);
virtual bool ACRReset(void)=0;

// Выполняет расчет этого объекта на текущем шаге.
virtual bool ACalculate(void);
virtual bool ACRCalculate(void)=0;
// --------------------------

// --------------------------
// Методы обучения сети
// --------------------------
public:
// Сброс настроек обучения в исходное состояние
virtual void ResetTraining(void);

// Однократное обучение на заданном примере
// exp_class - номер правильного класса
virtual bool Train(size_t exp_class);
// --------------------------

// ------------------------
// Методы счета
// ------------------------
public:
// Загружает настройки из файла 'name'
virtual bool FileLoad(const string &name);
virtual bool AFileLoad(fstream &file)=0;

// Сохраняет настройки в файл 'name'
virtual bool FileSave(const string &name);
virtual bool AFileSave(fstream &file)=0;

// Устанавливает значения входного вектора для распознавания
//virtual bool SetInput(const Real &input)=0;
// ------------------------

// --------------------------
// Скрытые методы обучения сети
// --------------------------
protected:
// Сброс настроек обучения в исходное состояние
virtual void AResetTraining(void)=0;

// Однократное обучение на заданном примере
// exp_class - номер правильного класса
virtual real ATrain(size_t exp_class)=0;
// --------------------------
};

}
#endif


