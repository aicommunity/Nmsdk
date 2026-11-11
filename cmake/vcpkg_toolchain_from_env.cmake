# Keep installed dependencies outside disposable application build trees.
# The binary cache remains managed by vcpkg (LOCALAPPDATA/vcpkg/archives by default).
# CMake Tools may replace VCPKG_ROOT with Visual Studio's bundled vcpkg when
# importing vcvarsall. Respect an explicit cache override, otherwise recover the
# persistent Windows user/machine setting only for that bundled-root case.
set(NMSDK_VCPKG_ROOT "" CACHE PATH "Optional explicit vcpkg checkout (overrides VCPKG_ROOT)")
if(NMSDK_VCPKG_ROOT)
  set(ENV{VCPKG_ROOT} "${NMSDK_VCPKG_ROOT}")
elseif(CMAKE_HOST_WIN32)
  file(TO_CMAKE_PATH "$ENV{VCPKG_ROOT}" _nmsdk_inherited_vcpkg)
  string(TOLOWER "${_nmsdk_inherited_vcpkg}" _nmsdk_inherited_vcpkg_lower)
  set(_nmsdk_vs_bundled_root "")
  if(DEFINED ENV{VSINSTALLDIR} AND NOT "$ENV{VSINSTALLDIR}" STREQUAL "")
    get_filename_component(_nmsdk_vs_bundled_root "$ENV{VSINSTALLDIR}/VC/vcpkg" ABSOLUTE)
    string(TOLOWER "${_nmsdk_vs_bundled_root}" _nmsdk_vs_bundled_root)
  endif()
  if(_nmsdk_inherited_vcpkg_lower STREQUAL _nmsdk_vs_bundled_root OR
     _nmsdk_inherited_vcpkg_lower MATCHES "/microsoft visual studio/[^/]+/[^/]+/vc/vcpkg/?$")
    execute_process(
      COMMAND powershell.exe -NoProfile -NonInteractive -Command
        "[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false); $p=[Environment]::GetEnvironmentVariable('VCPKG_ROOT','User'); if(!$p){$p=[Environment]::GetEnvironmentVariable('VCPKG_ROOT','Machine')}; if($p){[Console]::Write($p)}"
      ENCODING UTF8
      RESULT_VARIABLE _nmsdk_root_query_result
      OUTPUT_VARIABLE _nmsdk_persistent_vcpkg
      OUTPUT_STRIP_TRAILING_WHITESPACE)
    if(_nmsdk_root_query_result EQUAL 0 AND NOT _nmsdk_persistent_vcpkg STREQUAL "")
      file(TO_CMAKE_PATH "${_nmsdk_persistent_vcpkg}" _nmsdk_persistent_vcpkg)
      if(NOT EXISTS "${_nmsdk_persistent_vcpkg}/scripts/buildsystems/vcpkg.cmake")
        message(FATAL_ERROR "Persistent VCPKG_ROOT is invalid: ${_nmsdk_persistent_vcpkg}. Fix it or set NMSDK_VCPKG_ROOT explicitly.")
      endif()
      if(NOT _nmsdk_persistent_vcpkg STREQUAL _nmsdk_inherited_vcpkg)
        message(STATUS "Nmsdk: using persistent VCPKG_ROOT=${_nmsdk_persistent_vcpkg} instead of Visual Studio's bundled vcpkg")
        set(ENV{VCPKG_ROOT} "${_nmsdk_persistent_vcpkg}")
      endif()
    endif()
  endif()
endif()
if(NOT DEFINED ENV{VCPKG_ROOT} OR "$ENV{VCPKG_ROOT}" STREQUAL "")
  message(FATAL_ERROR "Set VCPKG_ROOT to a bootstrapped vcpkg checkout.")
endif()
file(TO_CMAKE_PATH "$ENV{VCPKG_ROOT}" _nmsdk_vcpkg_root)
if(NOT EXISTS "${_nmsdk_vcpkg_root}/scripts/buildsystems/vcpkg.cmake")
  message(FATAL_ERROR "VCPKG_ROOT does not contain scripts/buildsystems/vcpkg.cmake")
endif()
# x64-windows otherwise selects the newest VS instance independently of the
# application. Keep v143 dependencies on VS2022 when VS2026 is also installed.
if(CMAKE_HOST_WIN32 AND NMSDK_EXPECTED_TOOLSET STREQUAL "v143")
  set(_nmsdk_vswhere "$ENV{ProgramFiles\(x86\)}/Microsoft Visual Studio/Installer/vswhere.exe")
  if(NOT EXISTS "${_nmsdk_vswhere}")
    message(FATAL_ERROR "VS2022 discovery requires the Visual Studio Installer (vswhere).")
  endif()
  execute_process(COMMAND "${_nmsdk_vswhere}" -latest -products * -version "[17.0,18.0)"
    -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    OUTPUT_VARIABLE _nmsdk_vs2022 OUTPUT_STRIP_TRAILING_WHITESPACE RESULT_VARIABLE _nmsdk_vs_result)
  if(NOT _nmsdk_vs_result EQUAL 0 OR NOT IS_DIRECTORY "${_nmsdk_vs2022}")
    message(FATAL_ERROR "v143 presets require VS2022 with Desktop development with C++ installed.")
  endif()
  set(ENV{VCPKG_VISUAL_STUDIO_PATH} "${_nmsdk_vs2022}")
endif()
get_filename_component(_nmsdk_root "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
set(NMSDK_DEPS_ROOT "${_nmsdk_root}/.deps" CACHE PATH "Persistent dependency store; do not clean with application builds")
set(NMSDK_DEPENDENCY_PROFILE "default" CACHE STRING "Isolated dependency feature/toolset profile")
if(NOT DEFINED VCPKG_INSTALLED_DIR)
  set(VCPKG_INSTALLED_DIR "${NMSDK_DEPS_ROOT}/vcpkg/${NMSDK_DEPENDENCY_PROFILE}" CACHE PATH "Persistent vcpkg manifest installation")
endif()
# A caller may select another pinned manifest (v142 uses Qt 6.5.3).
if(NOT DEFINED VCPKG_MANIFEST_DIR)
  set(VCPKG_MANIFEST_DIR "${_nmsdk_root}" CACHE PATH "vcpkg manifest directory")
endif()
include("${_nmsdk_vcpkg_root}/scripts/buildsystems/vcpkg.cmake")
