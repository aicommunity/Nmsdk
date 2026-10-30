//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "NeuroVisualFrameUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TNeuroVisualFrame *NeuroVisualFrame;
//---------------------------------------------------------------------------




//---------------------------------------------------------------------------
__fastcall TNeuroVisualFrame::TNeuroVisualFrame(TComponent* Owner)
	: TFrame(Owner)
{
}
//---------------------------------------------------------------------------
