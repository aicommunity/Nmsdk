#ifndef NCMySDKWatchFrameH
#define NCMySDKWatchFrameH

#include "../../Kernel/NController.h"
#include "WatchFrameUnit.h"
#include "NBios.h"

namespace NMSDK {

class NCMySDKWatchFrame: public NController, public OutGateWatchData
{
protected: // Параметры
// Индекс наблюдаемого вектора выходов
size_t Output;

// Индекс элемента в наблюдаемом векторе выходов
size_t OutputIndex;

protected: // Данные
TWatchFrame *WatchFrame;

public:
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCMySDKWatchFrame(void);
NCMySDKWatchFrame(TWatchFrame *watch);
NCMySDKWatchFrame(TWatchFrame *watch, NAContainer *item, int output, int outindex, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));
virtual ~NCMySDKWatchFrame(void);
// --------------------------

// --------------------------
// Методы управления параметрами
// --------------------------
// --------------------------

// --------------------------
// Методы управления интерфейсом
// --------------------------
// Фрейм наблюдения
TWatchFrame* GetWatchFrame(void) const;
bool SetWatchFrame(TWatchFrame *watchframe);

// Добавляем объект в окно наблюдений (график по времени)
void AddWatch(NAContainer *item, int output, int outindex, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));
void AddWatch(NAContainer *item, int output, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));
void AddWatch(NAContainer *item, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

// Задает имя графика
void SetLegend(const string &legend);

// Вычисляет имя графика как имя компонента с индексом 'index' с заданной
// глубиной владельцев
void CalcLegend(int index, int level);
// --------------------------

// --------------------------
// Скрытые методы управления интерфейсом
// --------------------------
protected:
// Связывает интерфейс с компонентом
virtual bool ALink(NAContainer* component, bool forchlids=false);

// Отвязывает интерфейс от компонента
virtual bool AUnLink(int index, bool forchlids=false);

// Обновляет интерфейс
virtual bool AUpdate(void);
// --------------------------

};


}

#endif
