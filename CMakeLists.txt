cmake_minimum_required(VERSION 3.16)

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

# Automatic parallel build configuration
# Detect the number of CPU cores if CMAKE_BUILD_PARALLEL_LEVEL is not set
# This setting is automatically propagated to all subprojects via add_subdirectory()
include(ProcessorCount)
ProcessorCount(N)
if(N EQUAL 0)
    set(N 4)  # Fallback: use default value
endif()

# Set environment variable for use during build (for Ninja and other generators)
if(NOT DEFINED ENV{CMAKE_BUILD_PARALLEL_LEVEL})
    set(ENV{CMAKE_BUILD_PARALLEL_LEVEL} ${N})
    message(STATUS "CMAKE_BUILD_PARALLEL_LEVEL set to ${N} (auto-detected CPU cores)")
else()
    message(STATUS "CMAKE_BUILD_PARALLEL_LEVEL already set to $ENV{CMAKE_BUILD_PARALLEL_LEVEL}")
endif()

# For Visual Studio generator configure parallel build via cache variables
if(CMAKE_GENERATOR MATCHES "Visual Studio")
    # Set the number of parallel build threads for Visual Studio
    if(NOT DEFINED CMAKE_VS_PARALLEL_BUILD_THREADS)
        set(CMAKE_VS_PARALLEL_BUILD_THREADS ${N} CACHE STRING "Number of parallel build threads for Visual Studio" FORCE)
        message(STATUS "CMAKE_VS_PARALLEL_BUILD_THREADS set to ${N} (auto-detected CPU cores)")
    endif()
    # Enable parallel project build
    if(NOT DEFINED CMAKE_VS_GENERATE_DEVENV_LAUNCHER)
        set(CMAKE_VS_GENERATE_DEVENV_LAUNCHER ON CACHE BOOL "Generate Visual Studio devenv launcher" FORCE)
    endif()
endif()

# Policies and standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Common settings for MSVC runtime (DLL) — consistent for all targets
if (MSVC)
  set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<IF:$<CONFIG:Debug>,Debug,>DLL" CACHE STRING "" FORCE)
endif()

# Directory with shared CMake modules
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

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


