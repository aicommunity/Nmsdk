/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2011.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NSimpleStatisticH
#define NSimpleStatisticH

#include "../../Kernel/NBios.h"

namespace NMSDK {

class NSimpleStatistic: public NANet
{
public: // Параметры
// Интервал времени для анализа в секундах
// По завершении интервала статистика сохраняется, и начинает копиться заново
RDK::UTime StatsInterval;

// Режим формирования статистики
// 0 - подсчет минимума, максимума и среднего
// <временная метка> Min(PInputData[0]->Double[0]) Max(PInputData[0]->Double[0]) Avg(PInputData[0]->Double[0]) ... Min(PInputData[1]->Double[0]) Max(PInputData[1]->Double[0]) Avg(PInputData[1]->Double[0])
// 1 - явный вывод входных данных в виде (построчно)
// <временная метка>
// Значения вектора PInputData[0]...
// Значения вектора PInputData[1]...
// ...и т.д.
// 2 - явный вывод входных данных в в виде
// <временная метка> PInputData[0]->Double[0] PInputData[0]->Double[1] ... PInputData[1]->Double[0] PInputData[1]->Double[1] ...
int Mode;

// Заголовки столбцов/строк
vector<string> Headers;

protected: // Данные
// Номер статистики
int StatsNumber;

protected: // Временные переменные
// Файлы данных
fstream* StatsFile;

// Момент начала очередного интервала накопления статистики
double StatsStartTime;

// Данные текущей статистики
vector<Real> StatsMin;
vector<Real> StatsMax;
vector<Real> StatsAvg;
vector<Real> StatsDelta;



public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NSimpleStatistic(void);
virtual ~NSimpleStatistic(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NSimpleStatistic* New(void);
// --------------------------

// --------------------------
// Computation methods
// --------------------------
// Открывает новый файл, сохраняя предыдущий
bool ReCreateFile(void);
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
// Вспомогательные методы счета статистики
// --------------------------
protected:
// Сбрасывает текущую статистику
void ClearStats(void);

// Задает размеры векторов данных текущей статистики
void ResizeStats(void);
// --------------------------

};

}

#endif
