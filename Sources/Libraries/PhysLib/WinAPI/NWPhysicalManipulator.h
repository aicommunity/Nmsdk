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
 unsigned char   SetDir; //заданное направление вращения
 double	Speed; //угловая скорость
 double Pressure;  //напряжение
 unsigned char	CurrentDir; //текущее направление вращения
};

public: // Общедоступные свойства
// Диапазоны по току (моменту)
real MinMoment,MaxMoment;

// Диапазоны по углу
real MinAngle, MaxAngle;

//Дипазоны по входному напряжению
real MinVoltage, MaxVoltage;

// Найденные диапазоны по току
real FoundMinForce, FoundMaxForce;

// Найденные диапазоны по скорости
real FoundMinSpeed, FoundMaxSpeed;

HWND WindowHandle;

vector<pair<WPARAM,LPARAM> > Params;

TServoData* ServoData;

vector<real> PreviousAngles;
vector<unsigned> AnglesTimes;


size_t NumAnglesHistory;
real AnglesHistoryTime;

real AngleSpeed;

// Выходное управляющее напряжение
real OutputVoltage;

// Входное управляющее напряжение
real InputVoltage;

// Множитель выходного упрвляющего напряжения
real OutputMul;

// Длительность управляющего воздействия
real TimeDuration;

// Минимальная величина управляющего воздействия
real MinControlVoltage;

// Шаг по накоплению в контроллере за 1мс
int AccumulationStep;

// Шаг по разряду в контроллере за 1мс
int DissociationStep;

// Направление управления
unsigned char RightDirection;
unsigned char LeftDirection;


bool EmulatorMode;

unsigned char ComPort;

unsigned char ServoNumber;

typedef enum {ServoLeft = 1, ServoRight = 2, ServoNone = 255} TServoDirect;

public: // Данные
// Идентификатор библиотеки
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

public: // Общедоступные свойства
// Режим вычисления управляющего напряжения
// 0 - в модели
// 1 - в контроллере
//int Mode;

// Режим работы dll манипулятора
// 0 - Не задан
// 1 - Тестовый режим
// 2 - Командный режим
// 3 - Нейроуправление
int DllManipulatorMode;

protected: // Временные переменные
// Счетчик пропусков задания управляющего воздействия
int SendCounter;

// Максимум счетчика пропусков задания управляющего воздействия
int MaxSendCounter;

// Максимум счетчика пропусков считывания данных
int MaxReadCounter;

// Счетчик пропусков считывания данных
int ReadCounter;

// Ток якоря
real Current;

// ЭДС якоря
real EMF;

// Угол поворота
real Angle;

// Момент развиваемый двигателем
real Moment;

// Производная момента
real DiffMoment;

public:
// Последнее время отправки управляющего пакета
unsigned int LastSentTime;
unsigned int CurrentTime;
unsigned int LastDuration;

protected: // Временные переменные
// Состояния выходных нейронов
vector<int> PulseState;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NWPhysicalManipulator(void);
//NWPhysicalManipulator(const string &name);
virtual ~NWPhysicalManipulator(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NWPhysicalManipulator* New(void);
// --------------------------

public:
// --------------------------
// Методы управления железом
// --------------------------
// Загрузка DLL
bool LoadManipulatorDll(void);

// Выгрузка DLL
bool UnLoadManipulatorDll(void);

// Инициализация манипулятора
bool InitManipulator(void);

// Деинициализация манипулятора
bool UnInitManipulator(void);

// Шаг по накоплению в контроллере за 1мс
bool SetAccumulationStep(int value);

// Шаг по разряду в контроллере за 1мс
bool SetDissociationStep(int value);
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Электромагнитный коэффициент
bool SetEMFactor(real value);

// Индуктивность
bool SetInductance(real value);

// Сопротивление
bool SetResistance(real value);

// Электромеханическая постоянная времени
bool SetTm(real value);

// Передаточное число
bool SetReductionRate(real value);
// --------------------------

// --------------------------
// Computation methods
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool ADefault(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
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
