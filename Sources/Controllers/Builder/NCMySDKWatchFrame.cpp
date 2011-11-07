#include "NCMySDKWatchFrame.h"


namespace NMSDK {

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCMySDKWatchFrame::NCMySDKWatchFrame(void)
{
 WatchFrame=0;
}

NCMySDKWatchFrame::~NCMySDKWatchFrame(void)
{
}
// --------------------------

// --------------------------
// Методы управления интерфейсом
// --------------------------
// Фрейм наблюдения
TWatchFrame* NCMySDKWatchFrame::GetWatchFrame(void) const
{
 return WatchFrame;
}

bool NCMySDKWatchFrame::SetWatchFrame(TWatchFrame *watchframe)
{
 if(WatchFrame == watchframe)
  return true;

 if(!watchframe)
  return false;

 WatchFrame = watchframe;
 return true;
}

// Задает имя графика
void NCMySDKWatchFrame::SetLegend(const string &legend)
{
 Legend=legend;
}

// Вычисляет имя графика как имя компонента с индексом 'index' с заданной
// глубиной владельцев
void NCMySDKWatchFrame::CalcLegend(int index, int level)
{
 if(index < 0 || index>=int(Components.size()) || !Components[index])
  return;

 NAContainer *cont=Components[index];

 for(int i=0;i<level;i++)
 {
  cont=static_cast<NAContainer*>(cont->GetOwner());
  if(!cont)
   break;
 }

 if(cont)
  Components[index]->GetLongName(cont,Legend);
 else
  Components[index]->GetLongName(0,Legend);

 Legend+=string("[")+RDK::sntoa(Output)+string(":");
 Legend+=RDK::sntoa(OutputIndex)+string("]");
}
// --------------------------

// --------------------------
// Скрытые методы управления интерфейсом
// --------------------------
// Связывает интерфейс с компонентом
bool NCMySDKWatchFrame::ALink(NAContainer* component, bool forchlids)
{
 NADItem *itemd=dynamic_cast<NADItem*>(component);

 if(!WatchFrame || !itemd)
  return false;

 X=&NAContainer::GetDoubleTime();

 //

//, public OutGateWatchData
 DataSource=itemd;

 if(Color == 0) // Подбор подходящего цвета
  Color=WatchFrame->Chart1->GetFreeSeriesColor(true);

 Y=&(itemd->GetOutputData(Output).Double[OutputIndex]);
 XYSize=1;
 SeriesIndex=WatchFrame->Add(*this);

 return true;
}

// Отвязывает интерфейс от компонента
bool NCMySDKWatchFrame::AUnLink(int index, bool forchlids)
{
 if(!WatchFrame)
  return false;

 WatchFrame->Del(SeriesIndex);
 X=0;
 Y=0;
 DataSource=0;
 SeriesIndex=-1;

 return true;
}

// Обновляет интерфейс
bool NCMySDKWatchFrame::AUpdate(void)
{
 return true;
}
// --------------------------

}

