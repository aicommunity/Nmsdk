//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "LinksFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "NLinksFrameUnit"
#pragma resource "*.dfm"
TLinksForm *LinksForm;
//---------------------------------------------------------------------------
__fastcall TLinksForm::TLinksForm(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------

