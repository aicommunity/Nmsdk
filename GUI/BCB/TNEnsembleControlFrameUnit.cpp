//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "TNEnsembleControlFrameUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TNEnsembleControlFrame *NEnsembleControlFrame;
//---------------------------------------------------------------------------
__fastcall TNEnsembleControlFrame::TNEnsembleControlFrame(TComponent* Owner)
	: TFrame(Owner)
{
 UpdateInterfaceFlag=false;
 Network=0;
}
//---------------------------------------------------------------------------

void TNEnsembleControlFrame::UpdateInterface(void)
{
 if(!Network)
  return;

 UpdateInterfaceFlag=true;

 // А теперь данные бета-ансамблей
 BetaEnsembleStringGrid->RowCount=Network->GetNumBetaEnsembles()+1;
 BetaEnsembleStringGrid->ColCount=3;
 BetaEnsembleStringGrid->Cells[0][0]="Мощность";
 BetaEnsembleStringGrid->ColWidths[0]=60;

 if(BetaEnsembleStringGrid->RowCount>1)
  BetaEnsembleStringGrid->FixedRows=1;

 for(size_t i=0;i<Network->GetNumBetaEnsembles();i++)
 {
  if(BetaEnsembleStringGrid->ColCount<int(Network->GetBetaEnsemble(i).size())+1)
   BetaEnsembleStringGrid->ColCount=Network->GetBetaEnsemble(i).size()+1;
  for(size_t j=0;j<Network->GetBetaEnsemble(i).size();j++)
  {
   BetaEnsembleStringGrid->Cells[j+1][0]=String("#")+IntToStr(int(j+1));
   BetaEnsembleStringGrid->Cells[j+1][i+1]=Network->GetBetaEnsemble(i)[j]->GetName().c_str();
  }
  BetaEnsembleStringGrid->Cells[0][i+1]=FloatToStrF(Network->GetBetaEnsemblePower(i),ffFixed,5,5);
 }
/*
 if(BetaEnsembleStringGrid->RowCount>row)
  BetaEnsembleStringGrid->Row=row;
 else
 if(BetaEnsembleStringGrid->RowCount>0)
  BetaEnsembleStringGrid->Row=BetaEnsembleStringGrid->RowCount-1;

 if(BetaEnsembleStringGrid->ColCount>col)
  BetaEnsembleStringGrid->Col=col;
 else
 if(BetaEnsembleStringGrid->ColCount>0)
  BetaEnsembleStringGrid->Col=BetaEnsembleStringGrid->ColCount-1;
					*/

 // А теперь данные ансамблей
 EnsembleStringGrid->RowCount=Network->GetNumEnsembles()+1;
 EnsembleStringGrid->ColCount=5;

 if(EnsembleStringGrid->RowCount>1)
  EnsembleStringGrid->FixedRows=1;

 EnsembleStringGrid->FixedCols=3;

 EnsembleStringGrid->Cells[0][0]="Мощность";
 EnsembleStringGrid->Cells[1][0]="Активность";
 EnsembleStringGrid->Cells[2][0]="Отн. Актив.";
 EnsembleStringGrid->ColWidths[0]=60;
 EnsembleStringGrid->ColWidths[1]=60;
 EnsembleStringGrid->ColWidths[2]=60;
 for(size_t i=0;i<Network->GetNumEnsembles();i++)
 {
  if(EnsembleStringGrid->ColCount<int(Network->GetEnsemble(i).size())+3)
   EnsembleStringGrid->ColCount=Network->GetEnsemble(i).size()+3;
  for(size_t j=0;j<Network->GetEnsemble(i).size();j++)
  {
   EnsembleStringGrid->Cells[j+3][0]=String("#")+IntToStr(int(j+1));
   EnsembleStringGrid->Cells[j+3][i+1]=Network->GetEnsemble(i)[j]->GetName().c_str();
  }
  EnsembleStringGrid->Cells[0][i+1]=FloatToStrF(Network->GetEnsemblePower(i),ffFixed,5,5);
  EnsembleStringGrid->Cells[1][i+1]=FloatToStrF(Network->GetEnsembleActivity(i),ffFixed,3,3);
  EnsembleStringGrid->Cells[2][i+1]=FloatToStrF(Network->GetRelativeEnsembleActivity(i),ffFixed,3,3);
 }
				/*
 if(EnsembleStringGrid->RowCount>row)
  EnsembleStringGrid->Row=row;
 else
 if(EnsembleStringGrid->RowCount>0)
  EnsembleStringGrid->Row=EnsembleStringGrid->RowCount-1;

 if(EnsembleStringGrid->ColCount>col)
  EnsembleStringGrid->Col=col;
 else
 if(EnsembleStringGrid->ColCount>0)
  EnsembleStringGrid->Col=EnsembleStringGrid->ColCount-1;
                                */

 // А теперь данные ансамблей
 EnsembleLinksStringGrid->RowCount=Network->GetNumEnsembleLinks()+1;
 EnsembleLinksStringGrid->ColCount=4;

 if(EnsembleLinksStringGrid->RowCount>1)
  EnsembleLinksStringGrid->FixedRows=1;

 EnsembleLinksStringGrid->FixedCols=2;

 EnsembleLinksStringGrid->Cells[0][0]="#";
 EnsembleLinksStringGrid->Cells[1][0]="Мощность";
 EnsembleLinksStringGrid->Cells[2][0]="Источник";
 EnsembleLinksStringGrid->Cells[3][0]="Приемник";
 EnsembleLinksStringGrid->ColWidths[0]=30;
 EnsembleLinksStringGrid->ColWidths[1]=60;
 EnsembleLinksStringGrid->ColWidths[2]=120;
 EnsembleLinksStringGrid->ColWidths[3]=120;
 for(size_t i=0;i<Network->GetNumEnsembleLinks();i++)
 {
  EnsembleLinksStringGrid->Cells[0][i+1]=IntToStr(int(i)+1);
  const NMSDK::NEnsembleLink &link=Network->GetEnsembleLink(Network->GetNumEnsembleLinks()-i-1);
  EnsembleLinksStringGrid->Cells[1][i+1]=FloatToStrF(link.Power,ffFixed,5,5);
  EnsembleLinksStringGrid->Cells[2][i+1]=link.In.c_str();
  EnsembleLinksStringGrid->Cells[3][i+1]=link.Out.c_str();
 }

 // Остальные элементы управления
 EnsembleThresholdEdit->Text=FloatToStrF(Network->EnsembleThreshold,
			ffFixed,5,5);
 EnsembleThresholdTrackBar->Position=Network->EnsembleThreshold*10000.0;

 EnsembleThresholdModeRadioGroup->ItemIndex=Network->EnsembleThresholdMode;

 UpdateInterfaceFlag=false;
}
//---------------------------------------------------------------------------
void __fastcall TNEnsembleControlFrame::EnsembleThresholdTrackBarChange(TObject *Sender)

{
 if(UpdateInterfaceFlag)
  return;

 EnsembleThresholdEdit->Text=FloatToStrF(EnsembleThresholdTrackBar->Position/10000.0,
			ffFixed,5,5);
}
//---------------------------------------------------------------------------
void __fastcall TNEnsembleControlFrame::EnsembleThresholdEditChange(TObject *Sender)

{
 if(UpdateInterfaceFlag)
  return;

 NMSDK::double threshold=StrToFloat(EnsembleThresholdEdit->Text);
 if(Network)
  Network->EnsembleThreshold=threshold;
}
//---------------------------------------------------------------------------
void __fastcall TNEnsembleControlFrame::EnsembleThresholdModeRadioGroupClick(TObject *Sender)

{
 if(UpdateInterfaceFlag)
  return;

 Network->EnsembleThresholdMode=EnsembleThresholdModeRadioGroup->ItemIndex;
}
//---------------------------------------------------------------------------

