//---------------------------------------------------------------------------

#ifndef MainFormUnitH
#define MainFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <Grids.hpp>
#include <ExtCtrls.hpp>
#include <ComCtrls.hpp>
#include "WatchWindowFormUnit.h"

#include "../Deploy/Include/NMSDK.h"
#include "../Kernel/NKernel.h"
#include "TUClassRegistryFrame.h"
#include "NCMySDKWatchFrame.h"
#include "nmsdk.h"
#include "rdk.h"
#include "NWindowsActLibrary.h"
#include <AppEvnts.hpp>

using namespace NMSDK;
//---------------------------------------------------------------------------
class TMainForm : public TForm
{
__published:	// IDE-managed Components
	TTimer *Timer;
	TPanel *Panel1;
	TButton *Button2;
	TButton *Button3;
	TButton *Button4;
	TButton *Button6;
	TUClassRegistryFrame *ClassRegistryFrame;
	TRadioGroup *CSModeRadioGroup;
	TButton *LinksButton;
	TLabeledEdit *WatchIntervalLabeledEdit;
	TLabel *Label1;
	TComboBox *NumMotionElementsComboBox;
	TLabeledEdit *MySDKIOLabeledEdit;
	TButton *Button1;
	TGroupBox *GroupBox1;
	TComboBox *AfferentModeComboBox;
	TButton *StatsButton;
	TApplicationEvents *ApplicationEvents1;
	void __fastcall FormShow(TObject *Sender);
	void __fastcall Button3Click(TObject *Sender);
	void __fastcall Button4Click(TObject *Sender);
	void __fastcall FormClose(TObject *Sender, TCloseAction &Action);
	void __fastcall TimerTimer(TObject *Sender);
	void __fastcall Button6Click(TObject *Sender);
	void __fastcall ClassRegistryFrame1SetBitBtnClick(TObject *Sender);
	void __fastcall Button2Click(TObject *Sender);
	void __fastcall ClassRegistryFrameSetBitBtnClick(TObject *Sender);
	void __fastcall CSModeRadioGroupClick(TObject *Sender);
	void __fastcall ClassRegistryFrameLabeledEditKeyPress(TObject *Sender, wchar_t &Key);
	void __fastcall LinksButtonClick(TObject *Sender);
	void __fastcall AfferentModeRadioGroupClick(TObject *Sender);
	void __fastcall NumMotionElementsComboBoxSelect(TObject *Sender);
	void __fastcall Button1Click(TObject *Sender);
	void __fastcall StatsButtonClick(TObject *Sender);
	void __fastcall FormCreate(TObject *Sender);

private:	// User declarations
public:		// User declarations
		__fastcall TMainForm(TComponent* Owner);

//	WNDPROC OldWindowProc;


NStorage *Storage;

//NModel *Model;

UBitmap grcanvas;
UGraphics ugraph;

NGraphics ngraph;
ULongId netid;

NEnvironment* Environment;

NWindowsActLibrary WindowsActLibrary;

NWPhysicalManipulator *Man;

NSimpleStatistic *SensorStats,*OutStats,*DetailedSensorStats;

// ЧЧХ мотонейронов
vector<NSimpleStatistic*> FFH;

// Частоты мотонейронов
vector<NSimpleStatistic*> MNFrequency;
NSimpleStatistic* SingleMNFrequency;

		real CurrentOut;

		// Текущий выделенный item
		NADItem *Selected;
		NModel *CSelected;
		RDK::UClassRegistry CSelectedRegistry;

		String str;
		vector<vector<NReceptor*> > receptor;
		vector<vector<NIntervalSeparator*> > Separators;
		NADItem* engine;

		real WatchInterval;
		real FWatchInterval;
		real CacheSize;

		int NumMotionElements;

		double ModelTime;
		double RealTime;
		int StartRealTime;
		int StartProcTime,StopProcTime;

		// Последнее время отправки управляющего пакета
		unsigned int LastSentTime;
		unsigned int CurrentTime;
		unsigned int LastDuration;

		// Инициализаци СУ
		// mode == 1 полноценная СУ
		// mode == 2 СУ без вставочных нейронов
		void CSInit(int mode, int afferentmode, int nummotionselements);
};
//---------------------------------------------------------------------------
extern PACKAGE TMainForm *MainForm;
//---------------------------------------------------------------------------
#endif
