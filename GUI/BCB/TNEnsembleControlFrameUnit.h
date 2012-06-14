//---------------------------------------------------------------------------

#ifndef TNEnsembleControlFrameUnitH
#define TNEnsembleControlFrameUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include "../Libraries/NeuronLifeLib/NNeuronLifeLibrary.h"
#include <Grids.hpp>
#include <ComCtrls.hpp>
#include <ExtCtrls.hpp>
//---------------------------------------------------------------------------
class TNEnsembleControlFrame : public TFrame
{
__published:	// IDE-managed Components
	TPanel *Panel2;
	TGroupBox *GroupBox1;
	TStringGrid *BetaEnsembleStringGrid;
	TSplitter *Splitter1;
	TGroupBox *GroupBox3;
	TStringGrid *EnsembleStringGrid;
	TPanel *Panel3;
	TGroupBox *GroupBox4;
	TStringGrid *EnsembleLinksStringGrid;
	TSplitter *Splitter2;
	TPanel *Panel1;
	TGroupBox *GroupBox2;
	TTrackBar *EnsembleThresholdTrackBar;
	TEdit *EnsembleThresholdEdit;
	TRadioGroup *EnsembleThresholdModeRadioGroup;
	void __fastcall EnsembleThresholdTrackBarChange(TObject *Sender);
	void __fastcall EnsembleThresholdEditChange(TObject *Sender);
	void __fastcall EnsembleThresholdModeRadioGroupClick(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TNEnsembleControlFrame(TComponent* Owner);

// Данные
NMSDK::NLifeNet* Network;

bool UpdateInterfaceFlag;

void UpdateInterface(void);

};
//---------------------------------------------------------------------------
extern PACKAGE TNEnsembleControlFrame *NEnsembleControlFrame;
//---------------------------------------------------------------------------
#endif
