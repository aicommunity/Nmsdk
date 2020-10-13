//---------------------------------------------------------------------------

#ifndef NNeuronTrainerFormUnitH
#define NNeuronTrainerFormUnitH
//---------------------------------------------------------------------------
#include <System.Classes.hpp>
#include <Vcl.Controls.hpp>
#include <Vcl.StdCtrls.hpp>
#include <Vcl.Forms.hpp>

#include "TUVisualControllerFormUnit.h"
#include "NNeuronTrainerFrameUnit.h"
#include "TUVisualControllerFrameUnit.h"
#include <System.Actions.hpp>
#include <Vcl.ActnList.hpp>
//---------------------------------------------------------------------------
class TNNeuronTrainerForm : public TUVisualControllerForm
{
__published:	// IDE-managed Components
	TNNeuronTrainerFrame *NNeuronTrainerFrame1;
	TActionList *ActionList1;
	TAction *Action1;
	void __fastcall FormCreate(TObject *Sender);
	void __fastcall Action1Execute(TObject *Sender);
	void __fastcall FormShow(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TNNeuronTrainerForm(TComponent* Owner);

// Создание копии этого компонента
virtual TUVisualControllerForm* New(TComponent *owner=0);
};
//---------------------------------------------------------------------------
extern PACKAGE TNNeuronTrainerForm *NNeuronTrainerForm;
//---------------------------------------------------------------------------
#endif
