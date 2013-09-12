#ifndef TNSUPPORT_CPP
#define TNSUPPORT_CPP


#include "TNSupport.h"
#include "../Libraries/ReceiverLib/NReceiverLibrary.h"


namespace NMSDK {

// ��������� ������ � ���� ���������� (������ �� �������)
void AddWatch(TWatchFrame *watch, RDK::UContainer *item, int output, int outindex, double watchinterval, double yshift, TPenStyle style, TColor color)
{
 NADItem *itemd=dynamic_cast<NADItem*>(item);

 if(!watch || !itemd)
  return;

 OutGateWatchData wd;
 wd.FullUpdate=false;
 wd.WatchInterval=watchinterval;
 wd.X=&NAContainer::GetDoubleTime();

 wd.YShift=yshift;
 if(itemd->GetOwner())
  itemd->GetLongName(static_pointer_cast<NAContainer>(itemd->GetOwner()->GetOwner()),wd.Legend);
 else
  itemd->GetLongName(0,wd.Legend);
 wd.Legend+=string("[")+RDK::sntoa(output)+string(":");
 wd.Legend+=RDK::sntoa(outindex)+string("]");
 wd.DataSource=item;

 if(color == 0) // ������ ����������� �����
  wd.Color=watch->Chart1->GetFreeSeriesColor(true);
 else
  wd.Color=color;

 wd.Y=&(itemd->GetOutputData(output).Double[outindex]);
 wd.XYSize=1;
 wd.Style=style;
 watch->Add(wd);
}

// ��������� ����������� ������ � ���� ���������� (������ �� �������)
void AddWatch(TWatchFrame *watch, NameT name, double *y, double watchinterval, double yshift, TPenStyle style, TColor color)
{
 if(!watch || !y)
  return;

 OutGateWatchData wd;
 wd.FullUpdate=false;
 wd.WatchInterval=watchinterval;
 wd.X=&NAContainer::GetDoubleTime();

 wd.YShift=yshift;
 wd.Legend=name;
 wd.DataSource=0;

 if(color == 0) // ������ ����������� �����
  wd.Color=watch->Chart1->GetFreeSeriesColor(true);
 else
  wd.Color=color;

 wd.Y=y;
 wd.XYSize=1;
 wd.Style=style;
 watch->Add(wd);
}


// ��������� ������ � ���� ���������� (������ �� �������)
void AddFrequencyWatch(TWatchFrame *watch, RDK::UContainer* item, double watchinterval, double yshift, TPenStyle style, TColor color)
{
 NFrequencyReceiver *itemd=dynamic_cast<NFrequencyReceiver*>(item);

 if(!itemd || !watch)
  return;

 OutGateWatchData wd;
 wd.FullUpdate=true;
 wd.WatchInterval=watchinterval;
 wd.X=&itemd->GetXResult()[0];

 wd.YShift=yshift;
 if(itemd->GetOwner())
  itemd->GetLongName(static_pointer_cast<RDK::UContainer>(itemd->GetOwner()->GetOwner()),wd.Legend);
 else
  itemd->GetLongName(0,wd.Legend);
// wd.Legend+=string("[")+sntoa(output)+string(":")+sntoa(outindex)+string("]");
 wd.DataSource=item;

 if(color == 0) // ������ ����������� �����
  wd.Color=watch->Chart1->GetFreeSeriesColor(true);
 else
  wd.Color=color;

 wd.Y=&itemd->GetYResult()[0];
 wd.XYSize=itemd->GetYResult().size();
 wd.Style=style;
 watch->Add(wd);
}



}
#endif
