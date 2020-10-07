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
#include "UWatchFramePageUnit.h"

#include "..\..\Libraries\Nmsdk-PulseNeuronLib\Core\NNeuronTrainer.h"
//#include "nmsdk_cpp_initdll.h"
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
	TStringGrid *InputDelaysGrid;
	TButton *SetDendritesButton;
	TLabel *PatternLabel;
	TLabel *TrainLabel;
	TButton *StartTrainingButton;
	TButton *StopTrainingButton;
	TToolButton *ToolButton2;
	TToolButton *OpenToolButton;
	TToolButton *ToolButton5;
	TToolButton *SaveToolButton;
	TCheckBox *FixedLTZThresholdCheckBox;
	void __fastcall StartToolButtonClick(TObject *Sender);
	void __fastcall PauseToolButtonClick(TObject *Sender);
	void __fastcall SetDendritesButtonClick(TObject *Sender);
	void __fastcall NumInputDendriteUpDownClick(TObject *Sender, TUDBtnType Button);
	void __fastcall SetParamsButtonClick(TObject *Sender);
	void __fastcall StartTrainingButtonClick(TObject *Sender);
	void __fastcall StopTrainingButtonClick(TObject *Sender);
	void __fastcall ResetToolButtonClick(TObject *Sender);
	void __fastcall OpenToolButtonClick(TObject *Sender);
	void __fastcall SaveToolButtonClick(TObject *Sender);

private:	// User declarations
public:		// User declarations
	__fastcall TNNeuronTrainerFrame(TComponent* Owner);


// Сохраняет параметры интерфейса в xml
virtual void ASaveParameters(RDK::USerStorageXML &xml);

// Загружает параметры интерфейса из xml
virtual void ALoadParameters(RDK::USerStorageXML &xml);

virtual void AAfterLoadProject(void);

void AUpdateInterface(void);


// Возврат интерфейса в исходное состояние
void AClearInterface(void);


// Создание копии этого компонента
virtual TUVisualControllerFrame* New(TComponent *owner=0);
};
//---------------------------------------------------------------------------
extern PACKAGE TNNeuronTrainerFrame *NNeuronTrainerFrame;
//---------------------------------------------------------------------------
#endif
