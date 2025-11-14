# Tests Infrastructure CMake Configuration
cmake_minimum_required(VERSION 3.16)

# Enable testing
enable_testing()

# Find Google Test
find_package(GTest REQUIRED)

# Include test helpers
include_directories(${CMAKE_SOURCE_DIR}/Tests)

# Define CMAKE_SOURCE_DIR for tests
add_definitions(-DCMAKE_SOURCE_DIR="${CMAKE_SOURCE_DIR}")

# Add submodule tests
# Rdk tests
if(EXISTS ${CMAKE_SOURCE_DIR}/Rdk/Tests/CMakeLists.txt)
    add_subdirectory(${CMAKE_SOURCE_DIR}/Rdk/Tests Rdk/Tests)
endif()

# Library tests
if(EXISTS ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Tests/CMakeLists.txt)
    add_subdirectory(${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Tests Libraries/Rdk-BasicLib/Tests)
endif()

if(EXISTS ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Tests/CMakeLists.txt)
    add_subdirectory(${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Tests Libraries/Nmsdk-PulseLib/Tests)
endif()

if(EXISTS ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Tests/CMakeLists.txt)
    add_subdirectory(${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Tests Libraries/Nmsdk-MotionControlLib/Tests)
endif()

if(EXISTS ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Tests/CMakeLists.txt)
    add_subdirectory(${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Tests Libraries/Rdk-CvBasicLib/Tests)
endif()

if(EXISTS ${CMAKE_SOURCE_DIR}/Libraries/Rdk-HardwareLib/Tests/CMakeLists.txt)
    add_subdirectory(${CMAKE_SOURCE_DIR}/Libraries/Rdk-HardwareLib/Tests Libraries/Rdk-HardwareLib/Tests)
endif()

# Integration tests for application (in root Tests/)
add_subdirectory(integration)

# Test helpers library
add_library(TestHelpers STATIC
    TestHelpers.cpp
)

target_include_directories(TestHelpers PUBLIC
    ${CMAKE_SOURCE_DIR}/Tests
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Engine
    ${CMAKE_SOURCE_DIR}/Rdk/Core/System
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries
)

target_link_libraries(TestHelpers PUBLIC
    GTest::gtest
    glog::glog
    rdk.static.qt
    Rdk-HardwareLib.qt
)

target_compile_features(TestHelpers PUBLIC cxx_std_20)
target_compile_definitions(TestHelpers PUBLIC RDK_QT RDK_LIB_CVS_REVISION=0)

