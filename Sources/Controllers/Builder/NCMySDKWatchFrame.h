#ifndef NCMySDKWatchFrameH
#define NCMySDKWatchFrameH

#include "../../Kernel/NController.h"
#include "WatchFrameUnit.h"
#include "NBios.h"

namespace NMSDK {

class NCMySDKWatchFrame: public NController, public OutGateWatchData
{
protected: // ���������
// ������ ������������ ������� �������
size_t Output;

// ������ �������� � ����������� ������� �������
size_t OutputIndex;

protected: // ������
TWatchFrame *WatchFrame;

public:
// --------------------------
// ������������ � �����������
// --------------------------
NCMySDKWatchFrame(void);
NCMySDKWatchFrame(TWatchFrame *watch);
NCMySDKWatchFrame(TWatchFrame *watch, NAContainer *item, int output, int outindex, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));
virtual ~NCMySDKWatchFrame(void);
// --------------------------

// --------------------------
// ������ ���������� �����������
// --------------------------
// --------------------------

// --------------------------
// ������ ���������� �����������
// --------------------------
// ����� ����������
TWatchFrame* GetWatchFrame(void) const;
bool SetWatchFrame(TWatchFrame *watchframe);

// ��������� ������ � ���� ���������� (������ �� �������)
void AddWatch(NAContainer *item, int output, int outindex, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));
void AddWatch(NAContainer *item, int output, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));
void AddWatch(NAContainer *item, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

// ������ ��� �������
void SetLegend(const string &legend);

// ��������� ��� ������� ��� ��� ���������� � �������� 'index' � ��������
// �������� ����������
void CalcLegend(int index, int level);
// --------------------------

// --------------------------
// ������� ������ ���������� �����������
// --------------------------
protected:
// ��������� ��������� � �����������
virtual bool ALink(NAContainer* component, bool forchlids=false);

// ���������� ��������� �� ����������
virtual bool AUnLink(int index, bool forchlids=false);

// ��������� ���������
virtual bool AUpdate(void);
// --------------------------

};


}

#endif
