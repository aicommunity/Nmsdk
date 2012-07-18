//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "TNDCEngineControlFormUnit.h"
#include "TUBitmap.h"
#include "UEngineMonitorFormUnit.h"
#include "nmsdk_cpp_initdll.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "TUVisualControllerFormUnit"
#pragma resource "*.dfm"
TNDCEngineControlForm *NDCEngineControlForm;
//---------------------------------------------------------------------------
__fastcall TNDCEngineControlForm::TNDCEngineControlForm(TComponent* Owner)
	: TUVisualControllerForm(Owner)
{
 BmpGraphics.SetCanvas(&BmpCanvas);
 CanvasWidth=640;
 CanvasHeight=480;
 Length=100;
 X=CanvasWidth/2;
 Y=CanvasHeight/2;
 BmpGraphics.SetPenWidth(4);

}
//---------------------------------------------------------------------------
// �����, ���������� ����� ����� �������
void TNDCEngineControlForm::ABeforeCalculate(void)
{

}

// �����, ���������� ����� ���� �������
void TNDCEngineControlForm::AAfterCalculate(void)
{

}

// ����� ���������� ����������
void TNDCEngineControlForm::AUpdateInterface(void)
{
 UpdateInterfaceFlag=true;

 ReadComponentData();
 BmpCanvas.SetRes(CanvasWidth,CanvasHeight,RDK::ubmRGB24);
 BmpCanvas.Fill(RDK::UColorT(255,255,255));
 BmpGraphics.Line(X,Y,X+Length*cos(Angle),Y+Length*sin(Angle));
 BmpCanvas>>Image->Picture->Bitmap;
 Image->Repaint();


 UpdateInterfaceFlag=false;
}


// ��������� ������ �� ����������
void TNDCEngineControlForm::ReadComponentData(void)
{
 Angle=RDK::ReadStateValue<double>(ComponentName,"Angle");
}
//---------------------------------------------------------------------------

void __fastcall TNDCEngineControlForm::FormShow(TObject *Sender)
{
 MotionControlName="EngineControlRangeAfferent";
 ComponentName=MotionControlName+".Engine";
 UpdateInterface();
}
//---------------------------------------------------------------------------
void __fastcall TNDCEngineControlForm::IaCheckBoxClick(TObject *Sender)
{
 bool res;
// NAContainer* cont;
 std::string MotionControlNameTemp=MotionControlName+".";

  std::size_t num_motions=RDK::ReadParameterValue<double>(MotionControlName,"NumMotionElements");
  if(IaCheckBox->Checked)
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=MotionControlNameTemp+std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=MotionControlNameTemp+std::string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=MotionControlNameTemp+std::string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1);

	res=Model_BreakLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_Ia2.Receptor").c_str(),0);
	res=Model_BreakLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_Ia1.Receptor").c_str(),0);

	res=Model_CreateLink(pos_separator.c_str(),0,(motion+".Afferent_Ia2.Receptor").c_str(),0);
	res=Model_CreateLink(neg_separator.c_str(),0,(motion+".Afferent_Ia1.Receptor").c_str(),0);
   }
  }
  else
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=MotionControlNameTemp+std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=MotionControlNameTemp+std::string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=MotionControlNameTemp+std::string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1);

	res=Model_BreakLink(pos_separator.c_str(),0,(motion+".Afferent_Ia2.Receptor").c_str(),0);
	res=Model_BreakLink(neg_separator.c_str(),0,(motion+".Afferent_Ia1.Receptor").c_str(),0);

	res=Model_CreateLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_Ia2.Receptor").c_str(),0);
	res=Model_CreateLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_Ia1.Receptor").c_str(),0);
   }
  }

 if(!res)
  return;
}
//---------------------------------------------------------------------------

void __fastcall TNDCEngineControlForm::IbCheckBoxClick(TObject *Sender)
{
 bool res;
// NAContainer* cont;
 std::string MotionControlNameTemp=MotionControlName+".";
				 /*
 if(MainForm->AfferentModeComboBox->ItemIndex == 0)
 {
  if(IbCheckBox->Checked)
  {
   res=ControlSystem->BreakLink("AfferentSource1",0,"MotionElement0.Afferent_Ib2.Receptor",0);
   res=ControlSystem->BreakLink("AfferentSource1",0,"MotionElement0.Afferent_Ib1.Receptor",0);

   res=ControlSystem->CreateLink("Ib_PosSignumSeparator",0,"MotionElement0.Afferent_Ib1.Receptor",0);
   res=ControlSystem->CreateLink("Ib_NegSignumSeparator",0,"MotionElement0.Afferent_Ib2.Receptor",0);
  }
  else
  {
   res=ControlSystem->BreakLink("Ib_PosSignumSeparator",0,"MotionElement0.Afferent_Ib1.Receptor",0);
   res=ControlSystem->BreakLink("Ib_NegSignumSeparator",0,"MotionElement0.Afferent_Ib2.Receptor",0);

   res=ControlSystem->CreateLink("AfferentSource1",0,"MotionElement0.Afferent_Ib2.Receptor",0);
   res=ControlSystem->CreateLink("AfferentSource1",0,"MotionElement0.Afferent_Ib1.Receptor",0);
  }
 }
					  */
// if(MainForm->AfferentModeComboBox->ItemIndex >0)
// {
  int num_motions=RDK::ReadParameterValue<double>(MotionControlName,"NumMotionElements");
  if(IbCheckBox->Checked)
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=MotionControlNameTemp+std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=MotionControlNameTemp+std::string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=MotionControlNameTemp+std::string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1);

	res=Model_BreakLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_Ib2.Receptor").c_str(),0);
	res=Model_BreakLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_Ib1.Receptor").c_str(),0);

	res=Model_CreateLink(pos_separator.c_str(),0,(motion+".Afferent_Ib1.Receptor").c_str(),0);
	res=Model_CreateLink(neg_separator.c_str(),0,(motion+".Afferent_Ib2.Receptor").c_str(),0);
   }
  }
  else
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=MotionControlNameTemp+std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=MotionControlNameTemp+std::string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=MotionControlNameTemp+std::string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1);

	res=Model_BreakLink(pos_separator.c_str(),0,(motion+".Afferent_Ib1.Receptor").c_str(),0);
	res=Model_BreakLink(neg_separator.c_str(),0,(motion+".Afferent_Ib2.Receptor").c_str(),0);

	res=Model_CreateLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_Ib1.Receptor").c_str(),0);
	res=Model_CreateLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_Ib2.Receptor").c_str(),0);
   }
  }
