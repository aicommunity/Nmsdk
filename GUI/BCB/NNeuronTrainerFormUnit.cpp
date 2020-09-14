//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "NNeuronTrainerFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "NNeuronTrainerFrameUnit"
#pragma link "TUVisualControllerFrameUnit"
#pragma resource "*.dfm"
TNNeuronTrainerForm *NNeuronTrainerForm;
//---------------------------------------------------------------------------
__fastcall TNNeuronTrainerForm::TNNeuronTrainerForm(TComponent* Owner)
	: TUVisualControllerForm(Owner)
{
}
//---------------------------------------------------------------------------
