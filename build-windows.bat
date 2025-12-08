@echo off
REM Скрипт сборки проекта Nmsdk под Windows с Visual Studio 2022
REM Использование: build-windows.bat [debug|release]

setlocal enabledelayedexpansion

REM Переключаем консоль в UTF-8 для читабельных сообщений
for /f "tokens=2 delims=:." %%i in ('chcp') do set "_OLDCP=%%i"
chcp 65001 >nul

set BUILD_TYPE=Release
set PRESET_NAME=win-vs2022-release
if /I "%1"=="debug" (
  set BUILD_TYPE=Debug
  set PRESET_NAME=win-vs2022-debug
)

echo ========================================
echo Nmsdk Windows Build Script
echo ========================================
echo Тип сборки: %BUILD_TYPE%
echo Пресет: %PRESET_NAME%
echo.

REM Проверка CMake, при отсутствии пробуем активировать среду VS
where cmake >nul 2>&1
if errorlevel 1 (
    echo INFO: CMake не найден в PATH. Пробуем активировать среду VS...
    call :try_vs_devcmd
    where cmake >nul 2>&1
    if errorlevel 1 (
        echo ERROR: CMake не найден. Установите CMake или запустите из Developer Command Prompt.
        goto :cleanup
    )
)

echo [1/5] Проверка CMake...
cmake --version
if errorlevel 1 (
    echo ERROR: Не удалось запустить CMake
    goto :cleanup
)
echo.

REM Проверка наличия Visual Studio 2022
echo [2/5] Проверка Visual Studio 2022...
if not exist "C:\Program Files\Microsoft Visual Studio\2022" (
    echo WARNING: Visual Studio 2022 не найден в стандартном месте. Продолжаем, если DevCmd уже активирован.
)
echo.

REM Проверка подмодулей
echo [3/5] Проверка подмодулей Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Git не найден, пропускаем проверку подмодулей
) else (
    echo Проверка подмодулей...
    git submodule status
    if errorlevel 1 (
        echo Инициализация подмодулей...
        git submodule update --init --recursive
        if errorlevel 1 (
            echo WARNING: Не удалось инициализировать подмодули. Продолжаем...
        )
    )
)
echo.

REM Проверка vcpkg
echo [4/5] Проверка vcpkg...
if "%VCPKG_ROOT%"=="" (
    set "VCPKG_ROOT=%~dp0vcpkg"
    echo NOTICE: VCPKG_ROOT не задан, используем по умолчанию %VCPKG_ROOT%
)
echo VCPKG_ROOT: %VCPKG_ROOT%
if not exist "%VCPKG_ROOT%\scripts\buildsystems\vcpkg.cmake" (
    echo WARNING: vcpkg.cmake не найден по пути %VCPKG_ROOT%
)
echo.

echo [5/5] Конфигурация и сборка (preset %PRESET_NAME%)...
echo.

REM Конфигурация CMake
echo Конфигурация CMake...
cmake --preset %PRESET_NAME%
if errorlevel 1 (
    echo ERROR: Не удалось сконфигурировать проект
    goto :cleanup
)
echo.

REM Сборка проекта
echo Сборка проекта...
cmake --build --preset %PRESET_NAME% --config %BUILD_TYPE% --parallel
if errorlevel 1 (
    echo ERROR: Сборка завершилась с ошибками
    goto :cleanup
)
echo.

echo ========================================
echo Сборка успешно завершена!
echo ========================================
echo Исполняемые файлы: Bin\Platform\Win\
echo Библиотеки: Bin\Platform\Win\Lib.CMake\
echo.

:cleanup
if defined _OLDCP chcp %_OLDCP% >nul
endlocal
goto :eof

:try_vs_devcmd
REM Пытаемся найти VS2022 через vswhere и вызвать VsDevCmd для добавления CMake/MSVC в PATH
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" (
  echo INFO: vswhere не найден, пропускаем попытку автопоиска VS.
  goto :eof
)
for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VSINSTALL=%%i"
if "%VSINSTALL%"=="" (
  echo INFO: Visual Studio 2022 не найдено через vswhere.
  goto :eof
)
set "VSDEVCMD=%VSINSTALL%\Common7\Tools\VsDevCmd.bat"
if exist "%VSDEVCMD%" (
  echo INFO: Активируем среду через %VSDEVCMD% ...
  call "%VSDEVCMD%" -arch=x64 -host_arch=x64 >nul
) else (
  echo INFO: VsDevCmd.bat не найден по пути %VSDEVCMD%.
)
goto :eof

