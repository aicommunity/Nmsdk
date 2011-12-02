//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "TNSourceControlFrameUnit.h"
#include <algorithm>
#include "../Libraries/SourceLib/NSourceLibrary.h"
#include "TNSupport.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "WatchFrameUnit"
#pragma link "TUClassRegistryFrame"
#pragma resource "*.dfm"
TNSourceControlFrame *NSourceControlFrame;
//---------------------------------------------------------------------------
__fastcall TNSourceControlFrame::TNSourceControlFrame(TComponent* Owner)
	: TFrame(Owner)
{
 UpdateInterfaceFlag=false;
 WatchInterval=0.5;
 Origin=0;//1.1;
}
//---------------------------------------------------------------------------
// Устанавливает интервал наблюдения
bool TNSourceControlFrame::SetWatchInterval(real interval)
{
 if(WatchInterval == interval)
  return true;

 WatchInterval = interval;
 return true;
}

// Добавляет источник в массив
bool TNSourceControlFrame::AddSource(NSource* source)
{
 if(!source)
  return false;

 if(find(Sources.begin(),Sources.end(),source) != Sources.end())
  return true;

 Sources.push_back(source);

// source->Save(Parameters);
 return true;
}

// Удаляет источник из массива
bool TNSourceControlFrame::DelSource(NSource* source)
{
 if(!source)
  return true;

 vector<NSource*>::iterator I=find(Sources.begin(),Sources.end(),source);

 if(I != Sources.end())
 {
  Parameters.Del((*I)->GetName());
  Sources.erase(I);
 }
 return true;
}

// Удаляет источник по индексу
bool TNSourceControlFrame::DelSource(size_t index)
{
 if(index<Sources.size())
  return true;

 return DelSource(Sources[index]);
}

// Удаляет все источники
bool TNSourceControlFrame::DelAllSources(void)
{
 Sources.clear();
 Parameters.Clear();
 SourceWatchFrame->Clear();
 SourceWatchFrame->Reset();
 return true;
}

// Пополняет массив источников, всеми источниками из контейнера cont
// Возвращает число добавленных источников
int TNSourceControlFrame::FindSources(NAContainer *cont)
{
 if(!cont)
  return 0;

 int count=0;
 UEPtr<NSource> source;

 for(int i=0;i<cont->GetNumComponents();i++)
  if((source=dynamic_pointer_cast<NSource>(cont->GetComponentByIndex(i))) != 0)
  {
   if(!AddSource(source))
    return count;
   ++count;
  }
 return count;
}

// Активирует на форме источник с заданными индексами в массиве, и векторе выходов
bool TNSourceControlFrame::SelectSource(size_t sourceindex, size_t outputindex)
{
 return false;
}

// Обновляет список наблюдений графика
bool TNSourceControlFrame::WatchUpdate(void)
{
 map<int,OutGateWatchData> watches;
 map<int,OutGateWatchData>::iterator I,J;
 SourceWatchFrame->GetWatchList(watches);

 bool res;

 int shift=0;
 for(size_t i=0;i<Sources.size();i++)
 {
  I=watches.begin();
  J=watches.end();
  res=true;
  while(I != J)
  {
   if(I->second.DataSource == Sources[i])
   {
	res=false;
	break;
   }

   ++I;
  }

  if(!res)
   continue;

  for(int n=0;n<Sources[i]->GetNumOutputs();n++)
   for(size_t m=0;m<Sources[i]->GetOutputDataSize(n);m++)
   {
	if(Origin == 0)
	 AddWatch(SourceWatchFrame,Sources[i],n,m,WatchInterval);
	else
	{
	 AddWatch(SourceWatchFrame,Sources[i],n,m,WatchInterval,shift);
	 shift+=Origin;
	}
   }
 }
 return true;
}

// Обновляет состояние графика на очередном шаге счета
void TNSourceControlFrame::StepUpdate(void)
{
 SourceWatchFrame->StepUpdate();
}

