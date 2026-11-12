@echo off
setlocal
if not defined VCPKG_ROOT (
  echo Set VCPKG_ROOT to your vcpkg checkout first.
  exit /b 1
)
if not exist "%VCPKG_ROOT%\bootstrap-vcpkg.bat" (
  echo VCPKG_ROOT does not contain bootstrap-vcpkg.bat.
  exit /b 1
)
call "%VCPKG_ROOT%\bootstrap-vcpkg.bat" -disableMetrics
exit /b %errorlevel%
