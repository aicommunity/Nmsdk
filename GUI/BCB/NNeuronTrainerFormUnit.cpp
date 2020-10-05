//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "NNeuronTrainerFormUnit.h"
#include "UComponentsListFormUnit.h"
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
void __fastcall TNNeuronTrainerForm::FormCreate(TObject *Sender)
{
 TUComponentsListFrame::ComponentControllers["NNeuronTrainer"]=NNeuronTrainerForm;
}

// Создание копии этого компонента
TUVisualControllerForm* TNNeuronTrainerForm::New(TComponent *owner)
{
 return new TNNeuronTrainerForm(owner);
}
//---------------------------------------------------------------------------

