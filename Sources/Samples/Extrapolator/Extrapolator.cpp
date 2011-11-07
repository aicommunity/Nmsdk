//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop
#include <tchar.h>
//---------------------------------------------------------------------------
USEFORM("..\..\GUI\Builder\NLinksFrameUnit.cpp", NLinksFrame); /* TFrame: File Type */
USEFORM("..\..\GUI\Builder\TNSourceControlFrameUnit.cpp", NSourceControlFrame); /* TFrame: File Type */
USEFORM("..\..\GUI\Builder\NANetGraphicsFrameUnit.cpp", NANetGraphicsFrame); /* TFrame: File Type */
USEFORM("MainFormUnit.cpp", MainForm);
USEFORM("..\..\GUI\Builder\NANetFrameUnit.cpp", NANetFrame); /* TFrame: File Type */
USEFORM("..\..\RDK\GUI\Builder\ListInputFormUnit.cpp", ListInputForm);
USEFORM("..\..\RDK\GUI\Builder\SeriesControlUnit.cpp", SeriesControlForm);
USEFORM("..\..\RDK\GUI\Builder\ShowProgressBarUnit.cpp", ShowProgressBarForm);
USEFORM("..\..\RDK\GUI\Builder\TImagesFrameUnit.cpp", ImagesFrame); /* TFrame: File Type */
USEFORM("..\..\RDK\GUI\Builder\WatchFrameUnit.cpp", WatchFrame); /* TFrame: File Type */
USEFORM("..\..\RDK\GUI\Builder\WatchWindowFormUnit.cpp", WatchWindowForm);
USEFORM("..\..\RDK\GUI\Builder\TUClassRegistryFrame.cpp", UClassRegistryFrame); /* TFrame: File Type */
//---------------------------------------------------------------------------
WINAPI _tWinMain(HINSTANCE, HINSTANCE, LPTSTR, int)
{
	try
	{
		Application->Initialize();
		Application->MainFormOnTaskBar = true;
		Application->CreateForm(__classid(TMainForm), &MainForm);
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
