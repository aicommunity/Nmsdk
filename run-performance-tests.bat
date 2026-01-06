@echo off
REM Скрипт для запуска тестов производительности GetData()
REM Использование: запустить из Visual Studio Developer Command Prompt

setlocal enabledelayedexpansion

echo ========================================
echo Запуск тестов производительности GetData()
echo ========================================
echo.

REM Поиск исполняемого файла теста
set TEST_EXE=
if exist "build\win-vs2022-release\Rdk\Tests\Unit\Engine\UProperty\Release\Test_UProperty_Performance.exe" (
    set TEST_EXE=build\win-vs2022-release\Rdk\Tests\Unit\Engine\UProperty\Release\Test_UProperty_Performance.exe
) else if exist "build\win-vs2022-release\Rdk\Tests\Unit\Engine\UProperty\Debug\Test_UProperty_Performance.exe" (
    set TEST_EXE=build\win-vs2022-release\Rdk\Tests\Unit\Engine\UProperty\Debug\Test_UProperty_Performance.exe
) else if exist "build\win-vs2022-debug\Rdk\Tests\Unit\Engine\UProperty\Debug\Test_UProperty_Performance.exe" (
    set TEST_EXE=build\win-vs2022-debug\Rdk\Tests\Unit\Engine\UProperty\Debug\Test_UProperty_Performance.exe
) else (
    echo Поиск теста в других местах...
    for /r "build" %%f in (Test_UProperty_Performance.exe) do (
        set TEST_EXE=%%f
        goto :found
    )
    :found
)

if "%TEST_EXE%"=="" (
    echo ERROR: Исполняемый файл теста не найден!
    echo Пожалуйста, сначала соберите проект с тестами:
    echo   build-windows.bat release
    echo   cmake --build build\win-vs2022-release --target Test_UProperty_Performance --config Release
    goto :end
)

echo Найден тест: %TEST_EXE%
echo.

REM Создаем директорию для отчетов
if not exist "Reports\Performance" mkdir "Reports\Performance"

REM Запускаем тесты и сохраняем вывод
set REPORT_FILE=Reports\Performance\GetData_Performance_Report_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt
set REPORT_FILE=%REPORT_FILE: =0%

echo Запуск тестов производительности...
echo Результаты будут сохранены в: %REPORT_FILE%
echo.

"%TEST_EXE%" --gtest_filter=PerformanceTest.* > "%REPORT_FILE%" 2>&1

if errorlevel 1 (
    echo.
    echo WARNING: Некоторые тесты завершились с ошибками. Проверьте отчет.
) else (
    echo.
    echo Все тесты прошли успешно!
)

echo.
echo ========================================
echo Результаты сохранены в: %REPORT_FILE%
echo ========================================
echo.

REM Показываем краткую сводку
echo Краткая сводка результатов:
echo ----------------------------------------
type "%REPORT_FILE%" | findstr /C:"Average" /C:"Improvement" /C:"ns" /C:"PASSED" /C:"FAILED"
echo.

:end
endlocal

