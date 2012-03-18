//---------------------------------------------------------------------------

#ifndef MainFormUnitH
#define MainFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>

#include "nmsdk.h"
#include <ExtCtrls.hpp>
#include "WatchFrameUnit.h"
#include <ComCtrls.hpp>
#include "TUClassRegistryFrame.h"

using namespace NMSDK;

//---------------------------------------------------------------------------
class TMainForm : public TForm
{
__published:	// IDE-managed Components
	TTimer *Timer;
	TWatchFrame *WatchFrame;
	TPanel *Panel1;
	TButton *Button1;
	TTrackBar *AmplitudeTrackBar;
	TLabel *Label1;
	TEdit *AmplitudeEdit;
	TLabel *Label2;
	TTrackBar *FrequencyTrackBar;
	TEdit *FrequencyEdit;
	TButton *ResetButton;
	void __fastcall FormShow(TObject *Sender);
	void __fastcall TimerTimer(TObject *Sender);
	void __fastcall Button1Click(TObject *Sender);
	void __fastcall AmplitudeTrackBarChange(TObject *Sender);
	void __fastcall FrequencyTrackBarChange(TObject *Sender);
	void __fastcall ResetButtonClick(TObject *Sender);

private:	// User declarations
public:		// User declarations
	__fastcall TMainForm(TComponent* Owner);

 RDK::UEPtr<NMExtrapolator> MExtrapolator;
 RDK::UEPtr<NSinusGenerator> Generator;
 RDK::UEPtr<NPulseGenerator> PGenerator;
 RDK::UEPtr<NSum> Sum;

 NEnvironment Environment;
 NStorage Storage;

 RDK::UClassRegistry Reg;

NBCLLibrary BCLLibrary;
//NActLibrary ActLibrary;
//NCRLibrary CRLibrary;
NSourceLibrary SourceLibrary;
NMathLibrary MathLibrary;
//NPhysLibrary PhysLibrary;
//NSensorLibrary SensorLibrary;

//NPulseNeuronLibrary PulseNeuronLibrary;
//NMotionControlLibrary MotionControlLibrary;
};
//---------------------------------------------------------------------------
extern PACKAGE TMainForm *MainForm;
//---------------------------------------------------------------------------
#endif
