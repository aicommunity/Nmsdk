//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop
#include <tchar.h>
//---------------------------------------------------------------------------


































USEFORM("..\..\..\RDK\GUI\BCB\UEngineControlFormUnit.cpp", UEngineControlForm);
USEFORM("..\..\..\RDK\GUI\BCB\UEngineMonitorFormUnit.cpp", UEngineMonitorForm);
USEFORM("..\..\..\RDK\GUI\BCB\UEngineMonitorFrameUnit.cpp", UEngineMonitorFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\BCB\UComponentsPerformanceFrameUnit.cpp", UComponentsPerformanceFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\BCB\UComponentsListFormUnit.cpp", UComponentsListForm);
USEFORM("..\..\..\RDK\GUI\BCB\UComponentsListFrameUnit.cpp", UComponentsListFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\BCB\UComponentsPerformanceFormUnit.cpp", UComponentsPerformanceForm);
USEFORM("..\..\..\RDK\GUI\BCB\UListInputFormUnit.cpp", UListInputForm);
USEFORM("MainFormUnit.cpp", MainForm);
USEFORM("..\..\..\RDK\GUI\BCB\UWatchFrameUnit.cpp", UWatchFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\BCB\USeriesControlUnit.cpp", USeriesControlForm);
USEFORM("..\..\..\RDK\GUI\BCB\UShowProgressBarUnit.cpp", UShowProgressBarForm);
USEFORM("..\..\..\RDK\GUI\BCB\UWatchFormUnit.cpp", UWatchForm);
USEFORM("..\..\..\RDK\GUI\BCB\UComponentsControlFrameUnit.cpp", UComponentsControlFrame); /* TFrame: File Type */
USEFORM("..\..\..\GUI\BCB\TNManipulatorControlForm.cpp", NManipulatorControlForm);
USEFORM("..\..\..\GUI\BCB\TNDCEngineControlFormUnit.cpp", NDCEngineControlForm);
USEFORM("..\..\..\RDK\GUI\BCB\TUVisualControllerFormUnit.cpp", UVisualControllerForm);
USEFORM("..\..\..\RDK\GUI\BCB\UComponentLinksFormUnit.cpp", UComponentLinksForm);
USEFORM("..\..\..\RDK\GUI\BCB\UComponentLinksFrameUnit.cpp", UComponentLinksFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\BCB\UComponentsControlFormUnit.cpp", UComponentsControlForm);
USEFORM("..\..\..\RDK\GUI\BCB\UComponentIOFrameUnit.cpp", UComponentIOFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\BCB\TUVisualControllerFrameUnit.cpp", UVisualControllerFrame); /* TFrame: File Type */
USEFORM("..\..\..\RDK\GUI\BCB\UClassesListFormUnit.cpp", UClassesListForm);
USEFORM("..\..\..\RDK\GUI\BCB\UClassesListFrameUnit.cpp", UClassesListFrame);
USEFORM("..\..\..\RDK\GUI\BCB\UCRPerseptronFormUnit.cpp", UCRPerseptronForm);
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
		Application->CreateForm(__classid(TUWatchForm), &UWatchForm);
		Application->CreateForm(__classid(TUSeriesControlForm), &USeriesControlForm);
		Application->CreateForm(__classid(TUListInputForm), &UListInputForm);
		Application->CreateForm(__classid(TUVisualControllerForm), &UVisualControllerForm);
		Application->CreateForm(__classid(TUShowProgressBarForm), &UShowProgressBarForm);
		Application->CreateForm(__classid(TUCRPerseptronForm), &UCRPerseptronForm);
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

