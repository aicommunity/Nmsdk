// ===========================================================
// Version:        1.0.0
// ===========================================================
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
class NWPhysicalManipulator: public NADItem
{
typedef __stdcall bool (*PDLLManipulatorInit)(HANDLE FormHandle,bool isemulator);
typedef __stdcall bool (*PDLLManipulatorDeInit)(void);
typedef __stdcall bool (*PDLLManipulatorComOpen)(unsigned short Port);
typedef __stdcall bool (*PDLLManipulatorComClose)(void);
typedef __stdcall bool (*PDLLManipulatorComStatus)(void);
typedef __stdcall bool (*PDLLManipulatorStart)(void);
typedef __stdcall bool (*PDLLManipulatorStop)(void);
typedef __stdcall bool (*PDLLManipulatorReset)(void);
typedef __stdcall bool (*PDLLManipulatorMoveServo)(unsigned char Servo,
										 unsigned char Dir,
										 unsigned char PWM,
										 unsigned char Time);
typedef __stdcall bool (*PDLLManipulatorGetServoData)(unsigned char servo, unsigned char *data);
typedef __stdcall void (*PDLLManipulatorSetExternalData)(real moment, real currenttime);
typedef __stdcall double (*PDLLManipulatorGetModelTime)(void);

struct TServoData {
 unsigned char N;
 double	Angle;
 double	Force;
 unsigned char	Dir;
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

typedef enum {ServoLeft = 0, ServoRight = 1, ServoNone = 255} TServoDirect;

public: // ������
// ������������� ����������
HMODULE ManipulatorDLL;

PDLLManipulatorInit DLLManipulatorInit;
PDLLManipulatorDeInit DLLManipulatorDeInit;
PDLLManipulatorComOpen DLLManipulatorComOpen;
PDLLManipulatorComClose DLLManipulatorComClose;
PDLLManipulatorComStatus DLLManipulatorComStatus;
PDLLManipulatorStart DLLManipulatorStart;
PDLLManipulatorStop DLLManipulatorStop;
PDLLManipulatorReset DLLManipulatorReset;
PDLLManipulatorMoveServo DLLManipulatorMoveServo;
PDLLManipulatorGetServoData DLLManipulatorGetServoData;
PDLLManipulatorSetExternalData DLLManipulatorSetExternalData;
PDLLManipulatorGetModelTime DLLManipulatorGetModelTime;


public: // ������������� ��������
// ����� ���������� ������������ ����������
// 0 - � ������
// 1 - � �����������
int Mode;

protected: // ��������� ����������
// ������� ��������� ������� ������������ �����������
int SendCounter;

// �������� �������� ��������� ������� ������������ �����������
int MaxSendCounter;

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
