# End-to-End Integration Tests CMake Configuration
cmake_minimum_required(VERSION 3.16)

# Find Google Test
find_package(GTest REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Core)

# Create test executable for End-to-End tests
add_executable(EndToEndTests
    TestFullWorkflow.cpp
    TestMultipleConfigs.cpp
    TestLIFNeuronFullWorkflow.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries_con.cpp
)

target_include_directories(EndToEndTests PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Application
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Tests
    ${CMAKE_SOURCE_DIR}/Libraries
)

target_link_libraries(EndToEndTests PRIVATE
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

target_compile_features(EndToEndTests PRIVATE cxx_std_20)
target_compile_definitions(EndToEndTests PRIVATE RDK_QT RDK_LIB_CVS_REVISION=0 CMAKE_SOURCE_DIR="${CMAKE_SOURCE_DIR}")

# Register tests
add_test(NAME EndToEndTests COMMAND EndToEndTests)

