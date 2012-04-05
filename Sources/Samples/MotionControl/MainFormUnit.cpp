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
 UEngineMonitorForm->Show();
 EngineInit(0,ExceptionHandler);

 //ComponentsListForm->Show();
 //ClassesListForm->Show();
 UComponentsControlForm->Show();
 UComponentLinksForm->Show();
// Model_Create(80);
}
//---------------------------------------------------------------------------


void __fastcall TMainForm::ShowClassesButtonClick(TObject *Sender)
{
 UClassesListForm->Show();
}
//---------------------------------------------------------------------------


void __fastcall TMainForm::CreateModelButtonClick(TObject *Sender)
{
 Model_Destroy();

 Model_Create(UClassesListForm->ClassesListFrame->GetSelectedId());

 UComponentsListForm->ComponentsListFrame1->UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::DestroyModelButtonClick(TObject *Sender)
{
 Model_Destroy();
 UComponentsListForm->ComponentsListFrame1->UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::StartButtonClick(TObject *Sender)
{
 Timer->Enabled=true;
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::StopButtonClick(TObject *Sender)
{
 Timer->Enabled=false;
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::ResetButtonClick(TObject *Sender)
{
 Env_Reset("");
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::TimerTimer(TObject *Sender)
{
 Env_Calculate("");
 UEngineMonitorForm->EngineMonitorFrame->UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::Button1Click(TObject *Sender)
{
 UComponentLinksForm->UComponentLinksFrame->UpdateInterface();
}
//---------------------------------------------------------------------------

