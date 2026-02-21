@echo off
REM Скрипт для установки qtwebengine с коротким buildtrees-путём и overlay портом
REM Использование: install-qtwebengine.bat [install-root]
REM   install-root: каталог для установки пакетов (по умолчанию: build\win-vs2022-release-vcpkgqt\vcpkg_installed)

set "VCPKG_ROOT=E:\vcpkg"
set "OVERLAY_PORTS=%~dp0vcpkg-overlay-ports"
REM Используем стандартный buildtrees каталог vcpkg
REM Overlay порт уже исправлен и не падает с FATAL_ERROR при длинном пути
set "BUILD_TREES_ROOT=%VCPKG_ROOT%\buildtrees"

REM Определяем каталог установки
if "%1"=="" (
    set "INSTALL_ROOT=%~dp0build\win-vs2022-release-vcpkgqt\vcpkg_installed"
) else (
    set "INSTALL_ROOT=%~1"
)

if not exist "%VCPKG_ROOT%\vcpkg.exe" (
    echo ERROR: vcpkg.exe not found at %VCPKG_ROOT%
    exit /b 1
)

if not exist "%OVERLAY_PORTS%" (
    echo ERROR: Overlay ports directory not found: %OVERLAY_PORTS%
    exit /b 1
)

echo ========================================
echo Installing qtwebengine
echo ========================================
echo VCPKG_ROOT: %VCPKG_ROOT%
echo OVERLAY_PORTS: %OVERLAY_PORTS%
echo INSTALL_ROOT: %INSTALL_ROOT%
echo BUILD_TREES_ROOT: %BUILD_TREES_ROOT%
echo.
echo This may take 30-60 minutes. Please be patient...
echo.

REM Используем стандартный buildtrees каталог vcpkg
REM Overlay порт автоматически обработает длинный путь, используя ../tmp если нужно
REM Очищаем старый каталог qtwebengine, если существует (может быть заблокирован)
echo Cleaning old qtwebengine build directory...
if exist "%BUILD_TREES_ROOT%\qtwebengine" (
    echo Removing %BUILD_TREES_ROOT%\qtwebengine...
    rmdir /s /q "%BUILD_TREES_ROOT%\qtwebengine" 2>nul
    if exist "%BUILD_TREES_ROOT%\qtwebengine" (
        echo WARNING: Could not remove %BUILD_TREES_ROOT%\qtwebengine. Trying to continue anyway...
    )
)
REM Также очищаем tmp каталог, если порт использовал его ранее
if exist "%BUILD_TREES_ROOT%\tmp\qtwebengine" (
    echo Removing %BUILD_TREES_ROOT%\tmp\qtwebengine...
    rmdir /s /q "%BUILD_TREES_ROOT%\tmp\qtwebengine" 2>nul
)

cd /d "%VCPKG_ROOT%"
echo.
echo Starting installation...
echo Note: Overlay port will automatically handle long paths if needed.
echo.
REM Используем стандартный buildtrees, overlay порт сам обработает длинный путь
"%VCPKG_ROOT%\vcpkg.exe" install qtwebengine:x64-windows --triplet x64-windows --overlay-ports="%OVERLAY_PORTS%" --x-install-root="%INSTALL_ROOT%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: qtwebengine installed successfully!
    echo You can now configure the project in Qt Creator.
) else (
    echo.
    echo ERROR: Installation failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
