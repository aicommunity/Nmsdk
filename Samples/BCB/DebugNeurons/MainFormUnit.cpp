//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "MainFormUnit.h"
#include "MuscleTestFormUnit.h"
#include "ManipulatorTestUnit.h"
#include "MuscleControlFormUnit.h"
#include "GraphicsFormUnit.h"
#include "NGraphics.h"
#include "NNet.h"
#include "NPac.h"
#include "NSignumSeparator.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "TUClassRegistryFrame"
#pragma resource "*.dfm"
TMainForm *MainForm;



// Добавляем объект в окно наблюдений
void TMainForm::AddWatch(NAContainer *item, int output, TWatchFrame *watch, double yshift, TPenStyle style, TColor color)
{
 NADItem *itemd=dynamic_cast<NADItem*>(item);

 if(!watch || !itemd)
  return;


 OutGateWatchData wd;
 wd.FullUpdate=false;
 wd.WatchInterval=1;
 wd.X=&NAContainer::GetDoubleTime();

 wd.YShift=yshift;
 itemd->GetLongName(itemd->GetOwner()->GetOwner(),wd.Legend);
 wd.DataSource=item;
 wd.Color=color;
 wd.Y=&(itemd->GetOutputData(0).Double[output]);
 wd.XYSize=1;//itemd->GetOutputDataSize(0);
 wd.Style=style;
// wd.Y=&(((NAItem*)item->GetComponent("LTZone"))->GetOutputData().Double[0]);
// wd.XYSize=((NAItem*)item->GetComponent("LTZone"))->OutputSize;
 watch->Add(wd);
}

void TMainForm::AddFrequencyWatch(NAContainer *item,TWatchFrame *watch, double yshift, TPenStyle style, TColor color)
{
 NFrequencyReceiver* itemd=dynamic_cast<NFrequencyReceiver*>(item);

 if(!itemd || !watch)
  return;

 OutGateWatchData wd;
 wd.FullUpdate=true;
 wd.WatchInterval=1;
 wd.X=&itemd->GetXResult()[0];

 wd.YShift=yshift;
 itemd->GetLongName(itemd->GetOwner()->GetOwner(),wd.Legend);
 wd.DataSource=item;
 wd.Color=color;
 wd.Y=&itemd->GetYResult()[0];
 wd.XYSize=itemd->GetYResult().size();
 wd.Style=style;
// wd.Y=&(((NAItem*)item->GetComponent("LTZone"))->GetOutputData().Double[0]);
// wd.XYSize=((NAItem*)item->GetComponent("LTZone"))->OutputSize;
 watch->Add(wd);
}

// Формируем сеть тестирования нейронов
void TMainForm::CreateNeuralTest(NStorage *storage, NANet *net,TWatchFrame *watch)
{
 NAContainer *cont;
 bool res;

 int i=1,j=0;

 double ampl=1, dist=0.25;

 // Простой мелкий нейрон
 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="Small Simple Pulse";
 res=net->AddComponent(cont);
 AddWatch(cont->GetComponent("LTZone"),0, MuscleTestForm->SingleMuscleWatchFrame, (ampl+dist)*(j),psSolid,clRed);
 AddWatch(cont->GetComponent("LTZone"),1, MuscleTestForm->SingleMuscleWatchFrame, (ampl+dist)*(j++),psSolid,clRed);

// AddWatch(cont->GetComponentL("PNeuronMembrane.PosChannel.Synapse"),0, MuscleTestForm->SingleMuscleWatchFrame, (ampl+dist)*(j++),psDashDot,clRed);

 // Простой крупный нейрон
 cont=storage->TakeObject("NLPNeuron");
 if(!cont)
  return;
 cont->Name="Large Simple Pulse";
 res=net->AddComponent(cont);
 AddWatch(cont->GetComponent("LTZone"),0,MuscleTestForm->SingleMuscleWatchFrame, (ampl+dist)*(j),psSolid,clGreen);
 AddWatch(cont->GetComponent("LTZone"),1,MuscleTestForm->SingleMuscleWatchFrame, (ampl+dist)*(j++),psSolid,clGreen);

// AddWatch(cont->GetComponentL("PNeuronMembrane.PosChannel.Synapse"),0, MuscleTestForm->SingleMuscleWatchFrame, (ampl+dist)*(j++),psDashDot,clRed);

 // Создаем генератор
 cont=storage->TakeObject("NPGenerator");
 if(!cont)
  return;
 cont->Name="Simple Test Generator";
 ((NPulseGenerator*)cont)->Frequency=0;
 ((NPulseGenerator*)cont)->Amplitude=1;
 res=net->AddComponent(cont);
 MuscleControlForm->Generator=((NPulseGenerator*)cont);
 AddWatch(cont,0,MuscleTestForm->SingleMuscleWatchFrame, (ampl+dist)*(j++),psSolid,clBlue);

 res=net->CreateLink("Simple Test Generator",0,"Small Simple Pulse.PNeuronMembrane.PosChannel.Synapse");
// res=net->CreateLink("Simple Test Generator",0,"Small Simple Pulse.PNeuronMembrane.PosChannel.Synapse2");
// res=net->CreateLink("Simple Test Generator",0,"Small Simple Pulse.PNeuronMembrane.PosChannel.Synapse3");
 res=net->CreateLink("Simple Test Generator",0,"Large Simple Pulse.PNeuronMembrane.PosChannel.Synapse");
// res=net->CreateLink("Simple Test Generator",0,"Large Simple Pulse.PNeuronMembrane.PosChannel.Synapse2");
// res=net->CreateLink("Simple Test Generator",0,"Large Simple Pulse.PNeuronMembrane.PosChannel.Synapse3");


 MuscleTestForm->Show();
}

