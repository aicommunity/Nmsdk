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
#include <Vcl.Menus.hpp>
//---------------------------------------------------------------------------
class TNNeuronTrainerForm : public TUVisualControllerForm
{
__published:	// IDE-managed Components
	TNNeuronTrainerFrame *NNeuronTrainerFrame1;
	TActionList *ActionList1;
	TAction *Action1;
	TMainMenu *MainMenu1;
	TMenuItem *File1;
	TMenuItem *Windows1;
	TMenuItem *WatchForm1;
	TMenuItem *Exit1;
	TMenuItem *SaveState1;
	void __fastcall FormCreate(TObject *Sender);
	void __fastcall Action1Execute(TObject *Sender);
	void __fastcall FormShow(TObject *Sender);
	void __fastcall SaveState1Click(TObject *Sender);
	void __fastcall Exit1Click(TObject *Sender);
	void __fastcall WatchForm1Click(TObject *Sender);
	void __fastcall FormClose(TObject *Sender, TCloseAction &Action);
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
