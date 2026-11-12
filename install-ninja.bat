@echo off
setlocal
where ninja >nul 2>&1
if not errorlevel 1 exit /b 0
where winget >nul 2>&1
if errorlevel 1 (
  echo Install Ninja from https://github.com/ninja-build/ninja/releases and add it to PATH.
  echo Build-Windows.ps1 also locates the Ninja bundled with Visual Studio.
  exit /b 1
)
winget install --id Ninja-build.Ninja --exact --source winget
exit /b %errorlevel%
