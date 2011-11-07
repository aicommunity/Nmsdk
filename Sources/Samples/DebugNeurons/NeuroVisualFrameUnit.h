//---------------------------------------------------------------------------

#ifndef NeuroVisualFrameUnitH
#define NeuroVisualFrameUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>

#include <string>
#include "NGraphics.h"
#include "NTGraphics.h"

using namespace std;

//---------------------------------------------------------------------------
class TNeuroVisualFrame : public TFrame
{
__published:	// IDE-managed Components
	TImage *Image;
private:	// User declarations
public:		// User declarations
	__fastcall TNeuroVisualFrame(TComponent* Owner);

// ---------------------------
// База данных нейронов
// ---------------------------
// ---------------------------


// ---------------------------
// Временные переменные
// ---------------------------
// ---------------------------

// ---------------------------
// Методы коммуникации с NMSDK
// ---------------------------
// Устанавливает новую сеть
//bool SetNetwork(NANet *network);
// ---------------------------

// ---------------------------
// Методы отображения
// ---------------------------
// Перерисовывает сеть в соответствии с текущими настройками отображения
void DrawNetwork(void);
// ---------------------------
};
//---------------------------------------------------------------------------
extern PACKAGE TNeuroVisualFrame *NeuroVisualFrame;
//---------------------------------------------------------------------------
#endif
