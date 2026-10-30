//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "MainFormUnit.h"
#include "nmsdk_initdll.h"
#include "UClassesListFormUnit.h"
#include "UEngineMonitorFormUnit.h"
#include "UComponentsListFormUnit.h"
#include "UComponentsControlFormUnit.h"
#include "UComponentLinksFormUnit.h"
//#include "TNDCEngineControlFormUnit.h"
#include "TNManipulatorControlForm.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TMainForm *MainForm;

//---------------------------------------------------------------------------
__fastcall TMainForm::TMainForm(TComponent* Owner)
	: TForm(Owner)
{
 UpdateInterfaceFlag=false;
}
//---------------------------------------------------------------------------
void TMainForm::UpdateInterface(void)
{
 UpdateInterfaceFlag=true;
 UpdateInterfaceFlag=false;
}

void __fastcall TMainForm::FormShow(TObject *Sender)
{
// UEngineMonitorForm->Show();
// EngineInit(0,ExceptionHandler);

// UComponentsControlForm->Show();
// UComponentLinksForm->Show();
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::Button2Click(TObject *Sender)
{
 NManipulatorControlForm->Show();
}
//---------------------------------------------------------------------------

