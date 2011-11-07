//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "SourcesControlFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "TNSourceControlFrameUnit"
#pragma resource "*.dfm"
TSourcesControlForm *SourcesControlForm;
//---------------------------------------------------------------------------
__fastcall TSourcesControlForm::TSourcesControlForm(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
