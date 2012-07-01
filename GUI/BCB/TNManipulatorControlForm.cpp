//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "TNManipulatorControlForm.h"
#include "UComponentsListFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TNManipulatorControlForm *NManipulatorControlForm;
//---------------------------------------------------------------------------
__fastcall TNManipulatorControlForm::TNManipulatorControlForm(TComponent* Owner)
	: TForm(Owner)
{
 UpdateInterfaceFlag=false;
}

void TNManipulatorControlForm::UpdateInterface(void)
{
 UpdateInterfaceFlag=true;

 if(ManipulatorName.empty())
 {
  ComponentSelectionPanel->Color=clRed;
  ComponentSelectionPanel->Caption="Double click to select manipulator component";
  GroupBox1->Enabled=false;
  GroupBox3->Enabled=false;
  Caption="Manipulator [Not set]";
 }
 else
 {
  ComponentSelectionPanel->Color=clGreen;
  ComponentSelectionPanel->Caption=ManipulatorName.c_str();
  GroupBox1->Enabled=true;
  GroupBox3->Enabled=true;
  Caption=String("Manipulator [")+ManipulatorName.c_str()+String("]");
 }

 if(ControlSystemName.empty())
 {
  ControlSystemSelectionPanel->Color=clRed;
  ControlSystemSelectionPanel->Caption="Double click to select manipulator component";
  Caption="Manipulator control [Not set]";
 }
 else
 {
  ControlSystemSelectionPanel->Color=clGreen;
  ControlSystemSelectionPanel->Caption=ControlSystemName.c_str();
  Caption=String("Control system [")+ControlSystemName.c_str()+String("]");
 }


 if(Manipulator)
 {
  if(Manipulator->DMReset) // процедура подключения пройдена
  {
   ConnectButton->Enabled=false;
   DisconnectButton->Enabled=true;
   StartButton->Enabled=true;
   StopButton->Enabled=true;
   ResetButton->Enabled=true;
   GroupBox1->Enabled=false;
   TabSheet2->Enabled=true;
  }
  else
  {
   ConnectButton->Enabled=true;
   DisconnectButton->Enabled=false;
   StartButton->Enabled=false;
   StopButton->Enabled=false;
   ResetButton->Enabled=false;
   GroupBox1->Enabled=true;
   TabSheet2->Enabled=false;
  }
 }

 UpdateInterfaceFlag=false;
}


