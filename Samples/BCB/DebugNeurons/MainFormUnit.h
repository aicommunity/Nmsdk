//---------------------------------------------------------------------------

#ifndef MainFormUnitH
#define MainFormUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <Grids.hpp>
#include <ExtCtrls.hpp>
#include <ComCtrls.hpp>
#include "WatchWindowFormUnit.h"

#include "NFrequencyReceiver.h"
#include "TUClassRegistryFrame.h"

#include "NEnvironment.h"
#include "NBCLLibrary.h"
#include "NActLibrary.h"
#include "NCRLibrary.h"
#include "NPulseLibrary.h"
#include "NMathLibrary.h"
#include "NPhysLibrary.h"
#include "NSensorLibrary.h"

#include "NMSDK.h"
#include "NGraphics.h"
#include "mysdk.h"

using namespace NMSDK;
//---------------------------------------------------------------------------
class TMainForm : public TForm
{
__published:	// IDE-managed Components
	TGroupBox *GroupBox1;
	TStringGrid *StringGrid1;
	TGroupBox *GroupBox2;
	TStringGrid *StringGrid2;
	TTimer *Timer;
	TPanel *Panel1;
	TButton *Button2;
	TButton *Button1;
	TButton *Button3;
	TButton *Button4;
	TButton *Button5;
	TButton *Button6;
	TUClassRegistryFrame *ClassRegistryFrame;
	void __fastcall FormShow(TObject *Sender);
	void __fastcall Button1Click(TObject *Sender);
	void __fastcall StringGrid2SelectCell(TObject *Sender, int ACol, int ARow,
          bool &CanSelect);
	void __fastcall Button3Click(TObject *Sender);
	void __fastcall Button4Click(TObject *Sender);
	void __fastcall FormClose(TObject *Sender, TCloseAction &Action);
	void __fastcall TimerTimer(TObject *Sender);
	void __fastcall Button6Click(TObject *Sender);
	void __fastcall ClassRegistryFrame1SetBitBtnClick(TObject *Sender);
	void __fastcall Button2Click(TObject *Sender);
private:	// User declarations
public:		// User declarations
		__fastcall TMainForm(TComponent* Owner);

NStorage *Storage;

//NModel *Model;

UBitmap grcanvas;
UGraphics ugraph;

NGraphics ngraph;
LongIdT netid;

NEnvironment Environment;

NBCLLibrary BCLLibrary;
NActLibrary ActLibrary;
NCRLibrary CRLibrary;
NPulseLibrary PulseLibrary;
NMathLibrary MathLibrary;
NPhysLibrary PhysLibrary;
NSensorLibrary SensorLibrary;

NPulseNeuronLibrary PulseNeuronLibrary;



		real CurrentOut;

		// Текущий выделенный item
		NADItem *Selected;
		NAContainer *CSelected;
		UClassRegistry CSelectedRegistry;


		// Метод формирования модели простого импульсного нейрона
		NPulseNeuron* CreateSimplePulseNeuron(NStorage *storage, int num_membranes, int num_stimulates, int num_arresting);

		// Метод формирования модели афферентного нейрона
		NAfferentNeuron* CreateAfferentNeuron(NStorage *storage, int num_membranes);

		// Формируем сеть управления мышцами
		void CreateMuscleControl(NStorage *storage, NANet *net,TWatchFrame *watch);

		// Формируем сеть тестирования нейронов
		void CreateNeuralTest(NStorage *storage, NANet *net,TWatchFrame *watch);

		// Формируем СУ двигательной единицей
		void CreateMotionElement(NStorage *storage, NANet *net);

		// Добавляем объект в окно наблюдений
		void AddWatch(NAContainer *item, int output, TWatchFrame *watch, real yshift=0, TPenStyle style=psSolid, TColor color=0);
		void AddFrequencyWatch(NAContainer *item,TWatchFrame *watch, real yshift=0, TPenStyle style=psSolid, TColor color=0);

};
//---------------------------------------------------------------------------
extern PACKAGE TMainForm *MainForm;
//---------------------------------------------------------------------------
#endif
