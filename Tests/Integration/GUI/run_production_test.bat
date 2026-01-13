@echo off
REM Скрипт для запуска Test_QMessageBox_Production с использованием Qt DLL и плагинов из Bin/Platform/Win
REM Этот тест использует те же бинарники Qt, что и штатное приложение

setlocal enabledelayedexpansion

REM Получаем абсолютный путь к директории скрипта
set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%..\..\.."

REM Пути относительно корня проекта
set "TEST_EXE=%ROOT_DIR%\Bin\Platform\Win\Test_QMessageBox_Production.exe"
set "BIN_DIR=%ROOT_DIR%\Bin\Platform\Win"
set "PLUGINS_DIR=%BIN_DIR%\plugins"

REM Проверяем наличие исполняемого файла
if not exist "%TEST_EXE%" (
    echo ERROR: Test executable not found: %TEST_EXE%
    echo Please build the test first:
    echo   cmake --build <build_dir> --target Test_QMessageBox_Production --config Release
    pause
    exit /b 1
)

echo ========================================
echo QMessageBox Production Test Runner
echo ========================================
echo.
echo Using Qt DLL from: %BIN_DIR%
echo Using Qt plugins from: %PLUGINS_DIR%
echo.

REM Проверяем наличие Qt DLL
if not exist "%BIN_DIR%\Qt5Core.dll" (
    echo WARNING: Qt5Core.dll not found in %BIN_DIR%
    echo Make sure Qt DLLs are present in Bin/Platform/Win
    echo.
)

REM Проверяем наличие плагинов
if not exist "%PLUGINS_DIR%\platforms\qwindows.dll" (
    echo WARNING: Qt plugins not found in %PLUGINS_DIR%
    echo Make sure Qt plugins are present in Bin/Platform/Win/plugins
    echo.
)

REM Устанавливаем переменные окружения для Qt
REM PATH должен содержать Bin/Platform/Win для поиска Qt DLL
set "PATH=%BIN_DIR%;%PATH%"

REM QT_PLUGIN_PATH указывает на плагины
set "QT_PLUGIN_PATH=%PLUGINS_DIR%"

REM Также можно использовать QT_QPA_PLATFORM_PLUGIN_PATH
set "QT_QPA_PLATFORM_PLUGIN_PATH=%PLUGINS_DIR%\platforms"

echo Environment variables:
echo   PATH (first entry): %BIN_DIR%
echo   QT_PLUGIN_PATH: %QT_PLUGIN_PATH%
echo   QT_QPA_PLATFORM_PLUGIN_PATH: %QT_QPA_PLATFORM_PLUGIN_PATH%
echo.
echo Starting test...
echo.

REM Запускаем тест
"%TEST_EXE%"

if errorlevel 1 (
    echo.
    echo Test exited with error code: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Test completed successfully.
pause

endlocal