bool TNManipulatorControlForm::ManipulatorCSConnect(const std::string &cs_name, const std::string &man_name)
{
 RDK::UEPtr<RDK::UANet> net=RDK::dynamic_pointer_cast<RDK::UANet>(GetModel());

 bool res=true;
 res&=net->CreateLink(man_name,0,cs_name+".NManipulatorSource1",0);
 res&=net->CreateLink(man_name,1,cs_name+".NManipulatorSource1",1);
 res&=net->CreateLink(man_name,2,cs_name+".NManipulatorSource1",2);
 res&=net->CreateLink(cs_name+".NManipulatorInput1",0,man_name,0);

 // Связываем все управляющие элементы
 int motion_elements=RDK::dynamic_pointer_cast<NMSDK::NEngineMotionControl>(net->GetComponentL(cs_name))->NumMotionElements;
 for(int i=0;i<motion_elements;i++)
 {
  res&=net->CreateLink(cs_name+std::string(".MotionElement")+RDK::sntoa(i)
	+".Motoneuron1.LTZone",0,man_name);
  res&=net->CreateLink(cs_name+std::string(".MotionElement")+RDK::sntoa(i)
	+".Motoneuron2.LTZone",0,man_name);
 }
 return res;
}
//---------------------------------------------------------------------------
void __fastcall TNManipulatorControlForm::Disconnect1Click(TObject *Sender)
{
 if(!Manipulator)
  return;

 Manipulator->UnInitManipulator();
 Manipulator->UnLoadManipulatorDll();
 UpdateInterface();
}
//---------------------------------------------------------------------------
void __fastcall TNManipulatorControlForm::MoveLeft1Click(TObject *Sender)
{
 if(!Manipulator || !Manipulator->DMMoveServo)
  return;

 Manipulator->DMMoveServo(1,1,255,50);
}
//---------------------------------------------------------------------------
void __fastcall TNManipulatorControlForm::MoveRight1Click(TObject *Sender)
{
 if(!Manipulator || !Manipulator->DMMoveServo)
  return;

 Manipulator->DMMoveServo(1,2,255,50);
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::SelectManipulator1Click(TObject *Sender)
{
 if(UComponentsListForm->ShowComponentSelect() != mrOk)
  return;

 if(Manipulator)
 {
  Disconnect1Click(Sender);
  ManipulatorName="";
 }

 ManipulatorName=UComponentsListForm->ComponentsListFrame1->GetSelectedComponentLongName();
 Manipulator=RDK::dynamic_pointer_cast<NMSDK::NWPhysicalManipulator>(GetModel()->GetComponentL(ManipulatorName));
 if(!Manipulator)
  ManipulatorName="";

 UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::Connect1Click(TObject *Sender)
{
 if(!Manipulator)
  return;
 Manipulator->WindowHandle=Handle;
 Manipulator->ComPort=StrToInt(ComPortComboBox->Text);
 if(EmulatorModeRadioButton->Checked == true)
  Manipulator->EmulatorMode=true;
 else
  Manipulator->EmulatorMode=false;

 Manipulator->DllManipulatorMode=ControlModeComboBox->ItemIndex;
 Manipulator->LoadManipulatorDll();
 Manipulator->InitManipulator();
 UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::DeviceModeRadioButtonClick(TObject *Sender)
{
 ComPortComboBox->Enabled=true;
 EmulatorModeRadioButton->Checked=false;
 ControlModeComboBox->Enabled=true;
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::EmulatorModeRadioButtonClick(TObject *Sender)

{
 ComPortComboBox->Enabled=false;
 DeviceModeRadioButton->Checked=false;
 ControlModeComboBox->Enabled=false;
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::FormShow(TObject *Sender)
{
 UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::ComponentSelectionPanelDblClick(TObject *Sender)
{
 SelectManipulator1Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::ConnectButtonClick(TObject *Sender)
{
 Connect1Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::DisconnectButtonClick(TObject *Sender)
{
 Disconnect1Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::Reset1Click(TObject *Sender)
{
 if(!Manipulator || !Manipulator->DMMoveServo)
  return;

 Manipulator->DMReset();
 UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::ResetButtonClick(TObject *Sender)
{
 Reset1Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::StartButtonClick(TObject *Sender)
{
 Start1Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::StopButtonClick(TObject *Sender)
{
 Stop1Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::Start1Click(TObject *Sender)
{
 if(!Manipulator || !Manipulator->DMMoveServo)
  return;

 Manipulator->DMStart();
 UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::Stop1Click(TObject *Sender)
{
 if(!Manipulator || !Manipulator->DMMoveServo)
  return;

 Manipulator->DMStop();
 UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::Button2Click(TObject *Sender)
{
 if(!Manipulator || !Manipulator->DMMoveServo)
  return;

 Manipulator->DMMoveServo(CBoxServoMove->ItemIndex, ComboBoxDir->ItemIndex+1, TrackBarPWM->Position, TrackBarTime->Position);
}
//---------------------------------------------------------------------------


void __fastcall TNManipulatorControlForm::FormClose(TObject *Sender, TCloseAction &Action)

{
 Disconnect1Click(Sender);
 Sleep(100);
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::IaCheckBoxClick(TObject *Sender)
{
 bool res=true;
 RDK::UEPtr<NMSDK::NAContainer> cont;

 if(!ControlSystem)
  return;

 int num_motions=ControlSystem->NumMotionElements;

 if(IaCheckBox->Checked)
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=std::string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=std::string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1);
	res&=ControlSystem->BreakLink("AfferentSource1",0,motion+".Afferent_Ia2.Receptor",0);
	res&=ControlSystem->BreakLink("AfferentSource1",0,motion+".Afferent_Ia1.Receptor",0);

	res&=ControlSystem->CreateLink(pos_separator,0,motion+".Afferent_Ia2.Receptor",0);
	res&=ControlSystem->CreateLink(neg_separator,0,motion+".Afferent_Ia1.Receptor",0);
   }
  }
 else
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=std::string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=std::string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1);
	res&=ControlSystem->BreakLink(pos_separator,0,motion+".Afferent_Ia2.Receptor",0);
	res&=ControlSystem->BreakLink(neg_separator,0,motion+".Afferent_Ia1.Receptor",0);

	res&=ControlSystem->CreateLink("AfferentSource1",0,motion+".Afferent_Ia2.Receptor",0);
	res&=ControlSystem->CreateLink("AfferentSource1",0,motion+".Afferent_Ia1.Receptor",0);
   }
  }

 if(!res)
  return;

}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::IIAfferentTrackBarChange(TObject *Sender)

{
// IIPosAfferent=RDK::dynamic_pointer_cast<NMSDK::NPulseGenerator>(GetModel()->GetComponentL(ControlSystemName));


 if(!IIPosAfferent || !IINegAfferent)
  return;

 if(IIAfferentTrackBar->Position>=0)
 {
  IIPosAfferent->Frequency=IIAfferentTrackBar->Position;
  IINegAfferent->Frequency=0;
  IIAfferentEdit->Text=FloatToStrF(IIPosAfferent->Frequency,ffFixed,3,3);
 }
 else
 {
  IINegAfferent->Frequency=-IIAfferentTrackBar->Position;
  IIPosAfferent->Frequency=0;
  IIAfferentEdit->Text=FloatToStrF(-IINegAfferent->Frequency,ffFixed,3,3);
 }
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::IINumAfferentTrackBarChange(TObject *Sender)

{
 bool res=true;

 if(!ControlSystem)
  return;

 for(int i=0;i<IINumAfferentTrackBar->Position;i++)
 {
  // Вариант для отдельного участка мембраны для внешнего управления
  res&=ControlSystem->CreateLink("IIPosAfferentGenerator",0,std::string("MotionElement")+RDK::sntoa(i)+".PostAfferent14.PNeuronMembrane.PosChannel");
  res&=ControlSystem->CreateLink("IIPosAfferentGenerator",0,std::string("MotionElement")+RDK::sntoa(i)+".PostAfferent24.PNeuronMembrane.NegChannel");
  res&=ControlSystem->CreateLink("IINegAfferentGenerator",0,std::string("MotionElement")+RDK::sntoa(i)+".PostAfferent14.PNeuronMembrane.NegChannel");
  res&=ControlSystem->CreateLink("IINegAfferentGenerator",0,std::string("MotionElement")+RDK::sntoa(i)+".PostAfferent24.PNeuronMembrane.PosChannel");
 }

 for(int i=IINumAfferentTrackBar->Position;i<IINumAfferentTrackBar->Max;i++)
 {
  // Вариант для отдельного участка мембраны для внешнего управления
  res&=ControlSystem->BreakLink("IIPosAfferentGenerator",0,std::string("MotionElement")+RDK::sntoa(i)+".PostAfferent14.PNeuronMembrane.PosChannel",0);
  res&=ControlSystem->BreakLink("IIPosAfferentGenerator",0,std::string("MotionElement")+RDK::sntoa(i)+".PostAfferent24.PNeuronMembrane.NegChannel",0);
  res&=ControlSystem->BreakLink("IINegAfferentGenerator",0,std::string("MotionElement")+RDK::sntoa(i)+".PostAfferent14.PNeuronMembrane.NegChannel",0);
  res&=ControlSystem->BreakLink("IINegAfferentGenerator",0,std::string("MotionElement")+RDK::sntoa(i)+".PostAfferent24.PNeuronMembrane.PosChannel",0);
 }

 IINumAfferentEdit->Text=IntToStr(IINumAfferentTrackBar->Position);
 if(!res)
  return;

}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::IbCheckBoxClick(TObject *Sender)
{
 bool res=true;
// RDK::UEPtr<NMSDK::NAContainer> cont;

 if(!ControlSystem)
  return;

 int num_motions=ControlSystem->NumMotionElements;
  if(IbCheckBox->Checked)
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=std::string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=std::string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1);

	res&=ControlSystem->BreakLink("AfferentSource1",0,motion+".Afferent_Ib2.Receptor",0);
	res&=ControlSystem->BreakLink("AfferentSource1",0,motion+".Afferent_Ib1.Receptor",0);

	res&=ControlSystem->CreateLink(pos_separator,0,motion+".Afferent_Ib1.Receptor",0);
	res&=ControlSystem->CreateLink(neg_separator,0,motion+".Afferent_Ib2.Receptor",0);
   }
  }
  else
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=std::string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=std::string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1);

	res&=ControlSystem->BreakLink(pos_separator,0,motion+".Afferent_Ib1.Receptor",0);
	res&=ControlSystem->BreakLink(neg_separator,0,motion+".Afferent_Ib2.Receptor",0);

	res&=ControlSystem->CreateLink("AfferentSource1",0,motion+".Afferent_Ib1.Receptor",0);
	res&=ControlSystem->CreateLink("AfferentSource1",0,motion+".Afferent_Ib2.Receptor",0);
   }
  }

 if(!res)
  return;

}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::IICheckBoxClick(TObject *Sender)
{
 bool res=true;
// RDK::UEPtr<NMSDK::NAContainer> cont;

 if(!ControlSystem)
  return;

 int num_motions=ControlSystem->NumMotionElements;

  if(IICheckBox->Checked)
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=std::string("II_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=std::string("II_NegIntervalSeparator")+RDK::sntoa(i+1);

	res&=ControlSystem->BreakLink("AfferentSource1",0,motion+".Afferent_II2.Receptor",0);
	res&=ControlSystem->BreakLink("AfferentSource1",0,motion+".Afferent_II1.Receptor",0);

	res&=ControlSystem->CreateLink(pos_separator,0,motion+".Afferent_II1.Receptor",0);
	res&=ControlSystem->CreateLink(neg_separator,0,motion+".Afferent_II2.Receptor",0);
   }
  }
  else
  {
   for(int i=0;i<num_motions;i++)
   {
	std::string motion=std::string("MotionElement")+RDK::sntoa(i);
	std::string pos_separator=std::string("II_PosIntervalSeparator")+RDK::sntoa(i+1);
	std::string neg_separator=std::string("II_NegIntervalSeparator")+RDK::sntoa(i+1);

	res&=ControlSystem->BreakLink(pos_separator,0,motion+".Afferent_II1.Receptor",0);
	res&=ControlSystem->BreakLink(neg_separator,0,motion+".Afferent_II2.Receptor",0);

	res&=ControlSystem->CreateLink("AfferentSource1",0,motion+".Afferent_II2.Receptor",0);
	res&=ControlSystem->CreateLink("AfferentSource1",0,motion+".Afferent_II1.Receptor",0);
   }
  }
 if(!res)
  return;

}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::ControlVoltageCheckBoxClick(TObject *Sender)

{
 bool res=true;

 if(!ControlSystem)
  return;

 int num_motions=ControlSystem->NumMotionElements;

  if(ControlVoltageCheckBox->Checked == false)
  {
   res&=ControlSystem->BreakLink("Pac",0,"NManipulatorInput1",0);

   res&=ControlSystem->BreakLink("Pac",0,"NManipulatorInputEmulator1",0);
  }
  else
  {
   res&=ControlSystem->CreateLink("Pac",0,"NManipulatorInput1",0);

   res&=ControlSystem->CreateLink("Pac",0,"NManipulatorInputEmulator1",0);
  }

 if(!res)
  return;
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::SelectControlSystem1Click(TObject *Sender)
{
 if(UComponentsListForm->ShowComponentSelect() != mrOk)
  return;

 ControlSystemName=UComponentsListForm->ComponentsListFrame1->GetSelectedComponentLongName();
 ControlSystem=RDK::dynamic_pointer_cast<NMSDK::NEngineMotionControl>(GetModel()->GetComponentL(ControlSystemName));
 if(!ControlSystem)
  ControlSystemName="";

 UpdateInterface();
}
//---------------------------------------------------------------------------


void __fastcall TNManipulatorControlForm::ControlSystemSelectionPanelDblClick(TObject *Sender)
{
 SelectControlSystem1Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TNManipulatorControlForm::RadioGroup1Click(TObject *Sender)
{
 int num_ranges=ControlSystem->NumMotionElements;
 bool res=true;

 if(!ControlSystem)
  return;

 if(!ManipulatorName.empty() && !ControlSystemName.empty())
  ManipulatorCSConnect(ControlSystemName, ManipulatorName);

 if(!RadioGroup1->ItemIndex)
 {
  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->BreakLink("NManipulatorSource1",2,
				 std::string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->BreakLink("NManipulatorSource1",2,
				 std::string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }

  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->BreakLink("NManipulatorSource1",1,
				 std::string("II_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->BreakLink("NManipulatorSource1",1,
				 std::string("II_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }

  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->BreakLink("NManipulatorSource1",0,
				 std::string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->BreakLink("NManipulatorSource1",0,
				 std::string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }


  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->CreateLink("NManipulatorSourceEmulator1",2,
				 std::string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->CreateLink("NManipulatorSourceEmulator1",2,
				 std::string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }

  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->CreateLink("NManipulatorSourceEmulator1",1,
				 std::string("II_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->CreateLink("NManipulatorSourceEmulator1",1,
				 std::string("II_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }

  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->CreateLink("NManipulatorSourceEmulator1",0,
				 std::string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->CreateLink("NManipulatorSourceEmulator1",0,
				 std::string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }

//  cont=ControlSystem->GetComponent("NManipulatorSourceEmulator1");
//  Engine=(NManipulatorSource*)cont;
 }
 else
 {
  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->BreakLink("NManipulatorSourceEmulator1",2,
				 std::string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->BreakLink("NManipulatorSourceEmulator1",2,
				 std::string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }

  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->BreakLink("NManipulatorSourceEmulator1",1,
				 std::string("II_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->BreakLink("NManipulatorSourceEmulator1",1,
				 std::string("II_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }

  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->BreakLink("NManipulatorSourceEmulator1",0,
				 std::string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->BreakLink("NManipulatorSourceEmulator1",0,
				 std::string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }


  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->CreateLink("NManipulatorSource1",2,
				 std::string("Ia_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->CreateLink("NManipulatorSource1",2,
				 std::string("Ia_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }

  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->CreateLink("NManipulatorSource1",1,
				 std::string("II_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->CreateLink("NManipulatorSource1",1,
				 std::string("II_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }

  for(int i=0;i<num_ranges;i++)
  {
   res&=ControlSystem->CreateLink("NManipulatorSource1",0,
				 std::string("Ib_PosIntervalSeparator")+RDK::sntoa(i+1),0);
   res&=ControlSystem->CreateLink("NManipulatorSource1",0,
				 std::string("Ib_NegIntervalSeparator")+RDK::sntoa(i+1),0);
  }
//  cont=ControlSystem->GetComponent("NManipulatorSource1");
//  Engine=(NManipulatorSource*)cont;
 }

}
//---------------------------------------------------------------------------

