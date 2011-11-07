//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "NANetGraphicsFrameUnit.h"
#include "TUBitmap.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TNANetGraphicsFrame *NANetGraphicsFrame;


//---------------------------------------------------------------------------
// -------------------------
// Методы управления данными
// -------------------------
NANet* TNANetGraphicsFrame::GetNetwork(void)
{
 return Network;
}

bool TNANetGraphicsFrame::SetNetwork(NANet *net)
{
 if(Network == net)
  return true;

 Network=net;
 if(NetGraphicsCanvas.GetLength() == 0)
 {
  NetGraphicsCanvas.SetRes(640,480,RDK::ubmRGB24);
  Width=NetGraphicsCanvas.GetWidth();
  Height=NetGraphicsCanvas.GetHeight();
 }

 NetGraphicsCanvas.SetColorModel(RDK::ubmRGB24);
 Graph.SetCanvas(&NetGraphicsCanvas);

 NetGraphics.SetEngine(&Graph);
 NetGraphics.SetNet(Network);

 UpdateInterface();
 return true;
}

void TNANetGraphicsFrame::UpdateInterface(void)
{
 UpdateInterfaceFlag=true;

 NetGraphics.Draw();
 NetGraphicsCanvas>>Image->Picture->Bitmap;
 Image->Repaint();

 UpdateInterfaceFlag=false;
}
// -------------------------
//---------------------------------------------------------------------------
__fastcall TNANetGraphicsFrame::TNANetGraphicsFrame(TComponent* Owner)
	: TFrame(Owner)
{
 Network=0;
 UpdateInterfaceFlag=false;
}
//---------------------------------------------------------------------------