//---------------------------------------------------------------------------
// Формируем сеть управления мышцами
void TMainForm::CreateMuscleControl(NStorage *storage, NANet *net,TWatchFrame *watch)
{
}
//---------------------------------------------------------------------------

//---------------------------------------------------------------------------
// Формируем СУ двигательной единицей
void TMainForm::CreateMotionElement(NStorage *storage, NANet *net)
{
 NAContainer *cont;
 bool res;

 int i=1,j=0;

 double ampl=1, dist=0.25;

 // Клетка реншоу 1
 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="Renshow1";
 res=net->AddComponent(cont);

 // Клетка реншоу 2
 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="Renshow2";
 res=net->AddComponent(cont);

 // Мотонейрон 1
 cont=storage->TakeObject("NLPNeuron");
 if(!cont)
  return;
 cont->Name="Motoneuron1";
 res=net->AddComponent(cont);

 // Мотонейрон 2
 cont=storage->TakeObject("NLPNeuron");
 if(!cont)
  return;
 cont->Name="Motoneuron2";
 res=net->AddComponent(cont);

 // Постафферентные нейроны
 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="PostAfferent11";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="PostAfferent12";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="PostAfferent13";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="PostAfferent14";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="PostAfferent21";
 res=net->AddComponent(cont);


 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="PostAfferent22";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="PostAfferent23";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSPNeuron");
 if(!cont)
  return;
 cont->Name="PostAfferent24";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return;
 cont->Name="Afferent_Ia1";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return;
 cont->Name="Afferent_Ia2";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return;
 cont->Name="Afferent_Ib1";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return;
 cont->Name="Afferent_Ib2";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return;
 cont->Name="Afferent_II1";
 res=net->AddComponent(cont);

 cont=storage->TakeObject("NSAfferentNeuron");
 if(!cont)
  return;
 cont->Name="Afferent_II2";
 res=net->AddComponent(cont);

 // Установка связей
 NAContainer* c_item,*c_conn;
 LongIdT item,conn;

 res=net->CreateLink("Afferent_Ia1.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("Afferent_Ia1.LTZone",0,
				 "PostAfferent11.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("Afferent_Ia2.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("Afferent_Ia2.LTZone",0,
				 "PostAfferent21.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("PostAfferent11.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.NegChannel.Synapse");

 res=net->CreateLink("PostAfferent21.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel.Synapse");

 res=net->CreateLink("Motoneuron1.LTZone",0,
				 "Renshow1.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("Renshow1.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel.Synapse2");

 res=net->CreateLink("Renshow1.LTZone",0,
				 "PostAfferent11.PNeuronMembrane.NegChannel.Synapse");

 res=net->CreateLink("Motoneuron2.LTZone",0,
				 "Renshow2.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("Renshow2.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.NegChannel.Synapse2");

 res=net->CreateLink("Renshow2.LTZone",0,
				 "PostAfferent21.PNeuronMembrane.NegChannel.Synapse");

 // Канал Ib
 res=net->CreateLink("Afferent_Ib1.LTZone",0,
				 "PostAfferent12.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("Afferent_Ib1.LTZone",0,
				 "PostAfferent13.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("PostAfferent12.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.PosChannel.Synapse3");

 res=net->CreateLink("PostAfferent13.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel.Synapse3");

 res=net->CreateLink("Afferent_Ib2.LTZone",0,
				 "PostAfferent22.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("Afferent_Ib2.LTZone",0,
				 "PostAfferent23.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("PostAfferent22.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.PosChannel.Synapse3");

 res=net->CreateLink("PostAfferent23.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.NegChannel.Synapse3");

 // Канал II
 res=net->CreateLink("Afferent_II1.LTZone",0,
				 "PostAfferent14.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("PostAfferent14.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.NegChannel.Synapse4");
 res=net->CreateLink("PostAfferent14.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.PosChannel.Synapse4");

 res=net->CreateLink("Afferent_II2.LTZone",0,
				 "PostAfferent24.PNeuronMembrane.PosChannel.Synapse");

 res=net->CreateLink("PostAfferent24.LTZone",0,
				 "Motoneuron2.PNeuronMembrane.NegChannel.Synapse4");
 res=net->CreateLink("PostAfferent24.LTZone",0,
				 "Motoneuron1.PNeuronMembrane.PosChannel.Synapse4");
}
//---------------------------------------------------------------------------

//---------------------------------------------------------------------------
__fastcall TMainForm::TMainForm(TComponent* Owner)
		: TForm(Owner)
{
 Storage=new NStorage;
 Environment.SetStorage(Storage);
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::FormShow(TObject *Sender)
{
 Environment.AddClassLibrary(&BCLLibrary);
 Environment.AddClassLibrary(&ActLibrary);
 Environment.AddClassLibrary(&CRLibrary);
 Environment.AddClassLibrary(&PulseLibrary);
 Environment.AddClassLibrary(&MathLibrary);
 Environment.AddClassLibrary(&PhysLibrary);
 Environment.AddClassLibrary(&SensorLibrary);

 Environment.AddClassLibrary(&PulseNeuronLibrary);


 Environment.BuildStorage();

 NAContainer *cont;

 Environment.CreateModel("NModel");
// Model=Environment.GetModel();

 grcanvas.SetRes(1024,768);
 ugraph.SetCanvas(&grcanvas);
 ngraph.SetEngine(&ugraph);

 // Дополнительные классы

// Model=dynamic_cast<NModel*>(Storage->TakeObject("NModel"));
// if(!Model)
//  return;

 bool res;
 NAContainer *comp;

 NANet *net=dynamic_cast<NANet*>(Storage->TakeObject("NNet"));
 res=Environment->AddComponent(net);

 net->GetFullId(netid);
 ngraph.SetNet(net);
 Environment.AddGraphics(netid,&ngraph);


 comp=Storage->TakeObject("NReceiver");
 res=Environment->AddComponent(comp);

 comp=Storage->TakeObject("NSinusGenerator");
 comp->Name="SinusGenerator";
 res=Environment->AddComponent(comp);

 comp=Storage->TakeObject("NPGenerator");
 comp->Name="PulseGenerator";
 res=Environment->AddComponent(comp);



 // Формируем сеть управления мышцей
// CreateMuscleControl(Storage, net,WatchWindowForm->WatchFrame);

 CreateNeuralTest(Storage, net,WatchWindowForm->WatchFrame);

 MuscleControlForm->Show();

/* cont=Model->GetComponent("PulseGenerator");
 if(cont)
  item=cont->GetLongId(Model);
  */
 map<string,IdT>::const_iterator I,J;
 //
 I=Environment->GetComponentsList().begin();
 J=Environment->GetComponentsList().end();

 string s;
 StringGrid1->RowCount=2;
 while (I != J)
 {
  s=I->first;
  StringGrid1->Cells[1][StringGrid1->RowCount-1]=s.c_str();
  StringGrid1->Cells[0][StringGrid1->RowCount-1]=IntToStr(int(I->second));
  StringGrid1->RowCount=StringGrid1->RowCount+1;
  ++I;
 }
 StringGrid1->RowCount=StringGrid1->RowCount-1;


 I=Environment("Net")->GetComponentsList().begin();
 J=Environment()->GetComponentsList().end();

 StringGrid2->RowCount=2;
 while (I != J)
 {
  s=I->first;
  StringGrid2->Cells[1][StringGrid2->RowCount-1]=s.c_str();
  StringGrid2->Cells[0][StringGrid2->RowCount-1]=IntToStr(int(I->second));
  StringGrid2->RowCount=StringGrid2->RowCount+1;
  ++I;
 }
 StringGrid2->RowCount=StringGrid2->RowCount-1;

 Environment->TimeStep=10000;
 Environment.Reset();
 Environment.Calculate();

 // Model->TimeStep=0.01;
/*  MuscleTestForm->SingleMuscleWatchFrame->RestoreInfo("SingleMuscleWatchFrame",false);
  MuscleTestForm->DoubleMuscleWatchFrame->RestoreInfo("DoubleMuscleWatchFrame",false);
  MuscleTestForm->AfferentWatchFrame->RestoreInfo("AfferentWatchFrame",false);
  MuscleTestForm->FBMotoneuronWatchFrame->RestoreInfo("FBMotoneuronWatchFrame",false);
  MuscleTestForm->MotoneuronFrequencyWatchFrame->RestoreInfo("MotoneuronFrequencyWatchFrame",false);
  MuscleTestForm->NetworkWatchFrame->RestoreInfo("NetworkWatchFrame",false);
  MuscleTestForm->FNetworkWatchFrame->RestoreInfo("FNetworkWatchFrame",false);
  */
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::Button1Click(TObject *Sender)
{
// NeuroVisualForm->Show();
}
//---------------------------------------------------------------------------


void __fastcall TMainForm::StringGrid2SelectCell(TObject *Sender, int ACol,
	  int ARow, bool &CanSelect)
{
 IdT id=StrToInt(StringGrid2->Cells[0][ARow]);
 CSelected=Environment->GetComponent("Net")->GetComponent(id);

 if(!CSelected)
  return;

 CSelectedRegistry.Clear();
 CSelected->Save(CSelectedRegistry);
 ClassRegistryFrame->SetRegistry(&CSelectedRegistry);
// ClassRegistryFrame->UpdateRegistryTree();
// ClassRegistryFrame->UpdateRegistryParams();

 Selected=dynamic_cast<NADItem*>(CSelected);
 if(!Selected)
  return;

 string name;
 Selected->GetLongName(0,name);

// WatchWindowForm->Show();

 CanSelect=true;
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::Button3Click(TObject *Sender)
{
 //Model->TimeStep=0.01;
 Timer->Enabled=true;
 // Текущее время счета

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

 delete Storage;
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::TimerTimer(TObject *Sender)
{
 Timer->Enabled=false;
 for(int i=0;i<Environment->TimeStep()/10;i++)
 {
//  NAContainer::SetTime(NAContainer::GetTime()+1.0/Environment->Model->TimeStep);
  Environment.Calculate();
//  if(!(i%10))
  {
   if(MuscleTestForm->Visible)
   {
	MuscleTestForm->SingleMuscleWatchFrame->StepUpdate();
//	MuscleTestForm->DoubleMuscleWatchFrame->StepUpdate();
//	MuscleTestForm->AfferentWatchFrame->StepUpdate();
//	MuscleTestForm->FBMotoneuronWatchFrame->StepUpdate();
//	MuscleTestForm->MotoneuronFrequencyWatchFrame->StepUpdate();
//	MuscleTestForm->NetworkWatchFrame->StepUpdate();
//    MuscleTestForm->FNetworkWatchFrame->StepUpdate();
   }
  }

  if(Selected)
  {
  // WatchWindowForm->WatchFrame->StepUpdate();
  }
 }
 ManipulatorTestForm->UpdateInterface();
 Timer->Enabled=true;
}
//---------------------------------------------------------------------------



//---------------------------------------------------------------------------

void __fastcall TMainForm::Button6Click(TObject *Sender)
{
 Environment.Reset();
}
//---------------------------------------------------------------------------


void __fastcall TMainForm::ClassRegistryFrame1SetBitBtnClick(TObject *Sender)
{
 ClassRegistryFrame->SetBitBtnClick(Sender);

 CSelected->Load(CSelectedRegistry,0,true);
}
//---------------------------------------------------------------------------

void __fastcall TMainForm::Button2Click(TObject *Sender)
{
 NGraphics *gr=Environment.GetGraphics(netid);

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

