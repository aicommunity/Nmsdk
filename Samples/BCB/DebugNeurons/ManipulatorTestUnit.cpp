//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "ManipulatorTestUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TManipulatorTestForm *ManipulatorTestForm;
//---------------------------------------------------------------------------
__fastcall TManipulatorTestForm::TManipulatorTestForm(TComponent* Owner)
	: TForm(Owner),graph(&canvas)
{
 Engine=0;
 Source=0;
 canvas.SetRes(640,480);

 graph.SetPenWidth(5);
 graph.SetPenColor(UColorT(0x00FF0000));
 length=100;
}
//---------------------------------------------------------------------------
void TManipulatorTestForm::UpdateInterface(void)
{
 canvas.Fill(0xFFFFFFFF);

 if(!Engine)
  return;

 double angle=Engine->GetOutputData(1).Double[0];
 double x1,y1,x2,y2;

 x1=320; y1=240;
 x2=x1+length*cos(angle-M_PI/2.0);
 y2=y1+length*sin(angle-M_PI/2.0);
 graph.SetPenPos(x1,y1);
 graph.LineTo(x2,y2);
 canvas>>Image->Picture->Bitmap;
 Image->Repaint();
}
//---------------------------------------------------------------------------
void __fastcall TManipulatorTestForm::TrackBarChange(TObject *Sender)
{
 if(Source)
  Source->Amplitude=double(TrackBar->Position)/double(TrackBar->Max/10.0);
}
//---------------------------------------------------------------------------
void __fastcall TManipulatorTestForm::FormShow(TObject *Sender)
{
 DoubleBuffered=true;
}
//---------------------------------------------------------------------------
void __fastcall TManipulatorTestForm::MomentTrackBarChange(TObject *Sender)
{
 if(Engine)
  Engine->OutMoment=double(MomentTrackBar->Position)/double(MomentTrackBar->Max/10.0);

 if(MomentTrackBar->Position>0)
  MomentProgressBar->Position=MomentTrackBar->Position;
 else
  MomentProgressBar->Position=-MomentTrackBar->Position;
}
//---------------------------------------------------------------------------

