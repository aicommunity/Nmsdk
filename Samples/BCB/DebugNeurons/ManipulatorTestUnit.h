//---------------------------------------------------------------------------

#ifndef ManipulatorTestUnitH
#define ManipulatorTestUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>
#include "NDCEngine.h"
#include "NConstGenerator.h"
#include "UBitmap.h"
#include "TUBitmap.h"
#include "UGraphics.h"
#include <ComCtrls.hpp>

using namespace NMSDK;
using namespace Utilities;
//---------------------------------------------------------------------------
class TManipulatorTestForm : public TForm
{
__published:	// IDE-managed Components
	TPanel *Panel1;
	TImage *Image;
	TTrackBar *TrackBar;
	TTrackBar *MomentTrackBar;
	TLabel *Label1;
	TProgressBar *MomentProgressBar;
	void __fastcall TrackBarChange(TObject *Sender);
	void __fastcall FormShow(TObject *Sender);
	void __fastcall MomentTrackBarChange(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TManipulatorTestForm(TComponent* Owner);

 NDCEngine *Engine;
 NConstGenerator *Source;

 UGraphics graph;
 UBitmap canvas;
 double length;

 void UpdateInterface(void);
};
//---------------------------------------------------------------------------
extern PACKAGE TManipulatorTestForm *ManipulatorTestForm;
//---------------------------------------------------------------------------
#endif