// }
 if(!res)
  return;
}
//---------------------------------------------------------------------------

void __fastcall TNDCEngineControlForm::IICheckBoxClick(TObject *Sender)
{
 bool res=true;
 std::string MotionControlNameTemp=MotionControlName+".";
// NADItem* cont;
/*
 if(MainForm->AfferentModeComboBox->ItemIndex == 0)
 {
  if(IICheckBox->Checked)
  {
   res&=ControlSystem->BreakLink("AfferentSource1",0,"MotionElement0.Afferent_II2.Receptor",0);
   res&=ControlSystem->BreakLink("AfferentSource1",0,"MotionElement0.Afferent_II1.Receptor",0);

   res&=ControlSystem->CreateLink("II_PosSignumSeparator",0,"MotionElement0.Afferent_II1.Receptor",0);
   res&=ControlSystem->CreateLink("II_NegSignumSeparator",0,"MotionElement0.Afferent_II2.Receptor",0);
  }
  else
  {
   res&=ControlSystem->BreakLink("II_PosSignumSeparator",0,"MotionElement0.Afferent_II1.Receptor",0);
   res&=ControlSystem->BreakLink("II_NegSignumSeparator",0,"MotionElement0.Afferent_II2.Receptor",0);

   res&=ControlSystem->CreateLink("AfferentSource1",0,"MotionElement0.Afferent_II2.Receptor",0);
   res&=ControlSystem->CreateLink("AfferentSource1",0,"MotionElement0.Afferent_II1.Receptor",0);
  }
 }
		*/
// if(MainForm->AfferentModeComboBox->ItemIndex >0)
// {
  int num_motions=RDK::ReadParameterValue<double>(MotionControlName,"NumMotionElements");
  if(IICheckBox->Checked)
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=MotionControlNameTemp+std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=MotionControlNameTemp+std::string("II_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=MotionControlNameTemp+std::string("II_NegIntervalSeparator")+RDK::sntoa(i+1);

	res&=Model_BreakLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_II2.Receptor").c_str(),0);
	res&=Model_BreakLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_II1.Receptor").c_str(),0);

	res&=Model_CreateLink(pos_separator.c_str(),0,(motion+".Afferent_II1.Receptor").c_str(),0);
	res&=Model_CreateLink(neg_separator.c_str(),0,(motion+".Afferent_II2.Receptor").c_str(),0);
   }
  }
  else
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=MotionControlNameTemp+std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=MotionControlNameTemp+std::string("II_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=MotionControlNameTemp+std::string("II_NegIntervalSeparator")+RDK::sntoa(i+1);

	res&=Model_BreakLink(pos_separator.c_str(),0,(motion+".Afferent_II1.Receptor").c_str(),0);
	res&=Model_BreakLink(neg_separator.c_str(),0,(motion+".Afferent_II2.Receptor").c_str(),0);

	res&=Model_CreateLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_II2.Receptor").c_str(),0);
	res&=Model_CreateLink((MotionControlNameTemp+"AfferentSource1").c_str(),0,(motion+".Afferent_II1.Receptor").c_str(),0);
   }
  }
// }
 if(!res)
  return;
}
//---------------------------------------------------------------------------


void __fastcall TNDCEngineControlForm::ControlVoltageCheckBoxClick(TObject *Sender)

{
 bool res;
// NADItem* cont;
 int num_motions=RDK::ReadParameterValue<double>(MotionControlName,"NumMotionElements");
 std::string MotionControlNameTemp=MotionControlName+".";


  if(ControlVoltageCheckBox->Checked == false)
  {
   res=Model_BreakLink((MotionControlNameTemp+"Pac").c_str(),0,(MotionControlNameTemp+"NManipulatorInput1").c_str(),0);

   res=Model_BreakLink((MotionControlNameTemp+"Pac").c_str(),0,(MotionControlNameTemp+"NManipulatorInputEmulator1").c_str(),0);
  }
  else
  {
   res=Model_CreateLink((MotionControlNameTemp+"Pac").c_str(),0,(MotionControlNameTemp+"NManipulatorInput1").c_str(),0);

   res=Model_CreateLink((MotionControlNameTemp+"Pac").c_str(),0,(MotionControlNameTemp+"NManipulatorInputEmulator1").c_str(),0);
  }

 if(!res)
  return;
}
//---------------------------------------------------------------------------

void __fastcall TNDCEngineControlForm::MomentTrackBarChange(TObject *Sender)
{
 double amplitude=double(MomentTrackBar->Position)/double(MomentTrackBar->Max/2.0);
 RDK::WriteParameterValue<double>(MotionControlName+std::string(".")+"EngineMoment", "Amplitude", amplitude);
 ExtMomentEdit->Text=FloatToStrF(amplitude,ffFixed,3,3);

 if(MomentTrackBar->Position>0)
  MomentProgressBar->Position=MomentTrackBar->Position;
 else
  MomentProgressBar->Position=-MomentTrackBar->Position;
}
//---------------------------------------------------------------------------

