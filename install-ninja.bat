@echo off
REM Скрипт для установки Ninja через vcpkg или системно

setlocal

set "VCPKG_ROOT=E:\vcpkg"

echo ========================================
echo Installing Ninja...
echo ========================================

REM Вариант 1: Установить через vcpkg (рекомендуется)
if exist "%VCPKG_ROOT%\vcpkg.exe" (
    echo Installing ninja through vcpkg...
    "%VCPKG_ROOT%\vcpkg.exe" install ninja:x64-windows --triplet x64-windows
    if errorlevel 1 (
        echo WARNING: Failed to install ninja through vcpkg
    ) else (
        echo Ninja installed successfully through vcpkg
        goto :done
    )
)

REM Вариант 2: Установить через Chocolatey (если установлен)
where choco >nul 2>&1
if %errorlevel% equ 0 (
    echo Installing ninja through Chocolatey...
    choco install ninja -y
    if errorlevel 1 (
        echo WARNING: Failed to install ninja through Chocolatey
    ) else (
        echo Ninja installed successfully through Chocolatey
        goto :done
    )
)

REM Вариант 3: Скачать вручную
echo.
echo Ninja not found. Please install it manually:
echo 1. Download from: https://github.com/ninja-build/ninja/releases
echo 2. Extract ninja.exe to a directory in your PATH
echo 3. Or add it to PATH: set PATH=%PATH%;C:\path\to\ninja
echo.
echo Alternatively, use Visual Studio generator instead of Ninja in CMakePresets.json

:done
echo.
echo ========================================
echo Done!
echo ========================================

endlocal
