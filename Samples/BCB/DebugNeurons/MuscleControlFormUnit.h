//---------------------------------------------------------------------------

#ifndef MuscleControlFormUnitH
#define MuscleControlFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>
#include <ComCtrls.hpp>
#include "NBios.h"
#include "NConstGenerator.h"
#include "NMuscle.h"
#include "NPulseGenerator.h"

using namespace NMSDK;

//---------------------------------------------------------------------------
class TMuscleControlForm : public TForm
{
__published:	// IDE-managed Components
	TPanel *Panel1;
	TPanel *Panel2;
	TPanel *Panel3;
	TPanel *Panel4;
	TGroupBox *GroupBox1;
	TEdit *AfferentEdit1;
	TTrackBar *Afferent1TrackBar;
	TGroupBox *GroupBox2;
	TEdit *AfferentEdit3;
	TTrackBar *Afferent3TrackBar;
	TGroupBox *GroupBox3;
	TCheckBox *FBRenshowCheckBox1;
	TCheckBox *FBRenshowCheckBox2;
	TGroupBox *GroupBox4;
	TEdit *MuscleMassEdit2;
	TTrackBar *MuscleMassTrackBar2;
	TGroupBox *GroupBox5;
	TEdit *MuscleMassEdit1;
	TTrackBar *MuscleMassTrackBar1;
	TGroupBox *GroupBox6;
	TEdit *AfferentEdit2;
	TTrackBar *Afferent2TrackBar;
	TPanel *Panel5;
	TPanel *Panel6;
	TGroupBox *GroupBox7;
	TEdit *Renshow2DeactivatorEdit;
	TTrackBar *Renshow2DeactivatorTrackBar;
	TGroupBox *GroupBox8;
	TEdit *Renshow1ActivatorEdit;
	TTrackBar *Renshow1ActivatorTrackBar;
	TGroupBox *GroupBox9;
	TEdit *Renshow2ActivatorEdit;
	TTrackBar *Renshow2ActivatorTrackBar;
	TGroupBox *GroupBox10;
	TEdit *Renshow1DeactivatorEdit;
	TTrackBar *Renshow1DeactivatorTrackBar;
	TGroupBox *GroupBox11;
	TEdit *LengthEdit1;
	TTrackBar *LengthTrackBar1;
	void __fastcall Afferent1TrackBarChange(TObject *Sender);
	void __fastcall Afferent2TrackBarChange(TObject *Sender);
	void __fastcall AfferentEdit1Change(TObject *Sender);
	void __fastcall AfferentEdit2Change(TObject *Sender);
	void __fastcall FBRenshowCheckBox1Click(TObject *Sender);
	void __fastcall FBRenshowCheckBox2Click(TObject *Sender);
	void __fastcall MuscleMassTrackBar1Change(TObject *Sender);
	void __fastcall MuscleMassTrackBar2Change(TObject *Sender);
	void __fastcall MuscleMassEdit1Change(TObject *Sender);
	void __fastcall MuscleMassEdit2Change(TObject *Sender);
	void __fastcall AfferentEdit3Change(TObject *Sender);
	void __fastcall Afferent3TrackBarChange(TObject *Sender);
	void __fastcall Renshow1ActivatorTrackBarChange(TObject *Sender);
	void __fastcall Renshow2ActivatorTrackBarChange(TObject *Sender);
	void __fastcall Renshow1DeactivatorTrackBarChange(TObject *Sender);
	void __fastcall Renshow2DeactivatorTrackBarChange(TObject *Sender);
	void __fastcall Renshow1ActivatorEditChange(TObject *Sender);
	void __fastcall Renshow1DeactivatorEditChange(TObject *Sender);
	void __fastcall Renshow2ActivatorEditChange(TObject *Sender);
	void __fastcall Renshow2DeactivatorEditChange(TObject *Sender);
	void __fastcall FormHide(TObject *Sender);
	void __fastcall LengthEdit1Change(TObject *Sender);
	void __fastcall LengthTrackBar1Change(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TMuscleControlForm(TComponent* Owner);

 NConstGenerator *AfferentSource1,*AfferentSource2;
 NPulseGenerator *Generator;
 NMuscle *Muscle1, *Muscle2;
 NConstGenerator *Length1,*Length2;

 NPulseGenerator* Renshow1Activator,*Renshow2Activator,
 				  *Renshow1Deactivator,*Renshow2Deactivator;

 NANet *Net;
};
//---------------------------------------------------------------------------
extern PACKAGE TMuscleControlForm *MuscleControlForm;
//---------------------------------------------------------------------------
#endif
