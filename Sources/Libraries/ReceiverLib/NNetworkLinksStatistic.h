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
#ifndef NNetworkLinksStatisticH
#define NNetworkLinksStatisticH

#include "../../Kernel/NBios.h"
#include "rdk.h"

namespace NMSDK {

class NNetworkLinksStatistic: public NANet
{
public: // Параметры
// Интервал времени через который обновляется статистика
double StatsInterval;

// Режим формирования статистики
int Mode;

protected: // Данные
// Номер статистики
int StatsNumber;

protected: // Временные переменные
// Файлы данных
RDK::UIniFile<char> StatsFile;

// Момент начала очередного интервала накопления статистики
RDK::ULongTime StatsStartTime;


public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NNetworkLinksStatistic(void);
virtual ~NNetworkLinksStatistic(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NNetworkLinksStatistic* New(void);
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
