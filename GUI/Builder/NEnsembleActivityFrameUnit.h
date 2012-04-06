//---------------------------------------------------------------------------

#ifndef NEnsembleActivityFrameUnitH
#define NEnsembleActivityFrameUnitH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include "WatchFrameUnit.h"
#include <ExtCtrls.hpp>
#include "../Libraries/NeuronLifeLib/NNeuronLifeLibrary.h"
//---------------------------------------------------------------------------
class TNEnsembleActivityFrame : public TFrame
{
__published:	// IDE-managed Components
	TPanel *Panel1;
	TWatchFrame *WatchFrame;
private:	// User declarations
public:		// User declarations
	__fastcall TNEnsembleActivityFrame(TComponent* Owner);

public: // Данные
NMSDK::NLifeNet* Network;

bool UpdateInterfaceFlag;

NMSDK::real WatchInterval;

// Выходные данные ансамблей
map<string, NMSDK::real> EnsemblesActivityData;

void UpdateInterface(void);
};
//---------------------------------------------------------------------------
extern PACKAGE TNEnsembleActivityFrame *NEnsembleActivityFrame;
//---------------------------------------------------------------------------
#endif
