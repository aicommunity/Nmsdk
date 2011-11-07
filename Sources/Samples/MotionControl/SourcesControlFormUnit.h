//---------------------------------------------------------------------------

#ifndef SourcesControlFormUnitH
#define SourcesControlFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include "TNSourceControlFrameUnit.h"
//---------------------------------------------------------------------------
class TSourcesControlForm : public TForm
{
__published:	// IDE-managed Components
	TNSourceControlFrame *NSourceControlFrame;
private:	// User declarations
public:		// User declarations
	__fastcall TSourcesControlForm(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TSourcesControlForm *SourcesControlForm;
//---------------------------------------------------------------------------
#endif
