// ===========================================================
// Version:        3.0.4
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

#ifndef NCRFusionH
#define NCRFusionH

#include "NACRClassifier.h"

namespace NMSDK {

// Структура результата предварительной попарной классификации
struct NCRFPreResult
{
 // Индексы сравниваемых классов
 int Ix1, Ix2;

 // Результат классификации
 real Res1, Res2;

 NCRFPreResult(void)
 {
  Ix1=Ix2=0;
  Res1=Res2=0;
 };

};


class NCRFusion: public NACRClassifier
{
public: // Общедоступные свойства
// Режим комплексирования классификаторов
// 0 - по среднему показателей качества
// 1 - по попарному сравнению
// 2 - по среднему входов
// 3 - по числу обнаружений класса
// 4 - по сумме входов
// 5 - по числу побед на входах
// 6 - по сумме входов-победителей
RDK::ULProperty<int, NCRFusion> FusionMode;

// Число шагов усреднения по времени
RDK::ULProperty<int, NCRFusion> NumAttempts;

// Режим усреднения по времени
// 1 - среднее всех выходов
// 2 - среднее по максимумам показателей качества для класса
// 3 - по числу обнаружений класса
RDK::ULProperty<int, NCRFusion> AccumulateMode;

// Параметры попарного сравнения
RDK::UCLStateProperty<vector<vector<real> >, NCRFusion> PreResultsWeigths;

protected: // Данные модели
// Текущее значение накоплений
int CurrentAttempt;


protected: // Данные и параметры обучения сети

protected: // Временные переменные
vector<RDK::UItemData> AccumOutput;

public:
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRFusion(void);
~NCRFusion(void);
// --------------------------

protected:
// -----------------------------
// Методы управления общедоступными свойствами
// -----------------------------
bool SetFusionMode(int value);
// -----------------------------

// -----------------------------
// Методы доступа к данным модели
// -----------------------------
public:
// Текущее значение накоплений
int GetCurrentAttempt(void) const;
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
// --------------------------

// ------------------------
// Скрытые методы счета
// ------------------------
protected:
// Вычисление результата как среднего по показателю качества
bool AverageQualityCalculate(void);

// Вычисление результата как среднего по входам
bool AverageInputCalculate(void);

// Вычисление результата как суммы по входам
bool SumInputCalculate(void);

// Вычисление результата по числу обнаружений класса по входам
bool InputRecognitionCounterCalculate(void);

// Вычисление результата по сумме входов-победителей
bool SumInputRecognitionCounterCalculate(void);

// Вычисление результата через попарное сравнение
bool PairCalculate(void);

// Вычисление результата по числу обнаружений класса
bool RecognitionCounterCalculate(void);

public:
// Устанавливает значения входного вектора для распознавания
virtual bool SetInput(const Real &input);
// ------------------------
};

}
//---------------------------------------------------------------------------
#endif
