//---------------------------------------------------------------------------

#ifndef TNDCEngineControlFormUnitH
#define TNDCEngineControlFormUnitH
//---------------------------------------------------------------------------
#include <System.Classes.hpp>
#include <Vcl.Controls.hpp>
#include <Vcl.StdCtrls.hpp>
#include <Vcl.Forms.hpp>
#include <Vcl.ExtCtrls.hpp>
#include "rdk_initdll.h"
#include <Vcl.ComCtrls.hpp>
#include "TUVisualControllerFormUnit.h"
#include <string>
#include "myrdk.h"
#include "TUVisualController.h"
#pragma warn -8130
//---------------------------------------------------------------------------
class TNDCEngineControlForm : public TUVisualControllerForm
{
__published:	// IDE-managed Components
	TPanel *Panel1;
	TPanel *Panel2;
	TPanel *Panel3;
	TGroupBox *GroupBox1;
	TImage *Image;
	TCheckBox *IaCheckBox;
	TCheckBox *IbCheckBox;
	TCheckBox *IICheckBox;
	TCheckBox *ControlVoltageCheckBox;
	TGroupBox *GroupBox2;
	TTrackBar *MomentTrackBar;
	TProgressBar *MomentProgressBar;
	TEdit *ExtMomentEdit;
	void __fastcall FormShow(TObject *Sender);
	void __fastcall IaCheckBoxClick(TObject *Sender);
	void __fastcall IbCheckBoxClick(TObject *Sender);
	void __fastcall IICheckBoxClick(TObject *Sender);
	void __fastcall ControlVoltageCheckBoxClick(TObject *Sender);
	void __fastcall MomentTrackBarChange(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TNDCEngineControlForm(TComponent* Owner);

// ��� ������� ����������
std::string MotionControlName;

// ��� ������������ ����������
std::string ComponentName;

// ������������ �����������
RDK::UBitmap BmpCanvas;
RDK::UGraphics BmpGraphics;

// ���������� �����������
int CanvasWidth,CanvasHeight;

// ���������� ���� �����
double X,Y;

// ���� �������� �����
double Angle;

// ����� ����� (����)
double Length;

// ����� ���������� ����������
void AUpdateInterface(void);

// �����, ���������� ����� ����� �������
void ABeforeCalculate(void);

// �����, ���������� ����� ���� �������
void AAfterCalculate(void);

// ��������� ������ �� ����������
void ReadComponentData(void);
};
//---------------------------------------------------------------------------
extern PACKAGE TNDCEngineControlForm *NDCEngineControlForm;
//---------------------------------------------------------------------------
#pragma warn .8130

#endif
