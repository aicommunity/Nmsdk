//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "NEnsembleActivityFrameUnit.h"
#include "TNSupport.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma link "WatchFrameUnit"
#pragma resource "*.dfm"
TNEnsembleActivityFrame *NEnsembleActivityFrame;
//---------------------------------------------------------------------------
__fastcall TNEnsembleActivityFrame::TNEnsembleActivityFrame(TComponent* Owner)
	: TFrame(Owner)
{
 UpdateInterfaceFlag=false;
 Network=0;
 WatchInterval=1;
}
//---------------------------------------------------------------------------
void TNEnsembleActivityFrame::UpdateInterface(void)
{
 if(!Network)
  return;

 UpdateInterfaceFlag=true;

 map<string, NMSDK::double>::iterator I,J;
 I=EnsemblesActivityData.begin();
 J=EnsemblesActivityData.end();
 for(;I!=J;++I)
  I->second=0;

 for(size_t i=0;i<Network->GetNumEnsembles();i++)
 {
  EnsemblesActivityData[Network->GetEnsembleName(i)]=Network->GetEnsembleActivity(i);

  NMSDK::AddWatch(WatchFrame, Network->GetEnsembleName(i),
			&EnsemblesActivityData[Network->GetEnsembleName(i)], WatchInterval);
 }

 WatchFrame->StepUpdate();

 UpdateInterfaceFlag=false;
}
//---------------------------------------------------------------------------
