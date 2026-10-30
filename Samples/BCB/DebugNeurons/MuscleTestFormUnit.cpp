//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "MuscleTestFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "WatchFrameUnit"
#pragma resource "*.dfm"
TMuscleTestForm *MuscleTestForm;
//---------------------------------------------------------------------------
__fastcall TMuscleTestForm::TMuscleTestForm(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
