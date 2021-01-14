mkdir InstallSources
xcopy "..\..\Bin\Platform\Win\SpikeTrainer.exe" InstallSources\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\SpikeTrainer.ini" InstallSources\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\borlndmm.dll" InstallSources\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\cc32220mt.dll" InstallSources\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\Fonts\*.*" InstallSources\Bin\Platform\Win\Fonts\ /Y /D
xcopy "..\..\Bin\Configs\SpikeAnsTrainer\*.*" InstallSources\Bin\Configs\SpikeAnsTrainer\*.* /Y /E /D
rmdir /Q /S InstallSources\Bin\Configs\SpikeAnsTrainer\EventsLog

