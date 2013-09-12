//---------------------------------------------------------------------------

#ifndef TNSourceControlFrameUnitH
#define TNSourceControlFrameUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>
#include <Grids.hpp>
#include "WatchFrameUnit.h"
#include <ComCtrls.hpp>

#include "../../Kernel/NBios.h"
//#include "NSource.h"
#include "../Libraries/BCL/NBCLLibrary.h"
#include "TUClassRegistryFrame.h"

using namespace NMSDK;

//---------------------------------------------------------------------------
class TNSourceControlFrame : public TFrame
{
__published:	// IDE-managed Components
	TPanel *Panel1;
	TPanel *Panel2;
	TSplitter *Splitter1;
	TGroupBox *GroupBox1;
	TStringGrid *SourcesStringGrid;
	TWatchFrame *SourceWatchFrame;
	TPanel *Panel3;
	TGroupBox *AmplitudeGroupBox;
	TTrackBar *AmplitudeTrackBar;
	TEdit *AmplitudeEdit;
	TGroupBox *FrequencyGroupBox;
	TTrackBar *FrequencyTrackBar;
	TEdit *FrequencyEdit;
	TUClassRegistryFrame *UClassRegistryFrame;
	void __fastcall FrequencyTrackBarChange(TObject *Sender);
	void __fastcall FrequencyEditChange(TObject *Sender);
	void __fastcall AmplitudeTrackBarChange(TObject *Sender);
	void __fastcall AmplitudeEditChange(TObject *Sender);
	void __fastcall UClassRegistryFrameLabeledEditKeyPress(TObject *Sender, wchar_t &Key);
	void __fastcall UClassRegistryFrameSetBitBtnClick(TObject *Sender);

private:	// User declarations
public:		// User declarations
	__fastcall TNSourceControlFrame(TComponent* Owner);

protected: // ������
// ������ ���������� �������
vector<NSource*> Sources;

// ���� ���������� ����������
bool UpdateInterfaceFlag;

// ������������ ��������� ����������
double WatchInterval;

// ������ ����������
RDK::UClassRegistry Parameters;

// ����� ���������� ��������
// 0 - ������ ������� ����������
// ����� - ������ ������� ��������� ��� ������� ������� �� �������� �����
double Origin;

public: // ������
// ������������� �������� ����������
bool SetWatchInterval(double interval);

// ��������� �������� � ������
bool AddSource(NSource* source);

// ������� �������� �� �������
bool DelSource(NSource* source);

// ������� �������� �� �������
bool DelSource(size_t index);

// ������� ��� ���������
bool DelAllSources(void);

// ��������� ������ ����������, ����� ����������� �� ���������� cont
// ���������� ����� ����������� ����������
int FindSources(NAContainer *cont);

// ���������� �� ����� �������� � ��������� ��������� � �������, � ������� �������
bool SelectSource(size_t sourceindex, size_t outputindex);

// ��������� ������ ���������� �������
bool WatchUpdate(void);

// ��������� ��������� ������� �� ��������� ���� �����
void StepUpdate(void);

// ��������� ���������
void UpdateInterface(void);
};
//---------------------------------------------------------------------------
extern PACKAGE TNSourceControlFrame *NSourceControlFrame;
//---------------------------------------------------------------------------
#endif
