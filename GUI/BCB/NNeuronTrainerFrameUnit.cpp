//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "NNeuronTrainerFrameUnit.h"
#include "UGEngineControlFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "UDrawEngineFrameUnit"
#pragma link "UWatchFrameUnit"
#pragma link "UWatchFramePageUnit"
#pragma resource "*.dfm"
TNNeuronTrainerFrame *NNeuronTrainerFrame;
//---------------------------------------------------------------------------
__fastcall TNNeuronTrainerFrame::TNNeuronTrainerFrame(TComponent* Owner)
	: TUVisualControllerFrame(Owner)
{
}
//---------------------------------------------------------------------------

// Сохраняет параметры интерфейса в xml
void TNNeuronTrainerFrame::ASaveParameters(RDK::USerStorageXML &xml)
{
	//
}

// Загружает параметры интерфейса из xml
void TNNeuronTrainerFrame::ALoadParameters(RDK::USerStorageXML &xml)
{
    //
}

void TNNeuronTrainerFrame::AUpdateInterface(void)
{
 RDK::UELockPtr<RDK::UNet> model=RDK::GetModelLock<RDK::UNet>();
 if(!model)
  return;
 std::string ccname = "NeuronTrainer";
 RDK::UEPtr<NMSDK::NNeuronTrainer> trainer=RDK::dynamic_pointer_cast<NMSDK::NNeuronTrainer>(model->GetComponentL(ccname.c_str()));
 if(!trainer)
  return;

 // Количество дендритов
 int dend_num = trainer->NumInputDendrite;
 NumInputDendriteLabeledEdit->Text = IntToStr(dend_num);
 // Задержки сигналов на дендритах
 InputDelaysGrid->RowCount = dend_num;
 for(int i = 0; i < dend_num; i++)
 {
	InputDelaysGrid->Cells[0][i] = FloatToStr(trainer->InputPattern[i]);
 }

 // Задержка генераторов импульсов
 DelayLabeledEdit->Text = FloatToStr(trainer->Delay);
 // Частота генераторов
 FrequencyLabeledEdit->Text = FloatToStr(trainer->SpikesFrequency);
 // Максимальная длина дендритов
 MaxDendriteLengthLabeledEdit->Text = IntToStr(trainer->MaxDendriteLength);
 NumInputDendriteUpDown->Max = trainer->MaxDendriteLength;
 // Порог в низкопороговой зоне
 LTZThresholdLabeledEdit->Text = FloatToStr(trainer->LTZThreshold);

 // Процесс обучения
 bool is_training = trainer->IsNeedToTrain;
 if(is_training)
 {
  StartTrainingButton->Enabled = false;
  StopTrainingButton->Enabled = true;
 }
 else
 {
  StartTrainingButton->Enabled = true;
  StopTrainingButton->Enabled = false;
 }
}

// Возврат интерфейса в исходное состояние
void TNNeuronTrainerFrame::AClearInterface(void)
{
    //
}

// Создание копии этого компонента
TUVisualControllerFrame* TNNeuronTrainerFrame::New(TComponent *owner)
{
 return new TNNeuronTrainerFrame(owner);
}

//---------------------------------------------------------------------------
void __fastcall TNNeuronTrainerFrame::StartToolButtonClick(TObject *Sender)
{
 UGEngineControlForm->Start1Click(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TNNeuronTrainerFrame::PauseToolButtonClick(TObject *Sender)
{
 UGEngineControlForm->Pause1Click(Sender);
}
//---------------------------------------------------------------------------


void __fastcall TNNeuronTrainerFrame::SetDendritesButtonClick(TObject *Sender)
{
 RDK::UELockPtr<RDK::UNet> model=RDK::GetModelLock<RDK::UNet>();
 if(!model)
  return;
 std::string ccname = "NeuronTrainer";
 RDK::UEPtr<NMSDK::NNeuronTrainer> trainer=RDK::dynamic_pointer_cast<NMSDK::NNeuronTrainer>(model->GetComponentL(ccname.c_str()));
 if(!trainer)
  return;

 // Количество дендритов
 int dend_num = StrToInt(NumInputDendriteLabeledEdit->Text);
 trainer->NumInputDendrite = dend_num;
 // Задержки сигналов на дендритах
 for(int i = 0; i < dend_num; i++)
 {
	trainer->InputPattern[i] = StrToFloat(InputDelaysGrid->Cells[0][i]);
 }

 UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TNNeuronTrainerFrame::NumInputDendriteUpDownClick(TObject *Sender,
		  TUDBtnType Button)
{
	if(Button == btNext)
	{
		InputDelaysGrid->RowCount = InputDelaysGrid->RowCount + 1;
	}
	else if(Button == btPrev)
	{
		InputDelaysGrid->RowCount = InputDelaysGrid->RowCount - 1;
	}
}
//---------------------------------------------------------------------------

void __fastcall TNNeuronTrainerFrame::SetParamsButtonClick(TObject *Sender)
{
 RDK::UELockPtr<RDK::UNet> model=RDK::GetModelLock<RDK::UNet>();
 if(!model)
  return;
 std::string ccname = "NeuronTrainer";
 RDK::UEPtr<NMSDK::NNeuronTrainer> trainer=RDK::dynamic_pointer_cast<NMSDK::NNeuronTrainer>(model->GetComponentL(ccname.c_str()));
 if(!trainer)
  return;

 // Задержка генераторов импульсов
 trainer->Delay = StrToFloat(DelayLabeledEdit->Text);
 // Частота генераторов
 trainer->SpikesFrequency = StrToFloat(FrequencyLabeledEdit->Text);
 // Максимальная длина дендритов
 trainer->MaxDendriteLength = StrToFloat(MaxDendriteLengthLabeledEdit->Text);
 // Порог в низкопороговой зоне
 trainer->LTZThreshold = StrToFloat(LTZThresholdLabeledEdit->Text);

 UpdateInterface();
}
//---------------------------------------------------------------------------

void __fastcall TNNeuronTrainerFrame::StartTrainingButtonClick(TObject *Sender)
{
 RDK::UELockPtr<RDK::UNet> model=RDK::GetModelLock<RDK::UNet>();
 if(!model)
  return;
 std::string ccname = "NeuronTrainer";
 RDK::UEPtr<NMSDK::NNeuronTrainer> trainer=RDK::dynamic_pointer_cast<NMSDK::NNeuronTrainer>(model->GetComponentL(ccname.c_str()));
 if(!trainer)
  return;

 StartTrainingButton->Enabled = false;
 StopTrainingButton->Enabled = true;

 trainer->IsNeedToTrain = true;
}
//---------------------------------------------------------------------------

void __fastcall TNNeuronTrainerFrame::StopTrainingButtonClick(TObject *Sender)
{
 RDK::UELockPtr<RDK::UNet> model=RDK::GetModelLock<RDK::UNet>();
 if(!model)
  return;
 std::string ccname = "NeuronTrainer";
 RDK::UEPtr<NMSDK::NNeuronTrainer> trainer=RDK::dynamic_pointer_cast<NMSDK::NNeuronTrainer>(model->GetComponentL(ccname.c_str()));
 if(!trainer)
  return;

 StartTrainingButton->Enabled = true;
 StopTrainingButton->Enabled = false;

 trainer->IsNeedToTrain = false;
}
//---------------------------------------------------------------------------

