//---------------------------------------------------------------------------

#ifndef StatisticFormUnitH
#define StatisticFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>
//---------------------------------------------------------------------------
class TStatisticForm : public TForm
{
__published:	// IDE-managed Components
	TPanel *Panel1;
	TPanel *Panel2;
	TButton *Button1;
	TLabeledEdit *AngleMaxRangeLabeledEdit;
	TLabeledEdit *MaxSpeedLabeledEdit;
	TLabeledEdit *MaxFrequencyLabeledEdit;
	TLabeledEdit *AvgSpeedLabeledEdit;
	TLabeledEdit *AngleAvgRangeLabeledEdit;
	void __fastcall Button1Click(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TStatisticForm(TComponent* Owner);

	double FrequencyCounter;

	double StatsTime;
	double NumStats;

	double MinAngle,MaxAngle;

	double MaxSpeed,SumSpeed;

	void UpdateInterface(void);
	void Reset(void);
};
//---------------------------------------------------------------------------
extern PACKAGE TStatisticForm *StatisticForm;
//---------------------------------------------------------------------------
#endif
