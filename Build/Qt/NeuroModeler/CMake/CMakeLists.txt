# NeuroModeler Application CMake Configuration
cmake_minimum_required(VERSION 3.16)

# C++20 configuration
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Define macros to disable external GUI components
add_definitions(-DRDK_DISABLE_EXT_GUI)

# Define Boost macros to suppress warnings
add_definitions(-DBOOST_BIND_GLOBAL_PLACEHOLDERS)

# Define application macros
add_definitions(-DRDK_APP_URL="https://github.com/neuro-modeler/nmsdk")
add_definitions(-DRDK_APP_LICENSE="MIT License")
add_definitions(-DRDK_APP_VERSION="1.0.0")

# Find required packages
find_package(Qt5 REQUIRED COMPONENTS Core Widgets Network Charts)
find_package(PkgConfig REQUIRED)
pkg_check_modules(CURL REQUIRED libcurl)
find_package(Boost REQUIRED COMPONENTS thread filesystem system)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Engine
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Application
    ${CMAKE_SOURCE_DIR}/Rdk/Core/System
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Math
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Utilities
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Graphics
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt
    ${CMAKE_SOURCE_DIR}/Libraries
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-HardwareLib/Core
)

# Source files
set(SOURCES
    ../main.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries_con.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
)

# Add all Qt GUI files
file(GLOB_RECURSE QT_GUI_SOURCES "${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/*.cpp")
list(APPEND SOURCES ${QT_GUI_SOURCES})

# Create executable
add_executable(NeuroModeler ${SOURCES})

# Modern compiler flags for GNU
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(NeuroModeler PRIVATE
        -Wall -Wextra -Wpedantic
        -O3 -march=native -mtune=native
        -flto -fuse-linker-plugin
        -Wno-unused-function
        -Wno-deprecated-copy
    )
endif()

# Precompiled headers
target_precompile_headers(NeuroModeler PRIVATE
    <memory>
    <string>
    <vector>
    <QApplication>
    <QWidget>
)

# Link libraries
target_link_libraries(NeuroModeler
    Qt5::Core
    Qt5::Widgets
    Qt5::Network
    Qt5::Charts
    rdk.static.qt
    Rdk-BasicLib.qt
    Nmsdk-PulseLib.qt
    Nmsdk-MotionControlLib.qt
    Rdk-CvBasicLib.qt
    Rdk-HardwareLib.qt
    Threads::Threads
    ${CURL_LIBRARIES}
    Boost::thread
    Boost::filesystem
    Boost::system
)

# Set output directory
set_target_properties(NeuroModeler PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)