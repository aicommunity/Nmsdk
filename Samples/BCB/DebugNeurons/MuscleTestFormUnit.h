//---------------------------------------------------------------------------

#ifndef MuscleTestFormUnitH
#define MuscleTestFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include "WatchFrameUnit.h"
#include <ComCtrls.hpp>
//---------------------------------------------------------------------------
class TMuscleTestForm : public TForm
{
__published:	// IDE-managed Components
	TPageControl *PageControl1;
	TTabSheet *TabSheet1;
	TWatchFrame *SingleMuscleWatchFrame;
	TTabSheet *TabSheet2;
	TWatchFrame *DoubleMuscleWatchFrame;
	TTabSheet *TabSheet3;
	TTabSheet *TabSheet4;
	TWatchFrame *FBMotoneuronWatchFrame;
	TTabSheet *TabSheet5;
	TWatchFrame *MotoneuronFrequencyWatchFrame;
	TTabSheet *TabSheet6;
	TWatchFrame *NetworkWatchFrame;
	TTabSheet *TabSheet7;
	TWatchFrame *FNetworkWatchFrame;
	TWatchFrame *AfferentWatchFrame;
private:	// User declarations
public:		// User declarations
	__fastcall TMuscleTestForm(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TMuscleTestForm *MuscleTestForm;
//---------------------------------------------------------------------------
#endif
