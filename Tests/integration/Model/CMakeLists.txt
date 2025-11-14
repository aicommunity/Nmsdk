# Model Integration Tests CMake Configuration
cmake_minimum_required(VERSION 3.16)

# Find Google Test
find_package(GTest REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Core)

# Create test executable for Model tests
add_executable(ModelTests
    TestModelLoad.cpp
    TestModelComponents.cpp
    TestModelConnections.cpp
    TestModelExecution.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries_con.cpp
)

target_include_directories(ModelTests PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Application
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Tests
    ${CMAKE_SOURCE_DIR}/Libraries
)

target_link_libraries(ModelTests PRIVATE
    rdk.static.qt
    Rdk-BasicLib.qt
    Nmsdk-PulseLib.qt
    Nmsdk-MotionControlLib.qt
    Rdk-CvBasicLib.qt
    Rdk-HardwareLib.qt
    TestHelpers
    GTest::gtest
    GTest::gtest_main
    glog::glog
    Threads::Threads
    Qt5::Core
)

target_compile_features(ModelTests PRIVATE cxx_std_20)
target_compile_definitions(ModelTests PRIVATE RDK_QT RDK_LIB_CVS_REVISION=0 CMAKE_SOURCE_DIR="${CMAKE_SOURCE_DIR}")

# Register tests
add_test(NAME ModelTests COMMAND ModelTests)

