@echo off
REM Скрипт для запуска Test_QMessageBox с правильными путями к Qt плагинам

setlocal enabledelayedexpansion

set "VCPKG_ROOT=E:\vcpkg"
set "TEST_EXE=build_test\Release\Test_QMessageBox.exe"
set "TEST_DIR=%~dp0build_test\Release"

REM Проверяем наличие исполняемого файла
if not exist "%TEST_EXE%" (
    echo ERROR: Test executable not found: %TEST_EXE%
    echo Please build the test first.
    pause
    exit /b 1
)

REM Проверяем, были ли развернуты Qt зависимости через windeployqt
if not exist "%TEST_DIR%\platforms\qwindows.dll" (
    echo Qt plugins not found in test directory.
    echo Running windeployqt to deploy Qt dependencies...
    echo.
    
    REM Ищем windeployqt
    set "WINDEPLOYQT="
    if exist "%VCPKG_ROOT%\buildtrees\qt5-tools\x64-windows-rel\bin\windeployqt.exe" (
        set "WINDEPLOYQT=%VCPKG_ROOT%\buildtrees\qt5-tools\x64-windows-rel\bin\windeployqt.exe"
    ) else if exist "%VCPKG_ROOT%\installed\x64-windows\tools\qt5-tools\bin\windeployqt.exe" (
        set "WINDEPLOYQT=%VCPKG_ROOT%\installed\x64-windows\tools\qt5-tools\bin\windeployqt.exe"
    )
    
    if "%WINDEPLOYQT%"=="" (
        echo ERROR: windeployqt not found!
        echo Please install qt5-tools via vcpkg or run windeployqt manually.
        pause
        exit /b 1
    )
    
    REM Запускаем windeployqt
    "%WINDEPLOYQT%" --release "%TEST_EXE%"
    if errorlevel 1 (
        echo ERROR: windeployqt failed!
        pause
        exit /b 1
    )
    
    echo.
    echo Qt dependencies deployed successfully.
    echo.
)

REM Устанавливаем переменные окружения для Qt
REM Плагины должны быть в той же директории, что и исполняемый файл
set "QT_PLUGIN_PATH=%TEST_DIR%"
set "PATH=%TEST_DIR%;%PATH%"

REM Также добавляем путь к Qt bin из vcpkg на случай, если нужны дополнительные DLL
if exist "%VCPKG_ROOT%\installed\x64-windows\bin" (
    set "PATH=%VCPKG_ROOT%\installed\x64-windows\bin;%PATH%"
)

echo Starting test...
echo Qt plugins path: %QT_PLUGIN_PATH%
echo.

REM Запускаем тест
"%TEST_EXE%"

endlocal
