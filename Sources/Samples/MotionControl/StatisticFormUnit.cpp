//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "StatisticFormUnit.h"
#include <math.h>
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TStatisticForm *StatisticForm;
//---------------------------------------------------------------------------
__fastcall TStatisticForm::TStatisticForm(TComponent* Owner)
	: TForm(Owner)
{
 Reset();
}
//---------------------------------------------------------------------------

void TStatisticForm::UpdateInterface(void)
{
 String str="[";
 str+=FloatToStrF(MinAngle,ffFixed,4,4);
 str+="; ";
 str+=FloatToStrF(MaxAngle,ffFixed,4,4);
 str+="]=";
 str+=FloatToStrF(fabs(MaxAngle-MinAngle),ffFixed,4,4);
 AngleMaxRangeLabeledEdit->Text=str;
 AngleMaxRangeLabeledEdit->Repaint();

 str=FloatToStrF(MinAngle+(MaxAngle-MinAngle)/2.0,ffFixed,4,4);
 AngleAvgRangeLabeledEdit->Text=str;
 AngleAvgRangeLabeledEdit->Repaint();

 str=FloatToStrF(MaxSpeed,ffFixed,4,4);
 MaxSpeedLabeledEdit->Text=str;
 MaxSpeedLabeledEdit->Repaint();

 if(StatsTime != 0)
  str=FloatToStrF(FrequencyCounter/StatsTime,ffFixed,4,4);
 else
  str="";

 MaxFrequencyLabeledEdit->Text=str;
 MaxFrequencyLabeledEdit->Repaint();

 if(NumStats != 0)
  str=FloatToStrF(SumSpeed/NumStats,ffFixed,4,4);
 else
  str="";
 AvgSpeedLabeledEdit->Text=str;
 AvgSpeedLabeledEdit->Repaint();

// AngleAvgRangeLabeledEdit

}

void TStatisticForm::Reset(void)
{
 FrequencyCounter=0;

 StatsTime=0;

 MinAngle=0;
 MaxAngle=0;

 MaxSpeed=0;
 NumStats=0;
 SumSpeed=0;
}
void __fastcall TStatisticForm::Button1Click(TObject *Sender)
{
 Reset();
 UpdateInterface();
}
//---------------------------------------------------------------------------
