//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "TNAstaticGyroUnit.h"
#include "UComponentsListFormUnit.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TNAstaticGyro *NAstaticGyro;
//---------------------------------------------------------------------------
__fastcall TNAstaticGyro::TNAstaticGyro(TComponent* Owner)
	: TUVisualControllerForm(Owner)
{
}

// ��������� ��������� ���������� � xml
void TNAstaticGyro::ASaveParameters(RDK::USerStorageXML &xml)
{
}

// ��������� ��������� ���������� �� xml
void TNAstaticGyro::ALoadParameters(RDK::USerStorageXML &xml)
{
}


void TNAstaticGyro::AUpdateInterface(void)
{
 RDK::UELockPtr<NMSDK::NModel> model=RDK::GetModelLock<NMSDK::NModel>();
 if(!model)
  return;
 Gyro=std::static_pointer_cast<NMSDK::NAstaticGyro>(model->GetComponentL(ComponentControlName.c_str()));
 Image1->Canvas->TextOutA(5,0,"radians:");
 Image1->Canvas->TextOutA(5,20,"alpha = "+FloatToStr(Gyro->alpha));
 Image1->Canvas->TextOutA(5,40,"betta = "+FloatToStr(Gyro->betta));
 Image1->Canvas->TextOutA(5,60,"gamma = "+FloatToStr(Gyro->gamma));

 Image1->Canvas->TextOutA(5,80,"degrees:");
 Image1->Canvas->TextOutA(5,100,"alpha = "+FloatToStr(180*Gyro->alpha/3.1415));
 Image1->Canvas->TextOutA(5,120,"betta = "+FloatToStr(180*Gyro->betta/3.1415));
 Image1->Canvas->TextOutA(5,140,"gamma = "+FloatToStr(180*Gyro->gamma/3.1415));

 Image1->Repaint();
}

// ������� ���������� � �������� ���������
void TNAstaticGyro::AClearInterface(void)
{
 Gyro=0;
}

// �������� ����� ����� ����������
TUVisualControllerForm* TNAstaticGyro::New(TComponent *owner)
{
 return new TNAstaticGyro(owner);
}

//---------------------------------------------------------------------------
void __fastcall TNAstaticGyro::FormCreate(TObject *Sender)
{
 //
 TUComponentsListFrame::ComponentControllers["NAstaticGyro"]=NAstaticGyro;
}
//---------------------------------------------------------------------------


