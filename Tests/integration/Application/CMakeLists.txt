# Application Integration Tests CMake Configuration
cmake_minimum_required(VERSION 3.16)

# Find Google Test
find_package(GTest REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Core)

# Create test executable for Application tests
add_executable(ApplicationTests
    TestNeuroModelerConsole.cpp
    TestApplicationInit.cpp
    TestNeuroModelerConsoleIntegration.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries_con.cpp
)

target_include_directories(ApplicationTests PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Application
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Tests
    ${CMAKE_SOURCE_DIR}/Libraries
    ${CMAKE_SOURCE_DIR}/App/NeuroModelerConsole
)

target_link_libraries(ApplicationTests PRIVATE
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

target_compile_features(ApplicationTests PRIVATE cxx_std_20)
target_compile_definitions(ApplicationTests PRIVATE RDK_QT RDK_LIB_CVS_REVISION=0 CMAKE_SOURCE_DIR="${CMAKE_SOURCE_DIR}" CMAKE_BINARY_DIR="${CMAKE_BINARY_DIR}")

# Register tests
add_test(NAME ApplicationTests COMMAND ApplicationTests)

