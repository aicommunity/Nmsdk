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

typedef enum {ServoLeft = 0, ServoRight = 1, ServoNone = 255} TServoDirect;

public: // Данные
// Идентификатор библиотеки
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


public: // Общедоступные свойства
// Режим вычисления управляющего напряжения
// 0 - в модели
// 1 - в контроллере
int Mode;

protected: // Временные переменные
// Счетчик пропусков задания управляющего воздействия
int SendCounter;

// Максимум счетчика пропусков задания управляющего воздействия
int MaxSendCounter;

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
