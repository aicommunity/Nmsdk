#ifndef TNSupportH
#define TNSupportH

#include "../../Kernel/NBios.h"
#include "WatchFrameUnit.h"

namespace NMSDK {

// ��������� ������ � ���� ���������� (������ �� �������)
void AddWatch(TWatchFrame *watch, RDK::UContainer *item, int output, int outindex, double watchinterval, double yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

// ��������� ����������� ������ � ���� ���������� (������ �� �������)
void AddWatch(TWatchFrame *watch, NameT name, double *y, double watchinterval, double yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

// ��������� ������ � ���� ���������� (������ �� �������)
void AddFrequencyWatch(TWatchFrame *watch, RDK::UContainer* item, double watchinterval, double yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

}
#endif
