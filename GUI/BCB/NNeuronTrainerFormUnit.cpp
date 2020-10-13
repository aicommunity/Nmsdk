//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "NNeuronTrainerFormUnit.h"
#include "UComponentsListFormUnit.h"
#include "UGEngineControlFormUnit.h"
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

void __fastcall TNNeuronTrainerForm::Action1Execute(TObject *Sender)
{
 if(UGEngineControlForm->DisableAdminForm)
  return;

 if(UGEngineControlForm->Visible == false)
 {
  UGEngineControlForm->Show();
  RDK::UIVisualControllerStorage::UpdateInterface(false);
 }
 else
  UGEngineControlForm->Hide();
}
//---------------------------------------------------------------------------

void __fastcall TNNeuronTrainerForm::FormShow(TObject *Sender)
{
 NNeuronTrainerFrame1->UDrawEngineFrame1->ComponentsListFrame=UGEngineControlForm->UComponentsListFrame1;
}
//---------------------------------------------------------------------------

