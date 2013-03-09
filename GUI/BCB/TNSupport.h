#ifndef TNSupportH
#define TNSupportH

#include "../../Kernel/NBios.h"
#include "WatchFrameUnit.h"

namespace NMSDK {

// ��������� ������ � ���� ���������� (������ �� �������)
void AddWatch(TWatchFrame *watch, RDK::UContainer *item, int output, int outindex, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

// ��������� ����������� ������ � ���� ���������� (������ �� �������)
void AddWatch(TWatchFrame *watch, NameT name, real *y, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

// ��������� ������ � ���� ���������� (������ �� �������)
void AddFrequencyWatch(TWatchFrame *watch, RDK::UContainer* item, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

}
#endif
