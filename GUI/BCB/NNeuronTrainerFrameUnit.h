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
private:	// User declarations
public:		// User declarations
	__fastcall TNNeuronTrainerFrame(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TNNeuronTrainerFrame *NNeuronTrainerFrame;
//---------------------------------------------------------------------------
#endif
