//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop
//---------------------------------------------------------------------------
USEFORM("..\..\RDK\GUI\Builder\SeriesControlUnit.cpp", SeriesControlForm);
USEFORM("..\..\RDK\GUI\Builder\ListInputFormUnit.cpp", ListInputForm);
USEFORM("..\..\RDK\GUI\Builder\TImagesFrameUnit.cpp", ImagesFrame); /* TFrame: File Type */
USEFORM("StatisticFormUnit.cpp", StatisticForm);
USEFORM("..\..\RDK\GUI\Builder\ShowProgressBarUnit.cpp", ShowProgressBarForm);
USEFORM("MuscleTestFormUnit.cpp", MuscleTestForm);
USEFORM("..\..\GUI\Builder\NLinksFrameUnit.cpp", NLinksFrame); /* TFrame: File Type */
USEFORM("LinksFormUnit.cpp", LinksForm);
USEFORM("MuscleControlFormUnit.cpp", MuscleControlForm);
USEFORM("SourcesControlFormUnit.cpp", SourcesControlForm);
USEFORM("..\..\RDK\GUI\Builder\WatchFrameUnit.cpp", WatchFrame); /* TFrame: File Type */
USEFORM("MainFormUnit.cpp", MainForm);
USEFORM("..\..\RDK\GUI\Builder\TUClassRegistryFrame.cpp", UClassRegistryFrame); /* TFrame: File Type */
USEFORM("ManipulatorTestUnit.cpp", ManipulatorTestForm);
USEFORM("GraphicsFormUnit.cpp", GraphicsForm);
USEFORM("..\..\GUI\Builder\NANetFrameUnit.cpp", NANetFrame); /* TFrame: File Type */
USEFORM("..\..\GUI\Builder\NANetGraphicsFrameUnit.cpp", NANetGraphicsFrame); /* TFrame: File Type */
USEFORM("..\..\GUI\Builder\TNEnsembleControlFrameUnit.cpp", NEnsembleControlFrame); /* TFrame: File Type */
USEFORM("..\..\GUI\Builder\TNSourceControlFrameUnit.cpp", NSourceControlFrame); /* TFrame: File Type */
USEFORM("..\..\GUI\Builder\NEnsembleActivityFrameUnit.cpp", NEnsembleActivityFrame); /* TFrame: File Type */
USEFORM("..\..\RDK\GUI\Builder\WatchWindowFormUnit.cpp", WatchWindowForm);
//---------------------------------------------------------------------------
WINAPI WinMain(HINSTANCE inst, HINSTANCE, LPSTR, int)
{
	try
	{
		Application->Initialize();
		Application->CreateForm(__classid(TMainForm), &MainForm);
		Application->CreateForm(__classid(TMuscleTestForm), &MuscleTestForm);
		Application->CreateForm(__classid(TMuscleControlForm), &MuscleControlForm);
		Application->CreateForm(__classid(TManipulatorTestForm), &ManipulatorTestForm);
		Application->CreateForm(__classid(TGraphicsForm), &GraphicsForm);
		Application->CreateForm(__classid(TSourcesControlForm), &SourcesControlForm);
		Application->CreateForm(__classid(TNANetFrame), &NANetFrame);
		Application->CreateForm(__classid(TStatisticForm), &StatisticForm);
		Application->CreateForm(__classid(TListInputForm), &ListInputForm);
		Application->CreateForm(__classid(TSeriesControlForm), &SeriesControlForm);
		Application->CreateForm(__classid(TShowProgressBarForm), &ShowProgressBarForm);
		Application->CreateForm(__classid(TWatchWindowForm), &WatchWindowForm);
		Application->CreateForm(__classid(TNLinksFrame), &NLinksFrame);
		Application->CreateForm(__classid(TLinksForm), &LinksForm);
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
