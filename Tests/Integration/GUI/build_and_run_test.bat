@echo off
REM Скрипт для быстрой компиляции и запуска теста QMessageBox в Windows
REM Требуется: Qt5 или Qt6, установленный в стандартном месте или переменная окружения QTDIR

echo ========================================
echo QMessageBox Test Build Script for Windows
echo ========================================
echo.

REM Проверяем наличие Qt
if defined QTDIR (
    echo Found QTDIR: %QTDIR%
    set QT_INCLUDE=%QTDIR%\include
    set QT_LIB=%QTDIR%\lib
) else (
    echo QTDIR not set, trying default locations...
    if exist "C:\Qt\5.15.2\msvc2019_64" (
        set QT_INCLUDE=C:\Qt\5.15.2\msvc2019_64\include
        set QT_LIB=C:\Qt\5.15.2\msvc2019_64\lib
        echo Found Qt5 at: C:\Qt\5.15.2\msvc2019_64
    ) else if exist "C:\Qt\6.5.0\msvc2019_64" (
        set QT_INCLUDE=C:\Qt\6.5.0\msvc2019_64\include
        set QT_LIB=C:\Qt\6.5.0\msvc2019_64\lib
        echo Found Qt6 at: C:\Qt\6.5.0\msvc2019_64
    ) else (
        echo ERROR: Qt not found! Please set QTDIR environment variable.
        pause
        exit /b 1
    )
)

echo.
echo Compiling Test_QMessageBox_Standalone.cpp...
echo.

REM Определяем компилятор
where cl >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Using MSVC compiler...
    cl /EHsc /MD Test_QMessageBox_Standalone.cpp ^
        /I"%QT_INCLUDE%" ^
        /link /LIBPATH:"%QT_LIB%" Qt5Core.lib Qt5Widgets.lib /SUBSYSTEM:WINDOWS /OUT:Test_QMessageBox_Standalone.exe
    if %ERRORLEVEL% NEQ 0 (
        echo Compilation failed!
        pause
        exit /b 1
    )
) else (
    where g++ >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Using MinGW/GCC compiler...
        g++ -o Test_QMessageBox_Standalone.exe Test_QMessageBox_Standalone.cpp ^
            -I"%QT_INCLUDE%" ^
            -L"%QT_LIB%" ^
            -lQt5Core -lQt5Widgets -fPIC -mwindows
        if %ERRORLEVEL% NEQ 0 (
            echo Compilation failed!
            pause
            exit /b 1
        )
    ) else (
        echo ERROR: No compiler found! Please install MSVC or MinGW.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Compilation successful!
echo ========================================
echo.
echo Running test...
echo.

REM Запускаем тест
Test_QMessageBox_Standalone.exe

echo.
echo Test completed.
pause
