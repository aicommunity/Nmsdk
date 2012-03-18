//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop
#include <tchar.h>
//---------------------------------------------------------------------------
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UComponentsListFrameUnit.cpp", UComponentsListFrame); /* TFrame: File Type */
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UEngineMonitorFormUnit.cpp", UEngineMonitorForm);
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UComponentsControlFrameUnit.cpp", UComponentsControlFrame); /* TFrame: File Type */
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UComponentsListFormUnit.cpp", UComponentsListForm);
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UComponentLinksFormUnit.cpp", UComponentLinksForm);
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UComponentLinksFrameUnit.cpp", UComponentLinksFrame); /* TFrame: File Type */
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UEngineMonitorFrameUnit.cpp", UEngineMonitorFrame); /* TFrame: File Type */
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UComponentIOFrameUnit.cpp", UComponentIOFrame); /* TFrame: File Type */
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UComponentsControlFormUnit.cpp", UComponentsControlForm);
USEFORM("MainFormUnit.cpp", MainForm);
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UClassesListFormUnit.cpp", UClassesListForm);
USEFORM("..\..\ThirdParty\RDK\GUI\Builder\UClassesListFrameUnit.cpp", UClassesListFrame); /* TFrame: File Type */
//---------------------------------------------------------------------------
WINAPI _tWinMain(HINSTANCE, HINSTANCE, LPTSTR, int)
{
	try
	{
		Application->Initialize();
		Application->MainFormOnTaskBar = true;
		Application->CreateForm(__classid(TMainForm), &MainForm);
		Application->CreateForm(__classid(TUComponentsListForm), &UComponentsListForm);
		Application->CreateForm(__classid(TUClassesListForm), &UClassesListForm);
		Application->CreateForm(__classid(TUEngineMonitorForm), &UEngineMonitorForm);
		Application->CreateForm(__classid(TUComponentsControlForm), &UComponentsControlForm);
		Application->CreateForm(__classid(TUComponentLinksForm), &UComponentLinksForm);
		Application->Run();
	}
	catch (Exception &exception)
	{
		Application->ShowException(&exception);
	}
	catch (...)
	{
		try
		{
			throw Exception("");
		}
		catch (Exception &exception)
		{
			Application->ShowException(&exception);
		}
	}
	return 0;
}
//---------------------------------------------------------------------------
