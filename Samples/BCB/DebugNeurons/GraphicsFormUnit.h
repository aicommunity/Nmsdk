//---------------------------------------------------------------------------

#ifndef GraphicsFormUnitH
#define GraphicsFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>
//---------------------------------------------------------------------------
class TGraphicsForm : public TForm
{
__published:	// IDE-managed Components
	TImage *Image;
private:	// User declarations
public:		// User declarations
	__fastcall TGraphicsForm(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TGraphicsForm *GraphicsForm;
//---------------------------------------------------------------------------
#endif
