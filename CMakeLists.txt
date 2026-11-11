cmake_minimum_required(VERSION 3.23)

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
if (POLICY CMP0091)
  cmake_policy(SET CMP0091 NEW)
endif()

project(Nmsdk LANGUAGES C CXX)
include("${CMAKE_SOURCE_DIR}/cmake/NmsdkCompiler.cmake")

# Select a single Qt provider before discovering any Qt components.
set(NMSDK_QT_PROVIDER "local" CACHE STRING "Qt provider: local or vcpkg")
set_property(CACHE NMSDK_QT_PROVIDER PROPERTY STRINGS local vcpkg)
if(DEFINED NMSDK_FORCE_QT_FROM_VCPKG)
  if(NMSDK_FORCE_QT_FROM_VCPKG)
    set(NMSDK_QT_PROVIDER vcpkg)
  else()
    set(NMSDK_QT_PROVIDER local)
  endif()
endif()
if(NOT NMSDK_QT_PROVIDER MATCHES "^(local|vcpkg)$")
  message(FATAL_ERROR "NMSDK_QT_PROVIDER must be local or vcpkg")
endif()

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
  add_compile_options(/utf-8 /bigobj)
  if(CMAKE_GENERATOR MATCHES "Visual Studio")
    set(NMSDK_MSBUILD_COMPILE_JOBS 2 CACHE STRING "Compiler processes per MSBuild project")
    add_compile_options(/MP${NMSDK_MSBUILD_COMPILE_JOBS})
  endif()
  # VS2019 + C++20: make u8 literals compatible with third-party code
  # expecting const char* (for example llama.cpp b4533).
  if(MSVC_VERSION LESS 1930)
    add_compile_options(/Zc:char8_t-)
  endif()
endif()

# Unified Qt5/Qt6 selection and creation of Nmsdk::Qt::* aliases
include("${CMAKE_SOURCE_DIR}/cmake/SelectQt.cmake")

# Every configure preset and configuration owns its runtime and libraries.
# This prevents a Release build overwriting Debug DLLs and Qt5 mixing with Qt6.
set(NMSDK_DEPLOY_ROOT "${CMAKE_BINARY_DIR}/runtime" CACHE PATH "Runtime output root")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${NMSDK_DEPLOY_ROOT}/$<CONFIG>")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib/$<CONFIG>")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib/$<CONFIG>")
set(NMSDK_RESOURCE_ROOT "${CMAKE_SOURCE_DIR}/Bin" CACHE PATH "Nmsdk resource root")

# One switch for both root and Rdk tests; accept the historical spelling.
if(DEFINED BUILD_TESTS)
  if(DEFINED BUILD_TESTING)
    if((BUILD_TESTS AND NOT BUILD_TESTING) OR (BUILD_TESTING AND NOT BUILD_TESTS))
      message(FATAL_ERROR "Use BUILD_TESTING; BUILD_TESTS conflicts with it")
    endif()
  endif()
  set(BUILD_TESTING "${BUILD_TESTS}" CACHE BOOL "Build tests" FORCE)
  unset(BUILD_TESTS CACHE)
endif()
include(CTest)
if(BUILD_TESTING)
  # Install the manifest's tests feature, or the distribution's libgtest-dev.
  # Resolve once in the root so all child projects share imported targets.
  find_package(GTest REQUIRED)
  set(CMAKE_GTEST_DISCOVER_TESTS_DISCOVERY_MODE PRE_TEST)
endif()

# CMake 4.x: keep FindBoost MODULE mode for system/vcpkg packages
if(POLICY CMP0167)
  cmake_policy(SET CMP0167 OLD)
endif()

# Common definitions and dependencies (OpenCV/Boost/etc.)
include(RdkDefines)

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
# Default startup/run target for IDEs (VS / CMake Tools when supported)
if(TARGET NeuroModeler)
  set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT NeuroModeler)
endif()

# Tests (optional, can be disabled for production builds)
if(BUILD_TESTING)
    add_subdirectory(Tests)
endif()


