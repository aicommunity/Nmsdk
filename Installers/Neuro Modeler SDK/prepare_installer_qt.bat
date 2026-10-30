mkdir InstallSourcesQt
rem set QtPath=C:\Qt
rem set QtVersion=5.12.2
rem set QtCompiler=msvc2017_64
rem set QtFullPath=%QtPath5\%QtVersion%\%QtCompiler%\bin\
rem set path=%path%;%QtFullPath%
xcopy "..\..\Bin\Platform\Win\NeuroModeler.exe" InstallSourcesQt\Bin\Platform\Win\ /Y /D
xcopy "..\..\Bin\Platform\Win\NeuroModelerConsole.exe" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\Qt*.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\opencv_*.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\tbb.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\tbb_debug.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\NeuroModeler.ini" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\Fonts\*.*" InstallSourcesQt\Bin\Platform\Win\Fonts\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\boost*.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\libcurl*.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\libcrypto*.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\libssl*.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem xcopy "..\..\Bin\Platform\Win\double-conversion.dll" InstallSourcesQt\Bin\Platform\Win\ /Y /D
rem Clear old DLLs so no leftovers from previous builds
del /Q "InstallSourcesQt\Bin\Platform\Win\*.dll"

rem Copy full set of DLLs from Bin/Platform/Win
xcopy "..\..\Bin\Platform\Win\*.dll" InstallSourcesQt\Bin\Platform\Win\ /Y

rem Remove debug libraries by typical masks (suffix d, *_d, *_debug)
del /Q "InstallSourcesQt\Bin\Platform\Win\*d.dll"
del /Q "InstallSourcesQt\Bin\Platform\Win\*_d.dll"
del /Q "InstallSourcesQt\Bin\Platform\Win\*d1.dll"
del /Q "InstallSourcesQt\Bin\Platform\Win\python*_d.dll"
del /Q "InstallSourcesQt\Bin\Platform\Win\*_debug.dll"
del /Q "InstallSourcesQt\Bin\Platform\Win\QtWebEngineProcessd.exe"
del /Q "InstallSourcesQt\Bin\Platform\Win\*-gd-*.dll"

rem OpenCV optional (RDK_USE_OPENCV=OFF by default). NeuroModeler runs without opencv_*.dll.
del /Q "InstallSourcesQt\Bin\Platform\Win\opencv_*.dll"

rem Some libs in Bin/Platform/Win may be debug without explicit suffix in name.
rem If a DLL imports vcruntime140_1d.dll, replace it with release copy from vcpkg_installed (same filename).
powershell -NoProfile -Command "$dst='InstallSourcesQt\Bin\Platform\Win'; $src='..\..\vcpkg_installed\x64-windows\bin'; Get-ChildItem -File $dst -Filter *.dll | ForEach-Object { if (Select-String -SimpleMatch -Quiet 'vcruntime140_1d.dll' $_.FullName) { $cand = Join-Path $src $_.Name; if (Test-Path $cand) { Copy-Item -Force $cand $_.FullName } else { Write-Host ('NO_RELEASE_FOR ' + $_.Name) } } }"
del /Q "InstallSourcesQt\Bin\Platform\Win\*-gd-*.dll"

rem IMPORTANT: harfbuzz.dll in Bin/Platform/Win may be debug build without suffix in name.
rem Overwrite with release harfbuzz libs from vcpkg_installed.
copy /Y "..\..\vcpkg_installed\x64-windows\bin\harfbuzz.dll" "InstallSourcesQt\Bin\Platform\Win\harfbuzz.dll"
copy /Y "..\..\vcpkg_installed\x64-windows\bin\harfbuzz-subset.dll" "InstallSourcesQt\Bin\Platform\Win\harfbuzz-subset.dll"
xcopy "..\..\Bin\Platform\Win\qt.conf" InstallSourcesQt\Bin\Platform\Win\ /Y /D

xcopy "..\..\Bin\Configs\MC-RCN\*.*" InstallSourcesQt\Bin\Configs\MC-RCN\*.* /Y /E /D
xcopy "..\..\Bin\Configs\NM-Neurons\*.*" InstallSourcesQt\Bin\Configs\NM-Neurons\*.* /Y /E /D
xcopy "..\..\Bin\Configs\MC-Muscles\*.*" InstallSourcesQt\Bin\Configs\MC-Muscles\*.* /Y /E /D

xcopy "..\..\Docs\NMSDK.NeuronModel.ConfigurationSamples.Ru.doc" .\InstallSourcesQt\Docs\*.* /Y /D
xcopy "..\..\Docs\NMSDK.NeuronModel.Ru.doc" ".\InstallSourcesQt\Docs\*.*" /Y /D
xcopy "..\..\Rdk\Docs\RDK.GuiDescription.Bcb.Ru.doc" ".\InstallSourcesQt\Docs\*.*" /Y /D
xcopy "..\..\Rdk\Docs\RDK.RuntimeConfigurationDescription.Ru.doc" ".\InstallSourcesQt\Docs\*.*" /Y /D

xcopy "..\..\Bin\ClDesc\*.*" InstallSourcesQt\Bin\ClDesc\*.* /Y /D /E
xcopy "..\..\Bin\RTlibs\*.*" InstallSourcesQt\Bin\RTlibs\*.* /Y /D /E
xcopy "..\..\Bin\MockLibs\*.*" InstallSourcesQt\Bin\MockLibs\*.* /Y /D /E


xcopy "..\..\Bin\Platform\Win\plugins\platforms\*.dll" InstallSourcesQt\Bin\Platform\Win\plugins\platforms\*.dll /Y /E /D
xcopy "..\..\Bin\Platform\Win\plugins\platformthemes\*.dll" InstallSourcesQt\Bin\Platform\Win\plugins\platformthemes\*.dll /Y /E /D
xcopy "..\..\Bin\Platform\Win\plugins\printsupport\*.dll" InstallSourcesQt\Bin\Platform\Win\plugins\printsupport\*.dll /Y /E /D
xcopy "..\..\Bin\Platform\Win\plugins\styles\*.dll" InstallSourcesQt\Bin\Platform\Win\plugins\styles\*.dll /Y /E /D
xcopy "..\..\Bin\Platform\Win\resources\*.*" InstallSourcesQt\Bin\Platform\Win\resources\ /Y /E /D

rem Remove debug Qt platform plugins (they pull debug-CRT and freetyped.dll)
del /Q "InstallSourcesQt\Bin\Platform\Win\plugins\platforms\qwindowsd.dll"
del /Q "InstallSourcesQt\Bin\Platform\Win\plugins\platforms\qminimald.dll"
del /Q "InstallSourcesQt\Bin\Platform\Win\plugins\platforms\qoffscreend.dll"
del /Q "InstallSourcesQt\Bin\Platform\Win\plugins\platforms\qdirect2dd.dll"

rem Remove other debug Qt plugins (by actual debug CRT import) so target machine does not need vcruntime140_1d.dll etc.
powershell -NoProfile -Command "Get-ChildItem -Recurse -File 'InstallSourcesQt\Bin\Platform\Win\plugins' -Filter *.dll | ForEach-Object { if (Select-String -SimpleMatch -Quiet 'vcruntime140_1d.dll' $_.FullName) { Remove-Item -Force $_.FullName } }"

call "InstallSourcesQt\Bin\Configs\erase_all.bat"

"C:\Program Files (x86)\Actual Installer\actinst.exe" /S "NeuroModelerQt.aip"

