@echo off
REM Скрипт для исправления vcpkg после обновления
REM Пересобирает vcpkg и проверяет наличие необходимых файлов

setlocal

set "VCPKG_ROOT=E:\vcpkg"

if not exist "%VCPKG_ROOT%" (
    echo ERROR: vcpkg directory not found: %VCPKG_ROOT%
    exit /b 1
)

echo ========================================
echo Fixing vcpkg installation...
echo ========================================

cd /d "%VCPKG_ROOT%"

echo.
echo Step 1: Rebuilding vcpkg...
call bootstrap-vcpkg.bat
if errorlevel 1 (
    echo ERROR: vcpkg bootstrap failed
    exit /b 1
)

echo.
echo Step 2: Checking vcpkg-tools.json...
if exist "scripts\vcpkg-tools.json" (
    echo OK: vcpkg-tools.json found
) else (
    echo WARNING: vcpkg-tools.json not found
)

echo.
echo Step 3: Checking vcpkg.exe...
if exist "vcpkg.exe" (
    echo OK: vcpkg.exe found
) else (
    echo ERROR: vcpkg.exe not found after bootstrap
    exit /b 1
)

echo.
echo ========================================
echo vcpkg fix completed!
echo ========================================
echo.
echo Next steps:
echo 1. Restart Qt Creator
echo 2. Try to configure the project again
echo.

endlocal
