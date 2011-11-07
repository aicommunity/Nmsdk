//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "NeuroVisualFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "NeuroVisualFrameUnit"
#pragma resource "*.dfm"
TNeuroVisualForm *NeuroVisualForm;
//---------------------------------------------------------------------------
__fastcall TNeuroVisualForm::TNeuroVisualForm(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