// Обновляет интерфейс
void TNSourceControlFrame::UpdateInterface(void)
{
 UpdateInterfaceFlag=true;

 UClassRegistryFrame->SetRegistry(&Parameters);
/*
 SourcesStringGrid->RowCount=Sources.size()+1;
 SourcesStringGrid->ColCount=3;
 NPulseGenerator *gen;
 for(size_t i=0;i<Sources.size();i++)
 {
  SourcesStringGrid->Cells[0][i+1]=IntToStr(int(i));
  if(SourcesStringGrid->ColCount<Sources[i]->GetOutputDataSize(0)+1)
   SourcesStringGrid->ColCount=Sources[i]->GetOutputDataSize(0)+1;

  for(size_t j=0;j<Sources[i]->GetOutputDataSize(0);j++)
  {
   SourcesStringGrid->Cells[j+1][0]=IntToStr(int(j));
   SourcesStringGrid->Cells[j+1][i+1]=Sources[i]->Name->c_str();
   if(NPulseGenerator *pulse=dynamic_cast<NPulseGenerator*>(Sources[i]))
   {
	if(SourcesStringGrid->ColCount<4)
	 SourcesStringGrid->ColCount=4;
	SourcesStringGrid->Cells[j+2][i+1]=IntToStr(int(pulse->Amplitude));
	SourcesStringGrid->Cells[j+3][i+1]=IntToStr(int(pulse->Frequency));
	if(SourcesStringGrid->Row-1 == i && SourcesStringGrid->Col-1 == j)
	{
	 FrequencyGroupBox->Visible=true;
	 FrequencyTrackBar->Position=pulse->Frequency;
	}
   }
  }
 }

 SourcesStringGrid->Cells[0][0]="#";
 SourcesStringGrid->Cells[1][0]="Имя источника";
 SourcesStringGrid->Cells[2][0]="Амплитуда";
 SourcesStringGrid->Cells[3][0]="Частота";

 int width=SourcesStringGrid->ClientWidth;
 if(SourcesStringGrid->ColCount>1)
 {
  SourcesStringGrid->ColWidths[0]=15;
  width-=SourcesStringGrid->ColWidths[0];
  SourcesStringGrid->ColWidths[1]=width/2;
  width-=SourcesStringGrid->ColWidths[1];
 }

 width=width/(SourcesStringGrid->ColCount-2);
 for(size_t i=2;i<SourcesStringGrid->ColCount;i++)
  SourcesStringGrid->ColWidths[i]=width;
     */
 UpdateInterfaceFlag=false;
}
void __fastcall TNSourceControlFrame::FrequencyTrackBarChange(TObject *Sender)
{
 FrequencyEdit->Text=FloatToStrF(FrequencyTrackBar->Position,ffFixed,3,3);
}
//---------------------------------------------------------------------------
void __fastcall TNSourceControlFrame::FrequencyEditChange(TObject *Sender)
{
 NPulseGenerator* pulse=dynamic_cast<NPulseGenerator*>(Sources[SourcesStringGrid->Row-1]);
 if(!pulse)
  return;

 pulse->Frequency=StrToFloat(FrequencyEdit->Text);
 pulse->SetActivity(true);
}
//---------------------------------------------------------------------------
void __fastcall TNSourceControlFrame::AmplitudeTrackBarChange(TObject *Sender)
{
 AmplitudeEdit->Text=FloatToStrF(AmplitudeTrackBar->Position,ffFixed,3,3);
}
//---------------------------------------------------------------------------
void __fastcall TNSourceControlFrame::AmplitudeEditChange(TObject *Sender)
{
 NPulseGenerator* pulse=dynamic_cast<NPulseGenerator*>(Sources[SourcesStringGrid->Row-1]);
 if(!pulse)
  return;

 pulse->Amplitude=StrToFloat(AmplitudeEdit->Text);
}
//---------------------------------------------------------------------------
void __fastcall TNSourceControlFrame::UClassRegistryFrameLabeledEditKeyPress(TObject *Sender,
		  wchar_t &Key)
{
 UClassRegistryFrame->LabeledEditKeyPress(Sender,Key);
 if(Key == VK_RETURN)
 {
  for(size_t i=0;i<Sources.size();i++)
  {
   string name=(*UClassRegistryFrame->GetDiffRegistry())[0].GetName();
//   if(Sources[i]->GetName() == name.substr(0,name.find_first_of(":")))
//	Sources[i]->Load((*UClassRegistryFrame->GetDiffRegistry())[0],0,true);
  }

  UClassRegistryFrame->ClearDiffRegistry();
 }
}
//---------------------------------------------------------------------------
void __fastcall TNSourceControlFrame::UClassRegistryFrameSetBitBtnClick(TObject *Sender)
{
 UClassRegistryFrame->SetBitBtnClick(Sender);
 for(size_t i=0;i<Sources.size();i++)
 {
  string name=(*UClassRegistryFrame->GetDiffRegistry())[0].GetName();
//  if(Sources[i]->GetName() == name.substr(0,name.find_first_of(":")))
//   Sources[i]->Load((*UClassRegistryFrame->GetDiffRegistry())[0],0,true);
 }
 UClassRegistryFrame->ClearDiffRegistry();
}
//---------------------------------------------------------------------------
