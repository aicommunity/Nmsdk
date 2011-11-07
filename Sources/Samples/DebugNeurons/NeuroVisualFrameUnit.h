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
// ���� ������ ��������
// ---------------------------
// ---------------------------


// ---------------------------
// ��������� ����������
// ---------------------------
// ---------------------------

// ---------------------------
// ������ ������������ � NMSDK
// ---------------------------
// ������������� ����� ����
//bool SetNetwork(NANet *network);
// ---------------------------

// ---------------------------
// ������ �����������
// ---------------------------
// �������������� ���� � ������������ � �������� ����������� �����������
void DrawNetwork(void);
// ---------------------------
};
//---------------------------------------------------------------------------
extern PACKAGE TNeuroVisualFrame *NeuroVisualFrame;
//---------------------------------------------------------------------------
#endif
