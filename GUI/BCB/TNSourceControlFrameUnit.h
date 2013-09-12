//---------------------------------------------------------------------------

#ifndef TNSourceControlFrameUnitH
#define TNSourceControlFrameUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>
#include <Grids.hpp>
#include "WatchFrameUnit.h"
#include <ComCtrls.hpp>

#include "../../Kernel/NBios.h"
//#include "NSource.h"
#include "../Libraries/BCL/NBCLLibrary.h"
#include "TUClassRegistryFrame.h"

using namespace NMSDK;

//---------------------------------------------------------------------------
class TNSourceControlFrame : public TFrame
{
__published:	// IDE-managed Components
	TPanel *Panel1;
	TPanel *Panel2;
	TSplitter *Splitter1;
	TGroupBox *GroupBox1;
	TStringGrid *SourcesStringGrid;
	TWatchFrame *SourceWatchFrame;
	TPanel *Panel3;
	TGroupBox *AmplitudeGroupBox;
	TTrackBar *AmplitudeTrackBar;
	TEdit *AmplitudeEdit;
	TGroupBox *FrequencyGroupBox;
	TTrackBar *FrequencyTrackBar;
	TEdit *FrequencyEdit;
	TUClassRegistryFrame *UClassRegistryFrame;
	void __fastcall FrequencyTrackBarChange(TObject *Sender);
	void __fastcall FrequencyEditChange(TObject *Sender);
	void __fastcall AmplitudeTrackBarChange(TObject *Sender);
	void __fastcall AmplitudeEditChange(TObject *Sender);
	void __fastcall UClassRegistryFrameLabeledEditKeyPress(TObject *Sender, wchar_t &Key);
	void __fastcall UClassRegistryFrameSetBitBtnClick(TObject *Sender);

private:	// User declarations
public:		// User declarations
	__fastcall TNSourceControlFrame(TComponent* Owner);

protected: // Данные
// Массив источников сигнала
vector<NSource*> Sources;

// Флаг обновления интерфейса
bool UpdateInterfaceFlag;

// Длительность интервала наблюдения
double WatchInterval;

// Реестр параметров
RDK::UClassRegistry Parameters;

// Режим добавления графиков
// 0 - начало отсчета неподвижно
// иначе - начало отсчета смещается для каждого графика на заданное число
double Origin;

public: // Методы
// Устанавливает интервал наблюдения
bool SetWatchInterval(double interval);

// Добавляет источник в массив
bool AddSource(NSource* source);

// Удаляет источник из массива
bool DelSource(NSource* source);

// Удаляет источник по индексу
bool DelSource(size_t index);

// Удаляет все источники
bool DelAllSources(void);

// Пополняет массив источников, всеми источниками из контейнера cont
// Возвращает число добавленных источников
int FindSources(NAContainer *cont);

// Активирует на форме источник с заданными индексами в массиве, и векторе выходов
bool SelectSource(size_t sourceindex, size_t outputindex);

// Обновляет список наблюдений графика
bool WatchUpdate(void);

// Обновляет состояние графика на очередном шаге счета
void StepUpdate(void);

// Обновляет интерфейс
void UpdateInterface(void);
};
//---------------------------------------------------------------------------
extern PACKAGE TNSourceControlFrame *NSourceControlFrame;
//---------------------------------------------------------------------------
#endif
