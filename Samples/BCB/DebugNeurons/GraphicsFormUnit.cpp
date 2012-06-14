//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "GraphicsFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TGraphicsForm *GraphicsForm;
//---------------------------------------------------------------------------
__fastcall TGraphicsForm::TGraphicsForm(TComponent* Owner)
	: TForm(Owner)
{
 DoubleBuffered=true;
}
//---------------------------------------------------------------------------
