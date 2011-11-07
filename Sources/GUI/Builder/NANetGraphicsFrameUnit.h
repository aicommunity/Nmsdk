//---------------------------------------------------------------------------

#ifndef NANetGraphicsFrameUnitH
#define NANetGraphicsFrameUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ExtCtrls.hpp>
#include "NGraphics.h"
#include "rdk.h"

using namespace NMSDK;

//---------------------------------------------------------------------------
class TNANetGraphicsFrame : public TFrame
{
__published:	// IDE-managed Components
	TImage *Image;
private:	// User declarations
public:		// User declarations
	__fastcall TNANetGraphicsFrame(TComponent* Owner);

protected: // Данные
// Данные отрисовки
UBitmap NetGraphicsCanvas;
UGraphics Graph;
NGraphics NetGraphics;

// Управляемый компонент
NANet *Network;

// Флаг обновления интерфейса
bool UpdateInterfaceFlag;

public: // Методы
// -------------------------
// Методы управления данными
// -------------------------
NANet* GetNetwork(void);
bool SetNetwork(NANet *net);

void UpdateInterface(void);
// -------------------------
};
//---------------------------------------------------------------------------
extern PACKAGE TNANetGraphicsFrame *NANetGraphicsFrame;
//---------------------------------------------------------------------------
#endif
