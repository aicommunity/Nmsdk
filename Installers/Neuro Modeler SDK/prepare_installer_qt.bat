mkdir InstallSourcesQt
rem set QtPath=C:\Qt
rem set QtVersion=5.12.2
rem set QtCompiler=msvc2017_64
rem set QtFullPath=%QtPath5\%QtVersion%\%QtCompiler%\bin\
rem set path=%path%;%QtFullPath%
xcopy "..\..\Bin\Platform\Win\NeuroModeler.exe" InstallSourcesQt\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\NeuroModelerConsole.exe" InstallSourcesQt\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\Qt*.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\opencv_*.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\tbb.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\tbb_debug.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\NeuroModeler.ini" InstallSourcesQt\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\Fonts\*.*" InstallSourcesQt\Bin\Platform\Win\Fonts\ /Y /D
xcopy "..\..\Bin\Configs\MC-RCN\*.*" InstallSourcesQt\Bin\Configs\MC-RCN\*.* /Y /E /D
xcopy "..\..\Bin\Configs\NM-Neurons\*.*" InstallSourcesQt\Bin\Configs\NM-Neurons\*.* /Y /E /D
xcopy "..\..\Bin\Configs\MC-Muscles\*.*" InstallSourcesQt\Bin\Configs\MC-Muscles\*.* /Y /E /D
xcopy "..\..\Docs\NMSDK.NeuronModel.ConfigurationSamples.Ru.doc" InstallSourcesQt\Docs\NMSDK.NeuronModel.ConfigurationSamples.Ru.doc /Y /D
xcopy "..\..\Docs\NMSDK.NeuronModel.Ru.doc" InstallSourcesQt\Docs\NMSDK.NeuronModel.Ru.doc /Y /D
xcopy "..\..\Rdk\Docs\RDK.GuiDescription.Bcb.Ru.doc" InstallSourcesQt\Docs\RDK.GuiDescription.Bcb.Ru.doc /Y /D
xcopy "..\..\Rdk\Docs\RDK.RuntimeConfigurationDescription.Ru.doc" InstallSourcesQt\Docs\RDK.RuntimeConfigurationDescription.Ru.doc /Y /D
call "InstallSourcesQt\Bin\Configs\erase_all.bat"

rem "C:\Program Files (x86)\Actual Installer\actinst.exe" /S "NeuroModelerQt.aip"

