//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "NNeuronTrainerFrameUnit.h"
#include "UGEngineControlFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "UDrawEngineFrameUnit"
#pragma link "UWatchFrameUnit"
#pragma resource "*.dfm"
TNNeuronTrainerFrame *NNeuronTrainerFrame;
//---------------------------------------------------------------------------
__fastcall TNNeuronTrainerFrame::TNNeuronTrainerFrame(TComponent* Owner)
	: TUVisualControllerFrame(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TNNeuronTrainerFrame::StartToolButtonClick(TObject *Sender)
{
 UGEngineControlForm->Start1Click(Sender);
}
//---------------------------------------------------------------------------

