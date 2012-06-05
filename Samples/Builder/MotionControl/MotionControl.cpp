//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop
#include <tchar.h>
//---------------------------------------------------------------------------




































USEFORM("..\..\..\RDK\GUI\Builder\UEngineMonitorFormUnit.cpp", UEngineMonitorForm);
USEFORM("..\..\..\RDK\GUI\Builder\UEngineMonitorFrameUnit.cpp", UEngineMonitorFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\Builder\UEngineControlFormUnit.cpp", UEngineControlForm);
USEFORM("..\..\..\RDK\GUI\Builder\UComponentsPerformanceFormUnit.cpp", UComponentsPerformanceForm);
USEFORM("..\..\..\RDK\GUI\Builder\UComponentsPerformanceFrameUnit.cpp", UComponentsPerformanceFrame); /* TFrame: File Type */
USEFORM("MainFormUnit.cpp", MainForm);
USEFORM("..\..\..\RDK\GUI\Builder\UComponentsListFrameUnit.cpp", UComponentsListFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\Builder\UClassesListFormUnit.cpp", UClassesListForm);
USEFORM("..\..\..\RDK\GUI\Builder\UClassesListFrameUnit.cpp", UClassesListFrame); /* TFrame: File Type */
USEFORM("..\..\..\GUI\Builder\TNDCEngineControlFormUnit.cpp", NDCEngineControlForm);
USEFORM("..\..\..\GUI\Builder\TNManipulatorControlForm.cpp", NManipulatorControlForm);
USEFORM("..\..\..\RDK\GUI\Builder\UComponentIOFrameUnit.cpp", UComponentIOFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\Builder\UComponentsControlFrameUnit.cpp", UComponentsControlFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\Builder\UComponentsListFormUnit.cpp", UComponentsListForm);
USEFORM("..\..\..\RDK\GUI\Builder\UComponentsControlFormUnit.cpp", UComponentsControlForm);
USEFORM("..\..\..\RDK\GUI\Builder\UComponentLinksFormUnit.cpp", UComponentLinksForm);
USEFORM("..\..\..\RDK\GUI\Builder\UComponentLinksFrameUnit.cpp", UComponentLinksFrame); /* TFrame: File Type */
//---------------------------------------------------------------------------
WINAPI _tWinMain(HINSTANCE, HINSTANCE, LPTSTR, int)
{
	try
	{
		Application->Initialize();
		Application->MainFormOnTaskBar = true;
		Application->CreateForm(__classid(TUEngineControlForm), &UEngineControlForm);
		Application->CreateForm(__classid(TMainForm), &MainForm);
		Application->CreateForm(__classid(TNDCEngineControlForm), &NDCEngineControlForm);
		Application->CreateForm(__classid(TNManipulatorControlForm), &NManipulatorControlForm);
		Application->CreateForm(__classid(TUClassesListForm), &UClassesListForm);
		Application->CreateForm(__classid(TUComponentsListForm), &UComponentsListForm);
		Application->CreateForm(__classid(TUComponentsPerformanceForm), &UComponentsPerformanceForm);
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
