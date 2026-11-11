@echo off
setlocal
set "CONFIG=release"
if /I "%~1"=="debug" set "CONFIG=debug"
set "QTPROVIDER=vcpkgqt"
if defined QT_ROOT set "QTPROVIDER=localqt"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scripts\Build-Windows.ps1" -Preset win-vs2022-ninja-%CONFIG%-%QTPROVIDER%
exit /b %errorlevel%
