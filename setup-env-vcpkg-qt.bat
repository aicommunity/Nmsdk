@echo off
REM Первичная настройка окружения: vcpkg + Qt5 (msvc) + переменные
REM Запускать из корня репозитория. Требуются: git, cmake, powershell.

setlocal enabledelayedexpansion

REM Переключаем консоль в UTF-8 для читаемых сообщений
for /f "tokens=2 delims=:." %%i in ('chcp') do set "_OLDCP=%%i"
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "VCPKG_ROOT=%VCPKG_ROOT%"
if "%VCPKG_ROOT%"=="" set "VCPKG_ROOT=%SCRIPT_DIR%vcpkg"

echo ========================================
echo Подготовка окружения (vcpkg + Qt5)
echo VCPKG_ROOT = %VCPKG_ROOT%
echo ========================================

REM Проверка git
git --version >nul 2>&1
if errorlevel 1 (
  echo ERROR: git не найден. Установите git и повторите.
  goto :cleanup
)

REM Проверка cmake, при отсутствии пробуем активировать VS DevCmd
cmake --version >nul 2>&1
if errorlevel 1 (
  echo INFO: CMake не найден в PATH. Попробуем активировать среду VS...
  call :try_vs_devcmd
  cmake --version >nul 2>&1
  if errorlevel 1 (
    echo ERROR: CMake не найден. Добавьте CMake в PATH или запустите из Developer Command Prompt.
    goto :cleanup
  )
)

REM Клонирование vcpkg при отсутствии
if not exist "%VCPKG_ROOT%\." (
  echo Клонируем vcpkg в %VCPKG_ROOT% ...
  git clone https://github.com/microsoft/vcpkg.git "%VCPKG_ROOT%"
  if errorlevel 1 (
    echo ERROR: Не удалось клонировать vcpkg.
    exit /b 1
  )
)

REM Bootstrap
pushd "%VCPKG_ROOT%"
if not exist ".\vcpkg.exe" (
  echo Bootstrap vcpkg...
  .\bootstrap-vcpkg.bat
  if errorlevel 1 (
    echo ERROR: bootstrap-vcpkg завершился с ошибкой.
    popd
    exit /b 1
  )
)

REM Интеграция с VS (необязательно, но удобно)
echo Интеграция vcpkg с Visual Studio...
.\vcpkg.exe integrate install

REM Установка зависимостей по манифесту (включая Qt5) для x64-windows
echo Установка зависимостей по манифесту (triplet x64-windows)...
.\vcpkg.exe install --triplet x64-windows
if errorlevel 1 (
  echo WARNING: Установка зависимостей вернула ошибку. Проверьте лог.
)

popd

REM Прописать VCPKG_ROOT в системное окружение (требует права администратора)
echo Настройка переменной окружения VCPKG_ROOT ...
setx VCPKG_ROOT "%VCPKG_ROOT%" /M

echo ========================================
echo Готово. Перезапустите консоль/VS, чтобы переменные окружения обновились.
echo Для сборки используйте пресеты win-vs2022-{debug|release} или build-windows.bat.
echo ========================================

:cleanup
if defined _OLDCP chcp %_OLDCP% >nul
endlocal

:eof

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
