cmake_minimum_required(VERSION 3.16)

# Qt Creator: skip package-manager auto-setup on every project() (googletest, etc.).
# Windows vcpkg: use CMAKE_TOOLCHAIN_FILE from presets, not Qt Creator wrapper.
if(NOT QT_CREATOR_SKIP_PACKAGE_MANAGER_SETUP)
  set(QT_CREATOR_SKIP_PACKAGE_MANAGER_SETUP ON CACHE BOOL
    "Skip Qt Creator package manager auto-setup" FORCE)
endif()

# Normalize vcpkg toolchain file path (Windows only)
# This must be BEFORE project(), because CMAKE_TOOLCHAIN_FILE is used during project initialization
if(EXISTS "${CMAKE_SOURCE_DIR}/cmake/NormalizeVcpkgPath.cmake")
    include("${CMAKE_SOURCE_DIR}/cmake/NormalizeVcpkgPath.cmake")
endif()

# Enable CMAKE_MSVC_RUNTIME_LIBRARY (CMP0091) to control /MDd|/MD
if (MSVC AND POLICY CMP0091)
  cmake_policy(SET CMP0091 NEW)
endif()

project(Nmsdk LANGUAGES CXX)

# Qt source switch on Windows:
# - ON  (default on Windows): force using Qt from vcpkg (filtering local Qt installations out of CMAKE_PREFIX_PATH)
# - OFF: use local Qt (for example, C:\Qt\5.15.2\msvc2019_64), while still using vcpkg for other dependencies
if(WIN32)
  set(_NMSDK_FORCE_QT_FROM_VCPKG_DEFAULT ON)
else()
  set(_NMSDK_FORCE_QT_FROM_VCPKG_DEFAULT OFF)
endif()
option(NMSDK_FORCE_QT_FROM_VCPKG "Force Qt from vcpkg on Windows (filter local Qt from CMAKE_PREFIX_PATH)" ${_NMSDK_FORCE_QT_FROM_VCPKG_DEFAULT})

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
include(NmsdkParallelBuild)

# Policies and standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Common settings for MSVC runtime (DLL) — consistent for all targets
if (MSVC)
  set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<IF:$<CONFIG:Debug>,Debug,>DLL" CACHE STRING "" FORCE)
  # VS2019 + C++20: make u8 literals compatible with third-party code
  # expecting const char* (for example llama.cpp b4533).
  if(MSVC_VERSION LESS 1930)
    add_compile_options(/Zc:char8_t-)
  endif()
endif()

# Force Qt to be taken only from vcpkg on Windows
# (on Linux this module is a no-op)
if(NMSDK_FORCE_QT_FROM_VCPKG AND EXISTS "${CMAKE_SOURCE_DIR}/cmake/ForceQtFromVcpkg.cmake")
  include("${CMAKE_SOURCE_DIR}/cmake/ForceQtFromVcpkg.cmake")
endif()

# Unified Qt5/Qt6 selection and creation of Nmsdk::Qt::* aliases
include("${CMAKE_SOURCE_DIR}/cmake/SelectQt.cmake")

# Place binaries and libraries into Bin/Platform/<OS>
if (WIN32)
  set(PLATFORM_DIR "Win")
else()
  set(PLATFORM_DIR "Linux")
endif()

set(DEPLOY_ROOT "${CMAKE_SOURCE_DIR}/Bin/Platform/${PLATFORM_DIR}")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${DEPLOY_ROOT}/Lib.CMake")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${DEPLOY_ROOT}/Lib.CMake")

# For multi-config generators (Visual Studio) remove configuration subfolders
# Use the same output paths for all configurations
foreach(OUTPUTCONFIG DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
  string(TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} "${DEPLOY_ROOT}")
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG} "${DEPLOY_ROOT}/Lib.CMake")
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG} "${DEPLOY_ROOT}/Lib.CMake")
endforeach()

# Common definitions and dependencies (OpenCV/Boost/etc.)
include(RdkDefines OPTIONAL)

# Subprojects (gradual migration)
add_subdirectory(Rdk) # rdk.static
add_subdirectory(Libraries/Rdk-BasicLib) # Rdk-BasicLib
add_subdirectory(Libraries/Rdk-CvBasicLib) # Rdk-CvBasicLib
add_subdirectory(Libraries/Rdk-HardwareLib) # Rdk-HardwareLib
add_subdirectory(Libraries/Nmsdk-MotionControlLib) # Nmsdk-MotionControlLib
add_subdirectory(Libraries/Nmsdk-PulseLib) # Nmsdk-PulseLib
# add_subdirectory(Libraries/Rdk-CvBasicLib)
# add_subdirectory(Libraries/Rdk-HardwareLib)
# add_subdirectory(Libraries/Nmsdk-MotionControlLib)
# add_subdirectory(Libraries/Nmsdk-PulseLib)

# Applications
add_subdirectory(App/NeuroModeler)
add_subdirectory(App/NeuroModelerConsole)

# Tests (optional, can be disabled for production builds)
option(BUILD_TESTS "Build tests" ON)
if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(Tests)
endif()


