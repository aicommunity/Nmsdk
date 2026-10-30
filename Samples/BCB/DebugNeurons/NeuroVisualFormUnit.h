//---------------------------------------------------------------------------

#ifndef NeuroVisualFormUnitH
#define NeuroVisualFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include "NeuroVisualFrameUnit.h"
//---------------------------------------------------------------------------
class TNeuroVisualForm : public TForm
{
__published:	// IDE-managed Components
	TNeuroVisualFrame *NeuroVisualFrame1;
private:	// User declarations
public:		// User declarations
	__fastcall TNeuroVisualForm(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TNeuroVisualForm *NeuroVisualForm;
//---------------------------------------------------------------------------
#endif
