//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "UComponentsListFormUnit.h"
#include "TNNewPositionControlElementFormUnit.h"
#include "nmsdk.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TNNewPositionControlElementForm *NNewPositionControlElementForm;
//---------------------------------------------------------------------------
__fastcall TNNewPositionControlElementForm::TNNewPositionControlElementForm(TComponent* Owner)
	: TUVisualControllerForm(Owner)
{
}

// Сохраняет параметры интерфейса в xml
void TNNewPositionControlElementForm::ASaveParameters(RDK::USerStorageXML &xml)
{

}

// Загружает параметры интерфейса из xml
void TNNewPositionControlElementForm::ALoadParameters(RDK::USerStorageXML &xml)
{

}


void TNNewPositionControlElementForm::AUpdateInterface(void)
{
 try
 {
  RDK::UEPtr<NMSDK::NNewPositionControlElement> position_control=
	RDK::dynamic_pointer_cast<NMSDK::NNewPositionControlElement>(GetModel()->GetComponentL(ComponentControlName));

  // Отображаем состояние генераторов
  std::vector<RDK::UNet*> &generators=position_control->Generators;
  SelectedStateStringGrid->ColCount=generators.size()+1;
  SelectedStateStringGrid->RowCount=2;
  for(size_t i=0;i<generators.size();i++)
  {
   RDK::UEPtr<NMSDK::NPulseGenerator> gen=dynamic_cast<NMSDK::NPulseGenerator*>(generators[i]);
   SelectedStateStringGrid->Cells[i+1][1]=FloatToStrF(gen->Frequency,ffFixed,3,3);
  }

 // Отображаем состояние наученного слоя
  std::vector<NMSDK::NNet*> &neurons=position_control->PostInputNeurons;
  TrainedStateStringGrid->ColCount=neurons.size()+1;
  TrainedStateStringGrid->RowCount=2;
  for(size_t i=0;i<generators.size();i++)
  {
   RDK::UEPtr<NMSDK::NPulseNeuron> gen=dynamic_cast<NMSDK::NPulseNeuron*>(neurons[i]);
   RDK::UEPtr<NMSDK::NPulseLTZone> ltzone=dynamic_pointer_cast<NMSDK::NPulseLTZone>(neurons[i]->GetComponentL("LTZone"));
   TrainedStateStringGrid->Cells[i+1][1]=FloatToStrF(ltzone->GetOutputData(2).Double[0],ffFixed,3,3);
  }

 }
 catch(RDK::UException &exception)
 {

 }
}


// Создание копии этого компонента
TUVisualControllerForm* TNNewPositionControlElementForm::New(TComponent *owner)
{
 return new TNNewPositionControlElementForm(owner);
}
//---------------------------------------------------------------------------
void __fastcall TNNewPositionControlElementForm::FormCreate(TObject *Sender)
{
 TUComponentsListFrame::ComponentControllers["NNewPositionControlElement"]=NNewPositionControlElementForm;
}
//---------------------------------------------------------------------------

void __fastcall TNNewPositionControlElementForm::SelectedStateStringGridSetEditText(TObject *Sender,
          int ACol, int ARow, const UnicodeString Value)
{
 try
 {
  RDK::UEPtr<NMSDK::NNewPositionControlElement> position_control=
	RDK::dynamic_pointer_cast<NMSDK::NNewPositionControlElement>(GetModel()->GetComponentL(ComponentControlName));

  // Отображаем состояние генераторов
  std::vector<RDK::UNet*> &generators=position_control->Generators;

  if(ARow != 1 || ACol<=0 || ACol>generators.size())
   return;

  RDK::UEPtr<NMSDK::NPulseGenerator> gen=dynamic_cast<NMSDK::NPulseGenerator*>(generators[ACol-1]);
  try
  {
  gen->Frequency=StrToFloat(SelectedStateStringGrid->Cells[ACol][ARow]);
  }
  catch(EConvertError &ex)
  {

  }
 }
 catch(UException &exception)
 {

 }
}
//---------------------------------------------------------------------------

