@echo off
setlocal

REM Очистка vcpkg артефактов в build/* для пресетов win-msvc-debug/release (Qt Creator + manifests)
REM Запускать из корня репозитория.

set "ROOT=%~dp0"
REM убрать trailing backslash
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

echo ========================================
echo Cleaning vcpkg artifacts under build/ ...
echo ROOT = %ROOT%
echo ========================================

for %%D in (win-msvc-debug win-msvc-release) do (
  if exist "%ROOT%\build\%%D\vcpkg_installed" (
    echo Removing build\%%D\vcpkg_installed ...
    rmdir /s /q "%ROOT%\build\%%D\vcpkg_installed"
  )
  if exist "%ROOT%\build\%%D\vcpkg-dependencies" (
    echo Removing build\%%D\vcpkg-dependencies ...
    rmdir /s /q "%ROOT%\build\%%D\vcpkg-dependencies"
  )
  if exist "%ROOT%\build\%%D\.qtc\package-manager" (
    echo Removing build\%%D\.qtc\package-manager ...
    rmdir /s /q "%ROOT%\build\%%D\.qtc\package-manager"
  )
)

echo Done.
echo ========================================

endlocal

