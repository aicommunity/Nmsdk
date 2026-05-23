@echo off
rem Copy non-Qt runtime DLLs from vcpkg_installed to Bin\Platform\Win.
rem Run from repo root, or set VCPKG_BIN_DIR and BIN_PLATFORM_WIN.
setlocal
set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
if defined VCPKG_BIN_DIR (set "VCPKG_BIN=%VCPKG_BIN_DIR%") else (set "VCPKG_BIN=%REPO_ROOT%\build\vcpkg_installed\x64-windows\bin")
if defined BIN_PLATFORM_WIN (set "DEST=%BIN_PLATFORM_WIN%") else (set "DEST=%REPO_ROOT%\Bin\Platform\Win")
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%copy_runtime_deps_to_bin.ps1" -RepoRoot "%REPO_ROOT%" -VcpkgBinDir "%VCPKG_BIN%" -DestDir "%DEST%"
endlocal
