@echo off
setlocal
set "PRESET=win-vs2022-ninja-release-vcpkgqt"
if not "%~1"=="" set "PRESET=%~1"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Scripts\Build-Windows.ps1" -Preset "%PRESET%" -WithWebEngine -Action configure
exit /b %errorlevel%
