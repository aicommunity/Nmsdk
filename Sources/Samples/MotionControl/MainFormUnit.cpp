//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "MainFormUnit.h"
#include "MuscleTestFormUnit.h"
#include "MuscleControlFormUnit.h"
#include "ManipulatorTestUnit.h"
#include "GraphicsFormUnit.h"
#include "NGraphics.h"
//#include "NNet.h"
//#include "NPac.h"
//#include "NSignumSeparator.h"
//#include "NEngineMotionControl.h"
#include "../Deploy/Include/NMSDK.h"
#include "LinksFormUnit.h"
#include "TNSupport.h"
#include "SourcesControlFormUnit.h"
#include "StatisticFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "TUClassRegistryFrame"
#pragma resource "*.dfm"
TMainForm *MainForm;
       /*
LRESULT CALLBACK NewWindowProc(HWND hWnd, UINT msg, WPARAM w,
LPARAM l)
{

//Обрабатываем нужное нам сообщение
  if (msg == WM_USER+4242 && MainForm->Man)
  {
   pair<WPARAM,LPARAM> param;
   param.first=w;
   param.second=l;
   MainForm->Man->Params.push_back(param);
   if(MainForm->Man->Params.size()>1000)
	MainForm->Man->Params.erase(MainForm->Man->Params.begin());
  }

//Если нам необходимо прекратить дальнейшую обработку сообщения,
//то выходим и возвращаем ноль

//Вызываем старую оконную процедуру,
//которая обработает сообщение.
  return CallWindowProc((FARPROC)MainForm->OldWindowProc, hWnd, msg, w, l);
}
   */
