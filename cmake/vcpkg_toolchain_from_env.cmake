# Toolchain wrapper for vcpkg + Ninja discovery (Windows)
#
# Goals:
# - Avoid Qt Creator auto-generated vcpkg toolchain wrapper (`build/*/vcpkg-dependencies/toolchain.cmake`)
#   which may embed preset-only syntax like `${env:VCPKG_ROOT}` (invalid in CMake language).
# - Make win-msvc-debug/release presets portable: resolve VCPKG_ROOT from environment at configure time.
# - Provide a stable way to locate ninja.exe inside vcpkg downloads (no hardcoded version in presets).
# - Keep using in-repo overlay ports (boost-build fix for vc144 -> vc140).

cmake_minimum_required(VERSION 3.15)

# Resolve repository root from this file location: <repo>/cmake/vcpkg_toolchain_from_env.cmake
get_filename_component(_NMSDK_REPO_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)

# Ensure VCPKG_ROOT is present
if(NOT DEFINED ENV{VCPKG_ROOT} OR "$ENV{VCPKG_ROOT}" STREQUAL "")
  message(FATAL_ERROR "VCPKG_ROOT env var is not set. Please set VCPKG_ROOT to your vcpkg folder (e.g. E:/vcpkg).")
endif()
file(TO_CMAKE_PATH "$ENV{VCPKG_ROOT}" _VCPKG_ROOT)

# Ранее здесь по умолчанию добавлялись overlay-порты (vcpkg-overlay-ports),
# в т.ч. наш кастомный boost-modular-build-helper. Сейчас мы хотим проверить
# «чистый» vcpkg без оверлеев, поэтому не трогаем VCPKG_OVERLAY_PORTS вообще.
# Если потребуется вернуть оверлеи, это можно будет сделать либо через
# CMakePresets (cacheVariable VCPKG_OVERLAY_PORTS), либо через переменную среды.

# If generator is Ninja, ensure CMAKE_MAKE_PROGRAM points to a real ninja.exe.
# Qt Creator sometimes doesn't provide a valid path and CMake errors out early.
if(CMAKE_GENERATOR MATCHES "^Ninja")
  if(NOT DEFINED CMAKE_MAKE_PROGRAM OR "${CMAKE_MAKE_PROGRAM}" STREQUAL "")
    file(GLOB _NINJA_CANDIDATES
      LIST_DIRECTORIES false
      "${_VCPKG_ROOT}/downloads/tools/ninja-*-windows/ninja.exe"
      "${_VCPKG_ROOT}/downloads/tools/ninja/*/ninja.exe"
    )
    list(LENGTH _NINJA_CANDIDATES _NINJA_COUNT)
    if(_NINJA_COUNT EQUAL 0)
      message(FATAL_ERROR "Could not locate ninja.exe under ${_VCPKG_ROOT}/downloads/tools. Run vcpkg once or install Ninja.")
    endif()
    # Just pick the first candidate; in practice there is usually only one.
    list(GET _NINJA_CANDIDATES 0 _NINJA_EXE)
    if(NOT EXISTS "${_NINJA_EXE}")
      message(FATAL_ERROR "Could not locate ninja.exe under ${_VCPKG_ROOT}/downloads/tools. Run vcpkg once or install Ninja.")
    endif()
    set(CMAKE_MAKE_PROGRAM "${_NINJA_EXE}" CACHE FILEPATH "Ninja executable" FORCE)
  endif()
endif()

# Chainload vcpkg toolchain
include("${_VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake")

