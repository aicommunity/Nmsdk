//---------------------------------------------------------------------------

#ifndef NDrawManipulatorFrameUnitH
#define NDrawManipulatorFrameUnitH
//---------------------------------------------------------------------------
#include <System.Classes.hpp>
#include <Vcl.Controls.hpp>
#include <Vcl.StdCtrls.hpp>
#include <Vcl.Forms.hpp>
#include "TUVisualControllerFrameUnit.h"
#include <Vcl.ExtCtrls.hpp>
#include <Vcl.Grids.hpp>
#include "nmsdk_cpp_initdll.h"
//#include "nmsdk.bcb.h"
//---------------------------------------------------------------------------
class TNDrawManipulatorFrame : public TUVisualControllerFrame
{
__published:	// IDE-managed Components
	TPanel *Panel3;
	TButton *Button1;
	TImage *Image;
	void __fastcall Button1Click(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TNDrawManipulatorFrame(TComponent* Owner);
	// ������������ �����������
RDK::UBitmap BmpCanvas;
RDK::UGraphics BmpGraphics;

// ���������� �����������
int CanvasWidth,CanvasHeight;

// ���������� ���� �����
double X1,X2,Y1,Y2;

// ���� �������� �����
double Angle1,Angle2;

// �������� �� ����������� ��� �����������
double Movement;

// ����� ����� (����)
double Length;

// ����������� �������� �� ���������� ���� ��� �����������
double ZeroAngle;

// ����������� �������� �� ����������� ��� �����������
double ZeroMovement;

int NumElem;

double MaxAng;

TBitmap *TempBmp;

void DrawEngine(double x,double y,double angle);
void AUpdateInterface();
};
//---------------------------------------------------------------------------
extern PACKAGE TNDrawManipulatorFrame *NDrawManipulatorFrame;
//---------------------------------------------------------------------------
#endif
