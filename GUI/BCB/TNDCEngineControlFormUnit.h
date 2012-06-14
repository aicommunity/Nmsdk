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
#include <string>
#include "myrdk.h"
#pragma warn -8130
//---------------------------------------------------------------------------
class TNDCEngineControlForm : public TForm, public RDK::UIVisualController
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
	void __fastcall FormShow(TObject *Sender);
	void __fastcall FormHide(TObject *Sender);
	void __fastcall IaCheckBoxClick(TObject *Sender);
	void __fastcall IbCheckBoxClick(TObject *Sender);
	void __fastcall IICheckBoxClick(TObject *Sender);
	void __fastcall ControlVoltageCheckBoxClick(TObject *Sender);
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

// ���� ���������� ����������
bool UpdateInterfaceFlag;

// ����� ���������� ����������
void UpdateInterface(void);

// �����, ���������� ����� ����� �������
void BeforeCalculate(void);

// �����, ���������� ����� ���� �������
void AfterCalculate(void);

// ��������� ������ �� ����������
void ReadComponentData(void);
};
//---------------------------------------------------------------------------
extern PACKAGE TNDCEngineControlForm *NDCEngineControlForm;
//---------------------------------------------------------------------------
#pragma warn .8130

#endif
