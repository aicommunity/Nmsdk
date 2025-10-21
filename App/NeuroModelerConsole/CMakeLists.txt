# NeuroModelerConsole Application CMake Configuration
cmake_minimum_required(VERSION 3.16)

# C++20 configuration
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find required packages
find_package(Qt5 REQUIRED COMPONENTS Core)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Engine
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Application
    ${CMAKE_SOURCE_DIR}/Rdk/Core/System
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Math
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Utilities
    ${CMAKE_SOURCE_DIR}/Libraries
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-HardwareLib/Core
)

# Source files
set(SOURCES
    main.cpp
)

# Create executable
add_executable(NeuroModelerConsole ${SOURCES})

# Modern compiler flags for GNU
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(NeuroModelerConsole PRIVATE
        -Wall -Wextra -Wpedantic
        -O3 -march=native -mtune=native
        -flto -fuse-linker-plugin
        -fno-exceptions -fno-rtti
    )
endif()

# Precompiled headers
target_precompile_headers(NeuroModelerConsole PRIVATE
    <memory>
    <string>
    <vector>
    <QCoreApplication>
)

# Link libraries
target_link_libraries(NeuroModelerConsole
    Qt5::Core
    rdk.static.qt
    Rdk-BasicLib.qt
    Nmsdk-PulseLib.qt
    Nmsdk-MotionControlLib.qt
    Rdk-CvBasicLib.qt
    Rdk-HardwareLib.qt
    Threads::Threads
)

# Set output directory
set_target_properties(NeuroModelerConsole PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)