//---------------------------------------------------------------------------

#ifndef NNeuronTrainerFrameUnitH
#define NNeuronTrainerFrameUnitH
//---------------------------------------------------------------------------
#include <System.Classes.hpp>
#include <Vcl.Controls.hpp>
#include <Vcl.StdCtrls.hpp>
#include <Vcl.Forms.hpp>
#include "TUVisualControllerFrameUnit.h"
#include <Vcl.ComCtrls.hpp>
#include <Vcl.ExtCtrls.hpp>
#include <Vcl.ToolWin.hpp>
#include "UDrawEngineFrameUnit.h"
#include "UWatchFrameUnit.h"
#include <System.ImageList.hpp>
#include <Vcl.ImgList.hpp>
#include <Vcl.Grids.hpp>
//---------------------------------------------------------------------------
class TNNeuronTrainerFrame : public TUVisualControllerFrame
{
__published:	// IDE-managed Components
	TPanel *Panel1;
	TToolBar *ToolBar1;
	TStatusBar *StatusBar1;
	TPanel *Panel2;
	TPanel *Panel3;
	TSplitter *Splitter1;
	TSplitter *Splitter2;
	TPanel *Panel4;
	TPanel *Panel5;
	TSplitter *Splitter3;
	TUDrawEngineFrame *UDrawEngineFrame1;
	TUWatchFrame *UWatchFrame1;
	TToolButton *StartToolButton;
	TImageList *ImageList1;
	TToolButton *ToolButton1;
	TToolButton *PauseToolButton;
	TToolButton *ToolButton3;
	TToolButton *ResetToolButton;
	TLabel *SettingsLabel;
	TLabeledEdit *DelayLabeledEdit;
	TLabeledEdit *FrequencyLabeledEdit;
	TLabeledEdit *MaxDendriteLengthLabeledEdit;
	TLabeledEdit *LTZThresholdLabeledEdit;
	TButton *SetParamsButton;
	TUpDown *NumInputDendriteUpDown;
	TLabeledEdit *NumInputDendriteLabeledEdit;
	TStringGrid *StringGrid1;
	TButton *SetDendritesButton;
	TLabel *PatternLabel;
	TLabel *TrainLabel;
	TButton *StartTrainingButton;
	TButton *StopTrainingButton;
	void __fastcall StartToolButtonClick(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TNNeuronTrainerFrame(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TNNeuronTrainerFrame *NNeuronTrainerFrame;
//---------------------------------------------------------------------------
#endif
