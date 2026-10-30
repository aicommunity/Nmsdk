//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop
//---------------------------------------------------------------------------
USEFORM("..\..\GUI\Builder\TNEnsembleControlFrameUnit.cpp", NEnsembleControlFrame); /* TFrame: File Type */
USEFORM("MuscleControlFormUnit.cpp", MuscleControlForm);
USEFORM("ManipulatorTestUnit.cpp", ManipulatorTestForm);
USEFORM("GraphicsFormUnit.cpp", GraphicsForm);
USEFORM("MuscleTestFormUnit.cpp", MuscleTestForm);
USEFORM("MainFormUnit.cpp", MainForm);
USEFORM("..\..\GUI\Builder\NLinksFrameUnit.cpp", NLinksFrame); /* TFrame: File Type */
USEFORM("..\..\GUI\Builder\NANetFrameUnit.cpp", NANetFrame); /* TFrame: File Type */
USEFORM("..\..\GUI\Builder\NANetGraphicsFrameUnit.cpp", NANetGraphicsFrame); /* TFrame: File Type */
USEFORM("..\..\MySDK4\GUI\Builder\ListInputFormUnit.cpp", ListInputForm);
USEFORM("..\..\MySDK4\GUI\Builder\WatchFrameUnit.cpp", WatchFrame); /* TFrame: File Type */
USEFORM("..\..\MySDK4\GUI\Builder\WatchWindowFormUnit.cpp", WatchWindowForm);
USEFORM("..\..\MySDK4\GUI\Builder\TUClassRegistryFrame.cpp", UClassRegistryFrame); /* TFrame: File Type */
USEFORM("..\..\MySDK4\GUI\Builder\SeriesControlUnit.cpp", SeriesControlForm);
USEFORM("..\..\MySDK4\GUI\Builder\ShowProgressBarUnit.cpp", ShowProgressBarForm);
//---------------------------------------------------------------------------
WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int)
{
	try
	{
		Application->Initialize();
		Application->CreateForm(__classid(TMainForm), &MainForm);
		Application->CreateForm(__classid(TMuscleTestForm), &MuscleTestForm);
		Application->CreateForm(__classid(TMuscleControlForm), &MuscleControlForm);
		Application->CreateForm(__classid(TManipulatorTestForm), &ManipulatorTestForm);
		Application->CreateForm(__classid(TGraphicsForm), &GraphicsForm);
		Application->CreateForm(__classid(TListInputForm), &ListInputForm);
		Application->CreateForm(__classid(TSeriesControlForm), &SeriesControlForm);
		Application->CreateForm(__classid(TShowProgressBarForm), &ShowProgressBarForm);
		Application->CreateForm(__classid(TWatchWindowForm), &WatchWindowForm);
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
