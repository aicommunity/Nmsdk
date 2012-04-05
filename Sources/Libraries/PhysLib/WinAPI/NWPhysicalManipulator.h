/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2011.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef NWPhysicalManipulatorH
#define NWPhysicalManipulatorH

#include <windows.h>
#include "../../Kernel/NBios.h"

namespace NMSDK {


/* *************************************************************************** */
class NWPhysicalManipulator: public NANet
{
public:
typedef __stdcall bool (*PInit)(HANDLE FormHandle,bool isemulator);
typedef __stdcall bool (*PDeInit)(void);
typedef __stdcall bool (*PComOpen)(unsigned short Port);
typedef __stdcall bool (*PComClose)(void);
typedef __stdcall bool (*PComStatus)(void);
typedef __stdcall bool (*PStart)(void);
typedef __stdcall bool (*PStop)(void);
typedef __stdcall bool (*PReset)(void);
typedef __stdcall bool (*PMoveServo)(unsigned char Servo,
										 unsigned char Dir,
										 unsigned char PWM,
										 unsigned char Time);
typedef __stdcall bool (*PGetServoData)(unsigned char servo, unsigned char *data);
typedef __stdcall void (*PSetExternalData)(real moment, real currenttime);
typedef __stdcall double (*PGetModelTime)(void);
typedef __stdcall bool (*PGetState)(void);
typedef __stdcall bool (*PNeiroPulse)(unsigned char Servo, unsigned char NumItem, unsigned char TypeItem);
typedef __stdcall bool (*PNeiroPulseGroup)(unsigned char Servo, unsigned char MaskGroup);
typedef __stdcall bool (*PGetNeiroSumm)(unsigned char Servo);
typedef __stdcall bool (*PSetNeiroParam)(unsigned char NeiroPulseValue,unsigned char NeiroAutoDecValue);
typedef __stdcall bool (*PSetWorkMode)(unsigned char WorkMode);
typedef __stdcall bool (*PAngleServo)(unsigned char Servo,
										 unsigned short Angle,
										 int Mode);
typedef __stdcall bool (*PDiffServo)(unsigned char Servo,
										 unsigned char Dir,
										 unsigned short Angle);
typedef __stdcall bool (*PHoldServo)(unsigned char Servo);
typedef __stdcall bool (*PFreeServo)(unsigned char Servo);
typedef __stdcall bool (*PSetMinPWM)(unsigned char Servo, unsigned char MinPWM);



struct TServoData {
 unsigned char N;
 double	Angle;
 double	Force;
 unsigned char   SetDir; //�������� ����������� ��������
 double	Speed; //������� ��������
 double Pressure;  //����������
 unsigned char	CurrentDir; //������� ����������� ��������
};

public: // ������������� ��������
// ��������� �� ���� (�������)
real MinMoment,MaxMoment;

// ��������� �� ����
real MinAngle, MaxAngle;

//�������� �� �������� ����������
real MinVoltage, MaxVoltage;

// ��������� ��������� �� ����
real FoundMinForce, FoundMaxForce;

// ��������� ��������� �� ��������
real FoundMinSpeed, FoundMaxSpeed;

HWND WindowHandle;

vector<pair<WPARAM,LPARAM> > Params;

TServoData* ServoData;

vector<real> PreviousAngles;
vector<unsigned> AnglesTimes;


size_t NumAnglesHistory;
real AnglesHistoryTime;

real AngleSpeed;

// �������� ����������� ����������
real OutputVoltage;

// ������� ����������� ����������
real InputVoltage;

// ��������� ��������� ����������� ����������
real OutputMul;

// ������������ ������������ �����������
real TimeDuration;

// ����������� �������� ������������ �����������
real MinControlVoltage;

// ��� �� ���������� � ����������� �� 1��
int AccumulationStep;

// ��� �� ������� � ����������� �� 1��
int DissociationStep;

// ����������� ����������
unsigned char RightDirection;
unsigned char LeftDirection;


bool EmulatorMode;

unsigned char ComPort;

unsigned char ServoNumber;

typedef enum {ServoLeft = 1, ServoRight = 2, ServoNone = 255} TServoDirect;

public: // ������
// ������������� ����������
HMODULE ManipulatorDLL;

PInit DMInit;
PDeInit DMDeInit;
PComOpen DMComOpen;
PComClose DMComClose;
PComStatus DMComStatus;
PStart DMStart;
PStop DMStop;
PReset DMReset;
PMoveServo DMMoveServo;
PGetServoData DMGetServoData;
PSetExternalData DMSetExternalData;
PGetModelTime DMGetModelTime;

PGetState DMGetState;
PNeiroPulse DMNeiroPulse;
PNeiroPulseGroup DMNeiroPulseGroup;
PGetNeiroSumm DMGetNeiroSumm;
PSetNeiroParam DMSetNeiroParam;
PSetWorkMode DMSetWorkMode;

PAngleServo DMAngleServo;
PDiffServo DMDiffServo;
PHoldServo DMHoldServo;
PFreeServo DMFreeServo;
PSetMinPWM DMSetMinPWM;

public: // ������������� ��������
// ����� ���������� ������������ ����������
// 0 - � ������
// 1 - � �����������
//int Mode;

// ����� ������ dll ������������
// 0 - �� �����
// 1 - �������� �����
// 2 - ��������� �����
// 3 - ���������������
int DllManipulatorMode;

protected: // ��������� ����������
// ������� ��������� ������� ������������ �����������
int SendCounter;

// �������� �������� ��������� ������� ������������ �����������
int MaxSendCounter;

// �������� �������� ��������� ���������� ������
int MaxReadCounter;

// ������� ��������� ���������� ������
int ReadCounter;

// ��� �����
real Current;

// ��� �����
real EMF;

// ���� ��������
real Angle;

// ������ ����������� ����������
real Moment;

// ����������� �������
real DiffMoment;

public:
// ��������� ����� �������� ������������ ������
unsigned int LastSentTime;
unsigned int CurrentTime;
unsigned int LastDuration;

protected: // ��������� ����������
// ��������� �������� ��������
vector<int> PulseState;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NWPhysicalManipulator(void);
//NWPhysicalManipulator(const string &name);
virtual ~NWPhysicalManipulator(void);
// --------------------------

// --------------------------
// ��������� ������ ���������� ��������
// --------------------------
// �������� ������ ��� ����� ������ ����� ������� ����� ������
virtual NWPhysicalManipulator* New(void);
// --------------------------

public:
// --------------------------
// ������ ���������� �������
// --------------------------
// �������� DLL
bool LoadManipulatorDll(void);

// �������� DLL
bool UnLoadManipulatorDll(void);

// ������������� ������������
bool InitManipulator(void);

// ��������������� ������������
bool UnInitManipulator(void);

// ��� �� ���������� � ����������� �� 1��
bool SetAccumulationStep(int value);

// ��� �� ������� � ����������� �� 1��
bool SetDissociationStep(int value);
// --------------------------

// --------------------------
// ������ ���������� �������������� ����������
// --------------------------
// ���������������� �����������
bool SetEMFactor(real value);

// �������������
bool SetInductance(real value);

// �������������
bool SetResistance(real value);

// ������������������� ���������� �������
bool SetTm(real value);

// ������������ �����
bool SetReductionRate(real value);
// --------------------------

// --------------------------
// Computation methods
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
virtual bool ADefault(void);

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
virtual bool ABuild(void);

// Reset computation
virtual bool AReset(void);

// Execute math. computations of current object on current step
virtual bool ACalculate(void);
// --------------------------
};
/* *************************************************************************** */

}

#endif
