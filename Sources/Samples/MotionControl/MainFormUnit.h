//---------------------------------------------------------------------------

#ifndef MainFormUnitH
#define MainFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>
//---------------------------------------------------------------------------
class TMainForm : public TForm
{
__published:	// IDE-managed Components
	TPanel *Panel1;
	TButton *ShowClassesButton;
	TButton *CreateModelButton;
	TButton *DestroyModelButton;
	TButton *StartButton;
	TButton *StopButton;
	TButton *ResetButton;
	TTimer *Timer;
	TButton *Button1;
	void __fastcall FormShow(TObject *Sender);
	void __fastcall ShowClassesButtonClick(TObject *Sender);
	void __fastcall CreateModelButtonClick(TObject *Sender);
	void __fastcall DestroyModelButtonClick(TObject *Sender);
	void __fastcall StartButtonClick(TObject *Sender);
	void __fastcall StopButtonClick(TObject *Sender);
	void __fastcall ResetButtonClick(TObject *Sender);
	void __fastcall TimerTimer(TObject *Sender);
	void __fastcall Button1Click(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TMainForm(TComponent* Owner);

	bool UpdateInterfaceFlag;

	void UpdateInterface(void);
};


//---------------------------------------------------------------------------
extern PACKAGE TMainForm *MainForm;
//---------------------------------------------------------------------------
#endif
