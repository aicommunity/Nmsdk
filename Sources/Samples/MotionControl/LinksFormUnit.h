//---------------------------------------------------------------------------

#ifndef LinksFormUnitH
#define LinksFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include "NLinksFrameUnit.h"
//---------------------------------------------------------------------------
class TLinksForm : public TForm
{
__published:	// IDE-managed Components
	TNLinksFrame *NLinksFrame;
private:	// User declarations
public:		// User declarations
	__fastcall TLinksForm(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TLinksForm *LinksForm;
//---------------------------------------------------------------------------
#endif
