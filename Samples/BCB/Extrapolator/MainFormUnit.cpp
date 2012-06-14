//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "MainFormUnit.h"
#include "TNSupport.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "WatchFrameUnit"
#pragma link "TUClassRegistryFrame"
#pragma resource "*.dfm"
TMainForm *MainForm;
//---------------------------------------------------------------------------
__fastcall TMainForm::TMainForm(TComponent* Owner)
	: TForm(Owner)
{
 int v1=RDK::UItemData::DefaultDataSize;
 RDK::UItemData::DefaultDataSize=sizeof(double);
 int v2=RDK::UItemData::DefaultDataSize;

 Environment.SetStorage(&Storage);

 Environment.AddClassLibrary(&BCLLibrary);
 Environment.AddClassLibrary(&MathLibrary);
// Environment.AddClassLibrary(&SensorLibrary);
 Environment.AddClassLibrary(&SourceLibrary);
 Environment.BuildStorage();

 Environment.CreateModel("NModel");

 MExtrapolator=dynamic_pointer_cast<NMExtrapolator>(Storage.TakeObject("NMExtrapolator"));
 Generator=dynamic_pointer_cast<NSinusGenerator>(Storage.TakeObject("NSinusGenerator"));
 PGenerator=dynamic_pointer_cast<NPulseGenerator>(Storage.TakeObject("NPGenerator"));
 Sum=dynamic_pointer_cast<NSum>(Storage.TakeObject("NSum"));

 Environment->AddComponent(MExtrapolator);
 Environment->AddComponent(Generator);
 Environment->AddComponent(PGenerator);
 Environment->AddComponent(Sum);

 bool res=true;

 Environment->SetTimeStep(1000);
 MExtrapolator->SetTimeStep(1000);
 Generator->SetTimeStep(1000);

 MExtrapolator->NumLevels=4;

 PGenerator->PulseLength=0.01;
 PGenerator->Frequency=10;
 PGenerator->Amplitude=100;
 Generator->Amplitude=1;
 Generator->Frequency=1;

 res&=Generator->Connect(Sum,0);
 res&=PGenerator->Connect(Sum,0);
 res&=Sum->Connect(MExtrapolator,0);
 PGenerator->SetActivity(false);

 int v3=RDK::UItemData::DefaultDataSize;

}
//---------------------------------------------------------------------------
void __fastcall TMainForm::FormShow(TObject *Sender)
{
 Environment->Reset();

 AddWatch(WatchFrame,Sum,0,0,5);
 AddWatch(WatchFrame,MExtrapolator,0,0,5);
// AddWatch(WatchFrame,PGenerator,0,0,5);

// Environment->Save(Reg);
// UClassRegistryFrame->SetRegistry(&Reg);

 Timer->Enabled=true;
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::TimerTimer(TObject *Sender)
{
 int v1=RDK::UItemData::DefaultDataSize;
 for(size_t i=0;i<20;i++)
 {
  Environment.Calculate();
  WatchFrame->StepUpdate();
 }
 int v2=RDK::UItemData::DefaultDataSize;
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::Button1Click(TObject *Sender)
{
 PGenerator->SetActivity(!PGenerator->GetActivity());
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::AmplitudeTrackBarChange(TObject *Sender)
{
 Generator->Amplitude=AmplitudeTrackBar->Position/1000.0;
 AmplitudeEdit->Text=FloatToStrF(Generator->Amplitude,ffFixed,3,3);
}
//---------------------------------------------------------------------------/*
/*
void __fastcall TMainForm::UClassRegistryFrameLabeledEditKeyPress(TObject *Sender,
          wchar_t &Key)
{
  UClassRegistryFrame->LabeledEditKeyPress(Sender,Key);

  if(Key == VK_RETURN)
  {
   Environment->Load(*UClassRegistryFrame->GetDiffRegistry(),0,true);
   Environment->Save(Reg);
   UClassRegistryFrame->SetRegistry(&Reg);
  }
}
*/
//---------------------------------------------------------------------------/*
/*
void __fastcall TMainForm::UClassRegistryFrameSetBitBtnClick(TObject *Sender)
{
  UClassRegistryFrame->SetBitBtnClick(Sender);
  Environment->Load(*UClassRegistryFrame->GetDiffRegistry(),0,true);
  Environment->Save(Reg);
  UClassRegistryFrame->SetRegistry(&Reg);
}*/
//---------------------------------------------------------------------------
void __fastcall TMainForm::FrequencyTrackBarChange(TObject *Sender)
{
 Generator->Frequency=FrequencyTrackBar->Position/1000.0;
 FrequencyEdit->Text=FloatToStrF(Generator->Frequency,ffFixed,3,3);
}
//---------------------------------------------------------------------------
void __fastcall TMainForm::ResetButtonClick(TObject *Sender)
{
 Environment.Reset();
 WatchFrame->Reset();
 WatchFrame->Clear();
 AddWatch(WatchFrame,Sum,0,0,5);
 AddWatch(WatchFrame,MExtrapolator,0,0,5);
}
//---------------------------------------------------------------------------