// Инициализаци СУ
// mode == 1 полноценная СУ
// mode == 2 СУ без вставочных нейронов
void TMainForm::CSInit(int mode, int afferentmode, int nummotionselements)
{
 bool res;
 NAContainer *comp;
 string mename;

 // Формируем сеть управления двигателем
 if(mode == 0 && afferentmode==0)
 {
  if(nummotionselements>1)
   mename=string("NEngineControlSignumAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NEngineControlSignumAfferent";
 }
 else
 if(mode == 1 && afferentmode==0)
 {
  if(nummotionselements>1)
   mename=string("NSimpleEngineControlSignumAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NSimpleEngineControlSignumAfferent";
 }
 else
 if(mode == 0 && afferentmode==1)
 {
  if(nummotionselements>1)
   mename=string("NEngineControlRangeAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NEngineControlRangeAfferent";
 }
 else
 if(mode == 1 && afferentmode==1)
 {
  if(nummotionselements>1)
   mename=string("NSimpleEngineControlRangeAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NSimpleEngineControlRangeAfferent";
 }
 else
 if(mode == 0 && afferentmode==2)
 {
  if(nummotionselements>1)
   mename=string("NBranchedEngineControlRangeAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NBranchedEngineControlRangeAfferent";
 }
 else
 if(mode == 1 && afferentmode==2)
 {
  if(nummotionselements>1)
   mename=string("NSimpleBranchedEngineControlRangeAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NSimpleBranchedEngineControlRangeAfferent";
 }
 else
 if(mode == 0 && afferentmode==3)
 {
  if(nummotionselements>1)
   mename=string("NBranchedCrosslinksEngineControlRangeAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NBranchedCrosslinksEngineControlRangeAfferent";
 }
 else
 if(mode == 1 && afferentmode==3)
 {
  if(nummotionselements>1)
   mename=string("NSimpleBranchedCrosslinksEngineControlRangeAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NSimpleBranchedCrosslinksEngineControlRangeAfferent";
 }
 else
 if(mode == 0 && afferentmode==4)
 {
  if(nummotionselements>1)
   mename=string("NIndRangeBranchedEngineControlRangeAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NIndRangeBranchedEngineControlRangeAfferent";
 }
 else
 if(mode == 0 && afferentmode==5)
 {
  if(nummotionselements>1)
   mename=string("NIndRangeBranchedCrosslinksEngineControlRangeAfferent")+RDK::sntoa(nummotionselements);
  else
   mename="NIndRangeBranchedCrosslinksEngineControlRangeAfferent";
 }

 RDK::UEPtr<NANet> net;

// if(Environment->GetModel())
//  net=dynamic_cast<NANet*>((*Environment)->GetComponent("EngineControl"));

 if(!net || net->GetClass() != Storage->GetClassId(mename))
 {
  if(Environment->GetModel())
   Environment->GetModel()->DelAllComponents();
  res=Environment->DestroyModel();
  //Storage->FreeObjectsStorage();

  res=Environment->CreateModel("NModel");

  net=RDK::dynamic_pointer_cast<NANet>(Storage->TakeObject(mename));
 }

 if(!net)
  return;

 net->SetName("EngineControl");

 res=(*Environment)->AddComponent(RDK::static_pointer_cast<RDK::UAContainer>(net));
 ManipulatorTestForm->ControlSystem=net;

 ManipulatorTestForm->IIPosAfferent=RDK::dynamic_pointer_cast<NPulseGenerator>(Storage->TakeObject("NPGenerator"));
 if(ManipulatorTestForm->IIPosAfferent)
 {
  ManipulatorTestForm->IIPosAfferent->SetName("IIPosAfferentGenerator");
  net->AddComponent(ManipulatorTestForm->IIPosAfferent);
 }

 ManipulatorTestForm->IINegAfferent=RDK::dynamic_pointer_cast<NPulseGenerator>(Storage->TakeObject("NPGenerator"));
 if(ManipulatorTestForm->IINegAfferent)
 {
  ManipulatorTestForm->IINegAfferent->SetName("IINegAfferentGenerator");
  net->AddComponent(ManipulatorTestForm->IINegAfferent);
 }

/* if(mode == 0)
 {
  res=net->CreateLink("IIPosAfferentGenerator",0,"MotionElement0.PostAfferent14.PNeuronMembrane.PosChannel.Synapse2");
  res=net->CreateLink("IIPosAfferentGenerator",0,"MotionElement0.PostAfferent24.PNeuronMembrane.NegChannel.Synapse2");
  res=net->CreateLink("IINegAfferentGenerator",0,"MotionElement0.PostAfferent14.PNeuronMembrane.NegChannel.Synapse2");
  res=net->CreateLink("IINegAfferentGenerator",0,"MotionElement0.PostAfferent24.PNeuronMembrane.PosChannel.Synapse2");
 }*/

 // Подключаем управления к мотонейронам
 ManipulatorTestForm->MN1PosControl=RDK::dynamic_pointer_cast<NPulseGenerator>(Storage->TakeObject("NPGenerator"));
 if(ManipulatorTestForm->MN1PosControl)
 {
  ManipulatorTestForm->MN1PosControl->SetName("MN1PosControlGenerator");
  net->AddComponent(ManipulatorTestForm->MN1PosControl);
 }

 ManipulatorTestForm->MN1NegControl=RDK::dynamic_pointer_cast<NPulseGenerator>(Storage->TakeObject("NPGenerator"));
 if(ManipulatorTestForm->MN1NegControl)
 {
  ManipulatorTestForm->MN1NegControl->SetName("MN1NegControlGenerator");
  net->AddComponent(ManipulatorTestForm->MN1NegControl);
 }

// res=net->CreateLink("MN1PosControlGenerator",0,"MotionElement0.Motoneuron1.PNeuronMembrane.PosChannel.Synapse9");
// res=net->CreateLink("MN1PosControlGenerator",0,"MotionElement0.Motoneuron2.PNeuronMembrane.NegChannel.Synapse9");
// res=net->CreateLink("IINegAfferentGenerator",0,"MotionElement0.Motoneuron2.PNeuronMembrane.PosChannel.Synapse9");
// res=net->CreateLink("IINegAfferentGenerator",0,"MotionElement0.Motoneuron1.PNeuronMembrane.NegChannel.Synapse9");

 net->GetFullId(netid);
 ngraph.SetNet(net);
 Environment->AddGraphics(netid,&ngraph);

 if(!res)
  return;
}

//---------------------------------------------------------------------------
__fastcall TMainForm::TMainForm(TComponent* Owner)
		: TForm(Owner)
{
 RDK::UItemData::DefaultDataSize=sizeof(double);
 Storage=static_cast<NStorage*>(RDK::CreateStorage(NewNStorage()));

 list<RDK::UALibrary*> ext_libs;
 ext_libs.push_back(&WindowsActLibrary);
 Environment=static_cast<NEnvironment*>(RDK::CreateEnvironment(NewNEnvironment(),Storage,true,0,&ext_libs));
 NumMotionElements=2;

 SensorStats=0;
 SingleMNFrequency=0;
 DetailedSensorStats=0;
 OutStats=0;
 Man=0;
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::FormShow(TObject *Sender)
{
 NAContainer *cont;

 NumMotionElements=NumMotionElementsComboBox->ItemIndex+1;

 grcanvas.SetRes(1024,768);
 ugraph.SetCanvas(&grcanvas);
 ngraph.SetEngine(&ugraph);


 MuscleTestForm->Show();
 ManipulatorTestForm->Show();
// MuscleControlForm->Show();

// ManipulatorTestForm->IaCheckBox->Checked=true;
// ManipulatorTestForm->IbCheckBox->Checked=true;
// ManipulatorTestForm->IICheckBox->Checked=true;

 Button6Click(Sender);

 MuscleTestForm->SingleMuscleWatchFrame->RestoreInfo("SingleMuscleWatchFrame",false);
 MuscleTestForm->DoubleMuscleWatchFrame->RestoreInfo("DoubleMuscleWatchFrame",false);
 MuscleTestForm->AfferentWatchFrame->RestoreInfo("AfferentWatchFrame",false);
 MuscleTestForm->FBMotoneuronWatchFrame->RestoreInfo("FBMotoneuronWatchFrame",false);
 MuscleTestForm->MotoneuronFrequencyWatchFrame->RestoreInfo("MotoneuronFrequencyWatchFrame",false);
 MuscleTestForm->NetworkWatchFrame->RestoreInfo("NetworkWatchFrame",false);
 MuscleTestForm->FNetworkWatchFrame->RestoreInfo("FNetworkWatchFrame",false);
/*
 String stats;
 stats+=String("RTemp=")+IntToStr(int(NMSDK::RTemp.size()))+"; ";
 stats+=String("PTemp=")+IntToStr(int(NMSDK::PTemp.size()))+"; ";
 stats+=String("LongIdTemp=")+IntToStr(int(NMSDK::LongIdTemp.GetSize()))+"; ";
 stats+=String("NameTemp=")+IntToStr(int(NMSDK::NameTemp.size()))+"; ";

 MySDKIOLabeledEdit->Text=stats+String("LineBuffer=")+IntToStr(int(RDK::LineBuffer.size()));
 MySDKIOLabeledEdit->Repaint();
 */
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::Button3Click(TObject *Sender)
{
 ModelTime=0;
 RealTime=0;
 LastDuration=Timer->Interval;
 StartRealTime=GetTickCount();

 Timer->Enabled=true;
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::Button4Click(TObject *Sender)
{
 Timer->Enabled=false;
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::FormClose(TObject *Sender, TCloseAction &Action)
{
 Timer->Enabled=false;

 MuscleTestForm->SingleMuscleWatchFrame->CollectInfo("SingleMuscleWatchFrame",false);
 MuscleTestForm->DoubleMuscleWatchFrame->CollectInfo("DoubleMuscleWatchFrame",false);
 MuscleTestForm->AfferentWatchFrame->CollectInfo("AfferentWatchFrame",false);
 MuscleTestForm->FBMotoneuronWatchFrame->CollectInfo("FBMotoneuronWatchFrame",false);
 MuscleTestForm->MotoneuronFrequencyWatchFrame->CollectInfo("MotoneuronFrequencyWatchFrame",false);
 MuscleTestForm->NetworkWatchFrame->CollectInfo("NetworkWatchFrame",false);
 MuscleTestForm->FNetworkWatchFrame->CollectInfo("FNetworkWatchFrame",false);

 if(Storage)
 {
  Storage->ClearObjectsStorage();
  delete Storage;
  Storage=0;
 }

 if(Environment)
 {
  delete Environment;
  Environment=0;
 }
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::TimerTimer(TObject *Sender)
{
 Timer->Enabled=false;

 StartProcTime=GetTickCount();

 CurrentTime=GetTickCount();


 unsigned int curtime;
 real devicemodeltime=0;

 int i=0;
 if(LastDuration < Timer->Interval)
  LastDuration=Timer->Interval;
 int elapsed_counter=(1000*(*Environment)->GetTimeStep())/LastDuration;

// for(int i=0;i<(*Environment)->TimeStep()/5;i++)
 curtime=GetTickCount();
 while(curtime-CurrentTime<Timer->Interval && i<elapsed_counter)
 {
  NWPhysicalManipulator *engine_input=RDK::dynamic_pointer_cast<NWPhysicalManipulator>(ManipulatorTestForm->ControlSystem->GetComponent("WPhysicalManipulator"));
  if(engine_input && engine_input->DLLManipulatorSetExternalData && engine_input->EmulatorMode)
  {
   engine_input->DLLManipulatorSetExternalData(StrToFloat(ManipulatorTestForm->ExtMomentEdit->Text),StatisticForm->StatsTime);
   devicemodeltime=engine_input->DLLManipulatorGetModelTime();
  }

  Environment->Calculate();
  StatisticForm->StatsTime+=1.0/(*Environment)->GetTimeStep();


  if(!(i%10))
  {
   if(MuscleTestForm->Visible)
   {
	MuscleTestForm->SingleMuscleWatchFrame->StepUpdate();
	MuscleTestForm->AfferentWatchFrame->StepUpdate();
	MuscleTestForm->FBMotoneuronWatchFrame->StepUpdate();
	MuscleTestForm->MotoneuronFrequencyWatchFrame->StepUpdate();
	MuscleTestForm->NetworkWatchFrame->StepUpdate();

//	if(SourcesControlForm->Visible)
//	 SourcesControlForm->NSourceControlFrame->StepUpdate();

   }
  }
  ++i;
  curtime=GetTickCount();
 }
 ManipulatorTestForm->UpdateInterface();

   if(MuscleTestForm->Visible)
   {
	MuscleTestForm->SingleMuscleWatchFrame->StepUpdate();
	MuscleTestForm->AfferentWatchFrame->StepUpdate();
	MuscleTestForm->FBMotoneuronWatchFrame->StepUpdate();
	MuscleTestForm->MotoneuronFrequencyWatchFrame->StepUpdate();
	MuscleTestForm->NetworkWatchFrame->StepUpdate();

//	if(SourcesControlForm->Visible)
//	 SourcesControlForm->NSourceControlFrame->StepUpdate();

   }

 engine=ManipulatorTestForm->Engine;
 str=" [Ia=";
 str+=FloatToStrF(engine->GetOutputData(2).Double[0],ffFixed,3,3);
 str+=" : Ib=";
 str+=FloatToStrF(engine->GetOutputData(0).Double[0],ffFixed,3,3);
 str+=" : II=";
 str+=FloatToStrF(engine->GetOutputData(1).Double[0],ffFixed,3,3);
 str+="]";
 ManipulatorTestForm->EngineOutputsLabeledEdit->Text=str;
 ManipulatorTestForm->EngineOutputsLabeledEdit->Repaint();

  if(ManipulatorTestForm->RadioGroup1->ItemIndex == 0)
  {
   NADItem *engine_input=RDK::static_pointer_cast<NADItem>(ManipulatorTestForm->ControlSystem->GetComponent("Pac"));
   if(engine_input)
   {
	ManipulatorTestForm->VoltageLabeledEdit->Text=FloatToStrF(engine_input->GetOutputData(0).Double[0],ffFixed,3,3);
	ManipulatorTestForm->ControlDurationLabeledEdit->Text="";
   }
  }
  else
  {
   NWPhysicalManipulator *engine_input=RDK::static_pointer_cast<NWPhysicalManipulator>(ManipulatorTestForm->ControlSystem->GetComponent("WPhysicalManipulator"));
   if(engine_input)
   {
	ManipulatorTestForm->VoltageLabeledEdit->Text=FloatToStrF(engine_input->InputVoltage,ffFixed,3,3)+
			" -> "+FloatToStrF(engine_input->OutputVoltage,ffFixed,3,3);
	ManipulatorTestForm->ControlDurationLabeledEdit->Text=IntToStr(int(engine_input->LastDuration));
   }
  }

 // Расчет статистики
 double angle=engine->GetOutputData(1).Double[0];
 if(StatisticForm->MinAngle == 0 && StatisticForm->MaxAngle == 0)
  StatisticForm->MinAngle=StatisticForm->MaxAngle=angle;

 if(StatisticForm->MinAngle>angle)
  StatisticForm->MinAngle=angle;

 if(StatisticForm->MaxAngle<angle)
  StatisticForm->MaxAngle=angle;

 if(StatisticForm->MaxSpeed<fabs(engine->GetOutputData(2).Double[0]))
  StatisticForm->MaxSpeed=fabs(engine->GetOutputData(2).Double[0]);

 StatisticForm->NumStats+=1;
 StatisticForm->SumSpeed+=fabs(engine->GetOutputData(2).Double[0]);


// StatisticForm->UpdateInterface();

 StopProcTime=GetTickCount();
 LastSentTime=GetTickCount();
 LastDuration=LastSentTime-CurrentTime;

 RealTime=GetTickCount()-StartRealTime;
 ModelTime=(*Environment)->GetDoubleTime();
 if(RealTime/1000.0<ModelTime)
 {
  Sleep(ModelTime*1000-RealTime);
  RealTime=GetTickCount()-StartRealTime;
 }

 ManipulatorTestForm->TimeLabeledEdit->Text=String("Model=")+FloatToStrF(ModelTime,ffFixed,3,3)+
						String(" Real=")+FloatToStrF(RealTime/1000.0,ffFixed,3,3)+
						String(" D=")+FloatToStrF(StopProcTime-StartProcTime,ffFixed,3,3)+
						String(" DModel=")+FloatToStrF(devicemodeltime,ffFixed,3,3);


 Timer->Enabled=true;
}
//---------------------------------------------------------------------------



//---------------------------------------------------------------------------

void __fastcall TMainForm::Button6Click(TObject *Sender)
{
 if(CSModeRadioGroup->ItemIndex < 0)
  return;

 if(AfferentModeComboBox->ItemIndex <0)
  return;

 CSInit(CSModeRadioGroup->ItemIndex,AfferentModeComboBox->ItemIndex,NumMotionElements);

 RDK::UEPtr<NANet> net=RDK::dynamic_pointer_cast<NANet>((*Environment)("EngineControl"));

 if(!net)
  return;

 (*Environment)->SetTimeStep(1000);
 RDK::UAContainer *cont=0;

 // Контроллеры
// NCMySDKWatchFrame* controller=0;
 Environment->DelAllControllers();

 MuscleTestForm->SingleMuscleWatchFrame->Clear();
 MuscleTestForm->DoubleMuscleWatchFrame->Clear();
 MuscleTestForm->AfferentWatchFrame->Clear();
 MuscleTestForm->FBMotoneuronWatchFrame->Clear();
 MuscleTestForm->MotoneuronFrequencyWatchFrame->Clear();
 MuscleTestForm->NetworkWatchFrame->Clear();
 MuscleTestForm->FNetworkWatchFrame->Clear();

 MuscleTestForm->SingleMuscleWatchFrame->Reset();
 MuscleTestForm->DoubleMuscleWatchFrame->Reset();
 MuscleTestForm->AfferentWatchFrame->Reset();
 MuscleTestForm->FBMotoneuronWatchFrame->Reset();
 MuscleTestForm->MotoneuronFrequencyWatchFrame->Reset();
 MuscleTestForm->NetworkWatchFrame->Reset();
 MuscleTestForm->FNetworkWatchFrame->Reset();

 // Заполняем графики
 int i=1,j=0;

 real ampl=1, dist=0.25;

 int aff=1;
 WatchInterval=StrToFloat(WatchIntervalLabeledEdit->Text);
 FWatchInterval=1000;

 CacheSize=(1000/WatchInterval>0)?1000/WatchInterval:1;
 MuscleTestForm->SingleMuscleWatchFrame->SetCacheSize(CacheSize);
 MuscleTestForm->DoubleMuscleWatchFrame->SetCacheSize(CacheSize);
 MuscleTestForm->NetworkWatchFrame->SetCacheSize(CacheSize);
 MuscleTestForm->MotoneuronFrequencyWatchFrame->SetCacheSize(CacheSize);
 MuscleTestForm->FBMotoneuronWatchFrame->SetCacheSize(CacheSize);
 MuscleTestForm->AfferentWatchFrame->SetCacheSize(CacheSize);

 // Наблюдения
 cont=net->GetComponent("Engine");

 AddWatch(MuscleTestForm->SingleMuscleWatchFrame, cont,0,0,WatchInterval,0,psDashDot);
 AddWatch(MuscleTestForm->SingleMuscleWatchFrame, cont,1,0,WatchInterval,0,psDashDot);
 AddWatch(MuscleTestForm->SingleMuscleWatchFrame, cont,2,0,WatchInterval,0,psDashDot);
 cont=net->GetComponent("Pac");
 AddWatch(MuscleTestForm->SingleMuscleWatchFrame, cont,0,0,WatchInterval,0,psSolid);
 cont=net->GetComponent("EngineMoment");
 AddWatch(MuscleTestForm->SingleMuscleWatchFrame, cont,0,0,WatchInterval,0,psDot);

/* cont=net->GetComponent("IIPosAfferentGenerator");
 AddWatch(MuscleTestForm->SingleMuscleWatchFrame, cont,1,0,WatchInterval,0,psDot);
 cont=net->GetComponent("IINegAfferentGenerator");
 AddWatch(MuscleTestForm->SingleMuscleWatchFrame, cont,1,0,WatchInterval,0,psDot);
  */

 cont=net->GetComponent("AfferentSource1");
 AddWatch(MuscleTestForm->DoubleMuscleWatchFrame, cont,0,0,WatchInterval,0,psDash);
 MuscleControlForm->AfferentSource1=((NConstGenerator*)cont);

 cont=net->GetComponent("AfferentSource2");
 AddWatch(MuscleTestForm->DoubleMuscleWatchFrame, cont,0,0,WatchInterval,0,psDot);
 MuscleControlForm->AfferentSource2=((NConstGenerator*)cont);

 cont=net->GetComponent("LengthSource1");
 AddWatch(MuscleTestForm->DoubleMuscleWatchFrame, cont,0,0,WatchInterval,0,psDot);
 MuscleControlForm->Length1=((NConstGenerator*)cont);

 cont=net->GetComponent("Renshow1ActivatorGenerator");
 AddWatch(MuscleTestForm->NetworkWatchFrame, cont,0,0,WatchInterval,(ampl+dist)*(j++),psSolid);
 MuscleControlForm->Renshow1Activator=((NPulseGenerator*)cont);

 cont=net->GetComponent("Renshow2ActivatorGenerator");
 AddWatch(MuscleTestForm->NetworkWatchFrame, cont,0,0,WatchInterval,(ampl+dist)*(j++),psSolid);
 MuscleControlForm->Renshow2Activator=((NPulseGenerator*)cont);

 cont=net->GetComponent("Renshow1DeactivatorGenerator");
 AddWatch(MuscleTestForm->NetworkWatchFrame, cont,0,0,WatchInterval,(ampl+dist)*(j++),psSolid);
 MuscleControlForm->Renshow1Deactivator=((NPulseGenerator*)cont);

 cont=net->GetComponent("Renshow2DeactivatorGenerator");
 AddWatch(MuscleTestForm->NetworkWatchFrame, cont,0,0,WatchInterval,(ampl+dist)*(j++),psSolid);
 MuscleControlForm->Renshow2Deactivator=((NPulseGenerator*)cont);

 cont=net->GetComponent("NFrequencyReceiver");
 AddFrequencyWatch(MuscleTestForm->MotoneuronFrequencyWatchFrame, cont,FWatchInterval,0,psSolid);

 cont=net->GetComponent("Motoneuron2FrequencyReceiver");
 AddFrequencyWatch(MuscleTestForm->MotoneuronFrequencyWatchFrame, cont,FWatchInterval,0,psDot);

// cont=net->GetComponent("Engine");
// ManipulatorTestForm->Engine=(NDCEngine*)cont;

 cont=net->GetComponent("NManipulatorSourceEmulator1");
 ManipulatorTestForm->Engine=(NManipulatorSource*)cont;

 cont=net->GetComponent("EngineVoltage");
 ManipulatorTestForm->Source=(NConstGenerator*)cont;

 receptor.resize(NumMotionElements);
 Separators.resize(NumMotionElements);
 for(int n=0;n<NumMotionElements;n++)
 {
  receptor[n].resize(6);
  Separators[n].resize(6);
  cont=net->GetComponent(string("MotionElement")+RDK::sntoa(n));
  MuscleControlForm->Net=dynamic_cast<NANet*>(cont);

  if(n==0)
  {
  AddWatch(WatchWindowForm->WatchFrame, cont->GetComponentL("Motoneuron1.LTZone"),0,0,WatchInterval,(ampl+dist)*(i++)+ampl,psSolid);
  AddWatch(MuscleTestForm->FBMotoneuronWatchFrame, cont->GetComponentL("Motoneuron1.LTZone"),0,0,WatchInterval,(ampl+dist)*6,psSolid);
  AddWatch(MuscleTestForm->FBMotoneuronWatchFrame, cont->GetComponentL("Renshow1.LTZone"),0,0,WatchInterval,(ampl+dist)*5,psDot);
  AddWatch(MuscleTestForm->NetworkWatchFrame, cont->GetComponentL("Motoneuron1.LTZone"),0,0,WatchInterval,(ampl+dist)*(j++),psSolid);

  AddWatch(WatchWindowForm->WatchFrame, cont->GetComponentL("Motoneuron2.LTZone"),0,0,WatchInterval,(ampl+dist)*(i++)+ampl,psSolid);
  AddWatch(MuscleTestForm->FBMotoneuronWatchFrame, cont->GetComponentL("Motoneuron2.LTZone"),0,0,WatchInterval,(ampl+dist)*4,psSolid);
  AddWatch(MuscleTestForm->FBMotoneuronWatchFrame, cont->GetComponentL("Renshow2.LTZone"),0,0,WatchInterval,(ampl+dist)*3,psDot);
  AddWatch(MuscleTestForm->NetworkWatchFrame, cont->GetComponentL("Motoneuron2.LTZone"),0,0,WatchInterval,(ampl+dist)*(j++),psSolid);

  AddWatch(WatchWindowForm->WatchFrame, cont->GetComponentL("Afferent_Ia1.LTZone"),0,0,WatchInterval,(ampl+dist)*(i++)+ampl);
  AddWatch(MuscleTestForm->AfferentWatchFrame, cont->GetComponentL("Afferent_Ia1.LTZone"),0,0,WatchInterval,(ampl+dist)*(aff++)+ampl,psDot,clRed);
  AddWatch(MuscleTestForm->NetworkWatchFrame, cont->GetComponentL("Renshow1.LTZone"),0,0,WatchInterval,(ampl+dist)*(j++),psSolid,clRed);
  AddWatch(MuscleTestForm->AfferentWatchFrame, cont->GetComponentL("Afferent_Ib1.LTZone"),0,0,WatchInterval,(ampl+dist)*(aff++)+ampl,psSolid,clRed);
  AddWatch(MuscleTestForm->AfferentWatchFrame, cont->GetComponentL("Afferent_II1.LTZone"),0,0,WatchInterval,(ampl+dist)*(aff++)+ampl,psSolid,clRed);

  AddWatch(WatchWindowForm->WatchFrame, cont->GetComponentL("Afferent_Ia2.LTZone"),0,0,WatchInterval,(ampl+dist)*(i++)+ampl);
  AddWatch(MuscleTestForm->AfferentWatchFrame, cont->GetComponentL("Afferent_Ia2.LTZone"),0,0,WatchInterval,(ampl+dist)*(aff++)+ampl,psDash,clGreen);
  AddWatch(MuscleTestForm->NetworkWatchFrame, cont->GetComponentL("Renshow2.LTZone"),0,0,WatchInterval,(ampl+dist)*(j++),psSolid,clGreen);
  AddWatch(MuscleTestForm->AfferentWatchFrame, cont->GetComponentL("Afferent_Ib2.LTZone"),0,0,WatchInterval,(ampl+dist)*(aff++)+ampl,psSolid,clGreen);
  AddWatch(MuscleTestForm->AfferentWatchFrame, cont->GetComponentL("Afferent_II2.LTZone"),0,0,WatchInterval,(ampl+dist)*(aff++)+ampl,psSolid,clGreen);
  // Конец заполнения графиков
  }

  receptor[n][0]=RDK::dynamic_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_Ia1.Receptor"));
  receptor[n][1]=RDK::dynamic_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_Ia2.Receptor"));
  receptor[n][2]=RDK::dynamic_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_Ib1.Receptor"));
  receptor[n][3]=RDK::dynamic_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_Ib2.Receptor"));
  receptor[n][4]=RDK::dynamic_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_II1.Receptor"));
  receptor[n][5]=RDK::dynamic_pointer_cast<NReceptor>(cont->GetComponentL("Afferent_II2.Receptor"));

  Separators[n][0]=RDK::dynamic_pointer_cast<NIntervalSeparator>(net->GetComponentL(string("Ia_PosIntervalSeparator")+RDK::sntoa(n+1)));
  Separators[n][1]=RDK::dynamic_pointer_cast<NIntervalSeparator>(net->GetComponentL(string("Ia_NegIntervalSeparator")+RDK::sntoa(n+1)));
  Separators[n][2]=RDK::dynamic_pointer_cast<NIntervalSeparator>(net->GetComponentL(string("Ib_PosIntervalSeparator")+RDK::sntoa(n+1)));
  Separators[n][3]=RDK::dynamic_pointer_cast<NIntervalSeparator>(net->GetComponentL(string("Ib_NegIntervalSeparator")+RDK::sntoa(n+1)));
  Separators[n][4]=RDK::dynamic_pointer_cast<NIntervalSeparator>(net->GetComponentL(string("II_PosIntervalSeparator")+RDK::sntoa(n+1)));
  Separators[n][5]=RDK::dynamic_pointer_cast<NIntervalSeparator>(net->GetComponentL(string("II_NegIntervalSeparator")+RDK::sntoa(n+1)));
 }

 engine=ManipulatorTestForm->Engine;//RDK::static_pointer_cast<NADItem*>(net->GetComponentL("Engine"));

/* bool ICheckBoxes[3];
 ICheckBoxes[0]=ManipulatorTestForm->IaCheckBox->Checked;
 ICheckBoxes[1]=ManipulatorTestForm->IbCheckBox->Checked;
 ICheckBoxes[2]=ManipulatorTestForm->IICheckBox->Checked;

 ManipulatorTestForm->IaCheckBox->Checked=false;
 ManipulatorTestForm->IbCheckBox->Checked=false;
 ManipulatorTestForm->IICheckBox->Checked=false;
 ManipulatorTestForm->IaCheckBox->Checked=ICheckBoxes[0];
 ManipulatorTestForm->IbCheckBox->Checked=ICheckBoxes[1];
 ManipulatorTestForm->IICheckBox->Checked=ICheckBoxes[2];  */
 ManipulatorTestForm->IICheckBoxClick(Sender);
 ManipulatorTestForm->IaCheckBoxClick(Sender);
 ManipulatorTestForm->IbCheckBoxClick(Sender);
 ManipulatorTestForm->ControlVoltageCheckBoxClick(Sender);

 CSelected=Environment->GetModel();
 CSelectedRegistry.Clear();
// CSelected->Save(CSelectedRegistry);
 ClassRegistryFrame->SetRegistry(&CSelectedRegistry);

 ManipulatorTestForm->MomentTrackBar->Position=0;
 bool res=false;

 if(!Man)
 {
  Man=RDK::dynamic_pointer_cast<NWPhysicalManipulator>(Storage->TakeObject("NWPhysicalManipulator"));
  Man->WindowHandle=Handle;
  Man->LoadManipulatorDll();
 }
 else
 {
  if(Man)
  {
   Man->DisconnectAll();
   Man->DisconnectAllItems();
  }
 }

 if(!Man)
  return;


  // Связи с интерфейсом физического манипулятора
  res=net->AddComponent(Man);
  Man->SetActivity(true);
 //Man->Reset();


 res=net->CreateLink("WPhysicalManipulator",0,"NManipulatorSource1",0);
 res=net->CreateLink("WPhysicalManipulator",1,"NManipulatorSource1",1);
 res=net->CreateLink("WPhysicalManipulator",2,"NManipulatorSource1",2);
 res=net->CreateLink("NManipulatorInput1",0,"WPhysicalManipulator",0);

 // Связываем все управляющие элементы
 int motion_elements=RDK::dynamic_pointer_cast<NEngineMotionControl>(net)->NumMotionElements;
 for(int i=0;i<motion_elements;i++)
 {
  res&=net->CreateLink(string("MotionElement")+RDK::sntoa(i)
	+".Motoneuron1.LTZone",0,string("WPhysicalManipulator"));
  res&=net->CreateLink(string("MotionElement")+RDK::sntoa(i)
	+".Motoneuron2.LTZone",0,string("WPhysicalManipulator"));
/*  res&=(*Environment)->CreateLink(string("EngineControl.MotionElement")+RDK::sntoa(i)
	+".Motoneuron1.LTZone",0,string("WPhysicalManipulator"));
  res&=(*Environment)->CreateLink(string("EngineControl.MotionElement")+RDK::sntoa(i)
	+".Motoneuron2.LTZone",0,string("WPhysicalManipulator"));
 */
 }


 // Настраиваем статистику
 if(!SensorStats)
 {
  SensorStats=RDK::dynamic_pointer_cast<NSimpleStatistic>(Storage->TakeObject("NSimpleStatistic"));
 }
 else
 {
  if(SensorStats)
  {
   SensorStats->DisconnectAll();
   SensorStats->DisconnectAllItems();
  }
 }
 SensorStats->SetName("Sensors");
 SensorStats->StatsInterval=1;
 res=net->AddComponent(SensorStats);
 if(ManipulatorTestForm->RadioGroup1->ItemIndex == 0)
 {
  res=net->CreateLink("Engine",2,"Sensors",2); // скорость
  res=net->CreateLink("Engine",1,"Sensors",1); // угол
  res=net->CreateLink("Engine",0,"Sensors",0); // момент
 }
 else
 {
  res=net->CreateLink("WPhysicalManipulator",2,"Sensors",2);
  res=net->CreateLink("WPhysicalManipulator",1,"Sensors",1);
  res=net->CreateLink("WPhysicalManipulator",0,"Sensors",0);
 }
 SensorStats->Headers.resize(3*4);
 SensorStats->Headers[0]="Min(Sp)";
 SensorStats->Headers[1]="Max(Sp)";
 SensorStats->Headers[2]="Avg(Sp)";
 SensorStats->Headers[3]="Dlt(Sp)";
 SensorStats->Headers[4]="Min(An)";
 SensorStats->Headers[5]="Max(An)";
 SensorStats->Headers[6]="Avg(An)";
 SensorStats->Headers[7]="Dlt(An)";
 SensorStats->Headers[8]="Min(Mm)";
 SensorStats->Headers[9]="Max(Mm)";
 SensorStats->Headers[10]="Avg(Mm)";
 SensorStats->Headers[11]="Dlt(Mm)";


 SensorStats->SetActivity(true);
 SensorStats->ReCreateFile();

 if(!OutStats)
 {
  OutStats=RDK::dynamic_pointer_cast<NSimpleStatistic>(Storage->TakeObject("NSimpleStatistic"));
 }
 else
 {
  if(OutStats)
  {
   OutStats->DisconnectAll();
   OutStats->DisconnectAllItems();
  }
 }
 OutStats->StatsInterval=1;
 OutStats->SetName("Effectors");
 res=net->AddComponent(OutStats);
 if(ManipulatorTestForm->RadioGroup1->ItemIndex == 0)
 {
  res=net->CreateLink("NManipulatorInputEmulator1",0,"Effectors",0);
 }
 else
 {
  res=net->CreateLink("NManipulatorInput1",0,"Effectors",0);
 }
 OutStats->Headers.resize(4);
 OutStats->Headers[0]="Min(V)";
 OutStats->Headers[1]="Max(V)";
 OutStats->Headers[2]="Avg(V)";
 OutStats->Headers[3]="Dlt(V)";
 OutStats->SetActivity(true);
 OutStats->ReCreateFile();


 if(!DetailedSensorStats)
 {
  DetailedSensorStats=RDK::dynamic_pointer_cast<NSimpleStatistic>(Storage->TakeObject("NSimpleStatistic"));
 }
 else
 {
  if(DetailedSensorStats)
  {
   DetailedSensorStats->DisconnectAll();
   DetailedSensorStats->DisconnectAllItems();
  }
 }
 DetailedSensorStats->SetName("DetailedSensors");
 DetailedSensorStats->StatsInterval=1;
 res=net->AddComponent(DetailedSensorStats);
 DetailedSensorStats->Headers.resize(net->GetNumOutputs()*3);
 for(int i=net->GetNumOutputs()-1;i>=0;i--)
 {
  res=(*Environment)->CreateLink("EngineControl",i,"EngineControl.DetailedSensors",i);
 }
 DetailedSensorStats->Headers[0*3+0]="Min(N[Ia1])";
 DetailedSensorStats->Headers[0*3+1]="Max(N[Ia1])";
 DetailedSensorStats->Headers[0*3+2]="Avg(N[Ia1])";

 DetailedSensorStats->Headers[1*3+0]="Min(N[Ia2])";
 DetailedSensorStats->Headers[1*3+1]="Max(N[Ia2])";
 DetailedSensorStats->Headers[1*3+2]="Avg(N[Ia2])";

 DetailedSensorStats->Headers[2*3+0]="Min(N[Ib1])";
 DetailedSensorStats->Headers[2*3+1]="Max(N[Ib1])";
 DetailedSensorStats->Headers[2*3+2]="Avg(N[Ib1])";

 DetailedSensorStats->Headers[3*3+0]="Min(N[Ib2])";
 DetailedSensorStats->Headers[3*3+1]="Max(N[Ib2])";
 DetailedSensorStats->Headers[3*3+2]="Avg(N[Ib2])";

 DetailedSensorStats->Headers[4*3+0]="Min(N[II1])";
 DetailedSensorStats->Headers[4*3+1]="Max(N[II1])";
 DetailedSensorStats->Headers[4*3+2]="Avg(N[II1])";

 DetailedSensorStats->Headers[5*3+0]="Min(N[II2])";
 DetailedSensorStats->Headers[5*3+1]="Max(N[II2])";
 DetailedSensorStats->Headers[5*3+2]="Avg(N[II2])";

 DetailedSensorStats->SetActivity(true);
 DetailedSensorStats->ReCreateFile();

 int oldsize=FFH.size();
 int newsize=RDK::dynamic_pointer_cast<NEngineMotionControl>(net)->NumMotionElements*2;
 FFH.resize(newsize);
 for(int i=oldsize;i<newsize;i++)
  FFH[i]=0;

 for(size_t i=0;i<FFH.size()/2;i++)
 {
  if(!FFH[i])
  {
   FFH[i]=RDK::dynamic_pointer_cast<NSimpleStatistic>(Storage->TakeObject("NSimpleStatistic"));
  }
  else
  {
   if(FFH[i])
   {
	FFH[i]->DisconnectAll();
	FFH[i]->DisconnectAllItems();
   }
  }
  FFH[i]->SetName(string("PosMN_FFH_")+RDK::sntoa(i));
  FFH[i]->StatsInterval=1;
  FFH[i]->Mode=1;
  res=net->AddComponent(FFH[i]);
  res=(*Environment)->CreateLink(string("EngineControl")+string(".PosMNFrequencyReceiver")+RDK::sntoa(i),0,string("EngineControl.")+FFH[i]->GetName(),0);
  res=(*Environment)->CreateLink(string("EngineControl")+string(".PosMNFrequencyReceiver")+RDK::sntoa(i),1,string("EngineControl.")+FFH[i]->GetName(),1);
  FFH[i]->Headers.resize(2);
  FFH[i]->Headers[0]="<First Line - Freqency Value>";
  FFH[i]->Headers[1]="<Second Line - Number of registrations from Time=0>";

  FFH[i]->SetActivity(true);
  FFH[i]->ReCreateFile();
 }

 for(size_t i=FFH.size()/2;i<FFH.size();i++)
 {
  if(!FFH[i])
  {
   FFH[i]=RDK::dynamic_pointer_cast<NSimpleStatistic>(Storage->TakeObject("NSimpleStatistic"));
  }
  else
  {
   if(FFH[i])
   {
	FFH[i]->DisconnectAll();
	FFH[i]->DisconnectAllItems();
   }
  }
  FFH[i]->SetName(string("NegMN_FFH_")+RDK::sntoa((i)-FFH.size()/2));
  FFH[i]->StatsInterval=1;
  FFH[i]->Mode=1;

  res=net->AddComponent(FFH[i]);
  res=(*Environment)->CreateLink(string("EngineControl")+string(".NegMNFrequencyReceiver")+RDK::sntoa((i)-FFH.size()/2),0,string("EngineControl.")+FFH[i]->GetName(),0);
  res=(*Environment)->CreateLink(string("EngineControl")+string(".NegMNFrequencyReceiver")+RDK::sntoa((i)-FFH.size()/2),1,string("EngineControl.")+FFH[i]->GetName(),1);

  FFH[i]->Headers.resize(2);
  FFH[i]->Headers[0]="<First Line - Freqency Value>";
  FFH[i]->Headers[1]="<Second Line - Number of registrations from Time=0>";

  FFH[i]->SetActivity(true);
  FFH[i]->ReCreateFile();
 }

// SingleMNFrequency
 if(!SingleMNFrequency)
 {
  SingleMNFrequency=RDK::dynamic_pointer_cast<NSimpleStatistic>(Storage->TakeObject("NSimpleStatistic"));
 }
 else
 {
  if(SingleMNFrequency)
  {
   SingleMNFrequency->DisconnectAll();
   SingleMNFrequency->DisconnectAllItems();
  }
 }
 SingleMNFrequency->SetName("SingleMNFrequency");
 SingleMNFrequency->StatsInterval=1;
 SingleMNFrequency->Mode=2;
 res=net->AddComponent(SingleMNFrequency);
 motion_elements=RDK::dynamic_pointer_cast<NEngineMotionControl>(net)->NumMotionElements;
 SingleMNFrequency->Headers.resize(motion_elements*2);
 for(int i=0;i<motion_elements;i++)
 {
  res=(*Environment)->CreateLink(string("EngineControl.MotionElement")+RDK::sntoa(i)
	+".Motoneuron1.LTZone",2,string("EngineControl.")+SingleMNFrequency->GetName());
  SingleMNFrequency->Headers[i]=string("Me")+RDK::sntoa(i)+"_MN1";
 }
 for(int i=0;i<motion_elements;i++)
 {
  res=(*Environment)->CreateLink(string("EngineControl.MotionElement")+RDK::sntoa(i)
	+".Motoneuron2.LTZone",2,string("EngineControl.")+SingleMNFrequency->GetName());
  SingleMNFrequency->Headers[motion_elements+i]=string("Me")+RDK::sntoa(i)+"_MN2";
 }

 SingleMNFrequency->SetActivity(true);
 SingleMNFrequency->ReCreateFile();


// MNFrequency
/* oldsize=MNFrequency.size();
 newsize=RDK::dynamic_pointer_cast<NEngineMotionControl*>(net)->NumMotionElements*2;
 MNFrequency.resize(newsize);
 for(size_t i=oldsize;i<newsize;i++)
  MNFrequency[i]=0;
 for(size_t i=0;i<MNFrequency.size()/2;i++)
 {
  if(!MNFrequency[i])
  {
   MNFrequency[i]=RDK::dynamic_pointer_cast<NSimpleStatistic*>(Storage->TakeObject("NSimpleStatistic"));
  }
  else
  {
   if(MNFrequency[i])
   {
	MNFrequency[i]->DisconnectAll();
	MNFrequency[i]->DisconnectAllItems();
   }
  }
  MNFrequency[i]->Name=string("PosMN_Frequency_")+RDK::sntoa(i+1);
  MNFrequency[i]->StatsInterval=1;
  MNFrequency[i]->Mode=2;
  res=net->AddComponent(MNFrequency[i]);
  res=(*Environment)->CreateLink(string("EngineControl.MotionElement")+RDK::sntoa(i+1)
	+".Motoneuron1.LTZone",2,string("EngineControl.")+MNFrequency[0]->Name);
  MNFrequency[i]->Activity=true;
  MNFrequency[i]->ReCreateFile();
 }

 for(size_t i=MNFrequency.size()/2;i<MNFrequency.size();i++)
 {
  if(!MNFrequency[i])
  {
   MNFrequency[i]=RDK::dynamic_pointer_cast<NSimpleStatistic*>(Storage->TakeObject("NSimpleStatistic"));
  }
  else
  {
   if(MNFrequency[i])
   {
	MNFrequency[i]->DisconnectAll();
	MNFrequency[i]->DisconnectAllItems();
   }
  }
  MNFrequency[i]->Name=string("NegMN_Frequency_")+RDK::sntoa((i+1)-MNFrequency.size()/2);
  MNFrequency[i]->StatsInterval=1;
  MNFrequency[i]->Mode=2;

  res=net->AddComponent(MNFrequency[i]);
  res=(*Environment)->CreateLink(string("EngineControl.MotionElement")+RDK::sntoa((i+1)-MNFrequency.size()/2)
	+".Motoneuron2.LTZone",2,string("EngineControl.")+MNFrequency[0]->Name);
  MNFrequency[i]->Activity=true;
  MNFrequency[i]->ReCreateFile();
 }
				*/
 Environment->Reset();

 ManipulatorTestForm->EmulatorCheckBoxClick(Sender);
 ManipulatorTestForm->VoltageMulTrackBarChange(Sender);
 ManipulatorTestForm->TimeDurationTrackBarChange(Sender);
 ManipulatorTestForm->PACDeactivatorTimeTrackBarChange(Sender);
 ManipulatorTestForm->PACActivatorTimeTrackBarChange(Sender);
 ManipulatorTestForm->RadioGroup1Click(Sender);
 if(!res)
  return;
}
//---------------------------------------------------------------------------


void __fastcall TMainForm::ClassRegistryFrame1SetBitBtnClick(TObject *Sender)
{
 ClassRegistryFrame->SetBitBtnClick(Sender);

// CSelected->Load(CSelectedRegistry,0,true);
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::Button2Click(TObject *Sender)
{
 NGraphics *gr=Environment->GetGraphics(netid);

 if(gr)
 {
  gr->BuildDestinations();
  gr->Draw();
 }

 grcanvas>>GraphicsForm->Image->Picture->Bitmap;
 GraphicsForm->Image->Repaint();
 GraphicsForm->Show();
}
//---------------------------------------------------------------------------



void __fastcall TMainForm::ClassRegistryFrameSetBitBtnClick(TObject *Sender)
{
 ClassRegistryFrame->SetBitBtnClick(Sender);
 ClassRegistryFrame->UpdateInterface();

// CSelected->Load(ClassRegistryFrame->GetDiffRegistry()->operator[](0),0,true);
 CSelectedRegistry.Clear();
// CSelected->Save(CSelectedRegistry);
 ClassRegistryFrame->SetRegistry(&CSelectedRegistry);
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::CSModeRadioGroupClick(TObject *Sender)
{
 Button4Click(Sender);
 Button6Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::ClassRegistryFrameLabeledEditKeyPress(TObject *Sender,
          wchar_t &Key)
{
  ClassRegistryFrame->LabeledEditKeyPress(Sender,Key);

  if(Key == VK_RETURN)
  {
   ClassRegistryFrame->UpdateInterface();

//   CSelected->Load(ClassRegistryFrame->GetDiffRegistry()->operator[](0),0,true);
   CSelectedRegistry.Clear();
//   CSelected->Save(CSelectedRegistry);
   ClassRegistryFrame->SetRegistry(&CSelectedRegistry);
  }
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::LinksButtonClick(TObject *Sender)
{
 LinksForm->NLinksFrame->Init(Environment->GetModel());
 LinksForm->Show();
}
//---------------------------------------------------------------------------



void __fastcall TMainForm::AfferentModeRadioGroupClick(TObject *Sender)
{
 Button4Click(Sender);
 Button6Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::NumMotionElementsComboBoxSelect(TObject *Sender)
{
 NumMotionElements=NumMotionElementsComboBox->ItemIndex+1;
 Button4Click(Sender);
 Button6Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::Button1Click(TObject *Sender)
{
 //try {
  throw new RDK::UPtr<int>::UFEUsingZeroPtr();

 /*}
	catch (RDK::UPtr<int>::UFEUsingZeroPtr *exception)
	{
	 Application->MessageBox(L"RDK::UPtr<int>::UFEUsingZeroPtr Exception",L"RDK Exception",MB_OK);
	 throw;

	}
  	catch (RDK::UException *exception)
	{
	 Application->MessageBox(L"RDK Exception",L"RDK Exception",MB_OK);
	 throw;
	}
	catch(...)
	{
	 Application->MessageBox(L"AAAAAAAAAAAAAA",L"RDK Exception",MB_OK);

	}     */
/* NAContainer *cont=0;
 MySDKIOLabeledEdit->Text=IntToStr(int(sizeof(*RDK::dynamic_pointer_cast<NAContainer*>(cont))));
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+";";
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+IntToStr(int(sizeof(*RDK::dynamic_pointer_cast<NAConnector*>(cont))));
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+";";
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+IntToStr(int(sizeof(*RDK::dynamic_pointer_cast<NAItem*>(cont))));
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+";";
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+IntToStr(int(sizeof(*RDK::dynamic_pointer_cast<NADItem*>(cont))));
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+";";
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+IntToStr(int(sizeof(*RDK::dynamic_pointer_cast<NANet*>(cont))));
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+";";
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+IntToStr(int(sizeof(*RDK::dynamic_pointer_cast<NNet*>(cont))));
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+";";
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+IntToStr(int(sizeof(*RDK::dynamic_pointer_cast<NNeuron*>(cont))));
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+";";
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+IntToStr(int(sizeof(*RDK::dynamic_pointer_cast<NPulseNeuron*>(cont))));
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+"; NumObjs=";
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+IntToStr(int(Environment->GetStorage()->CalcNumObjects()));
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+"; LastClassId=";
 MySDKIOLabeledEdit->Text=MySDKIOLabeledEdit->Text+IntToStr(int(Environment->GetStorage()->GetLastClassId()));



// for(int i=0;i<100;i++)
//  Environment->GetStorage()->TakeObject("NNeuronLife");
  //cont=new NNeuronLife("NeuronLife");    */
			   /*
SendNotifyMessage(          Handle,
	WM_USER+4242,
	10,
	0
);               */

}
//---------------------------------------------------------------------------

void __fastcall TMainForm::StatsButtonClick(TObject *Sender)
{
 StatisticForm->Show();
}
//---------------------------------------------------------------------------



void __fastcall TMainForm::FormCreate(TObject *Sender)
{
// OldWindowProc = (WNDPROC)SetWindowLong(Handle,
// GWL_WNDPROC, (long)NewWindowProc);
}
//---------------------------------------------------------------------------

