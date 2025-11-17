# Diagnostic tests for segfault diagnosis
cmake_minimum_required(VERSION 3.16)

# Find Google Test
find_package(GTest REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Core)

add_executable(SegfaultDiagnosisTests
    TestSegfaultDiagnosis.cpp
    TestNEngineMotionControlLifecycle.cpp
    TestComponentDeletion.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries_con.cpp
)

target_link_libraries(SegfaultDiagnosisTests
    PRIVATE
    rdk.static.qt
    Rdk-BasicLib.qt
    Rdk-CvBasicLib.qt
    Rdk-HardwareLib.qt
    Nmsdk-PulseLib.qt
    Nmsdk-MotionControlLib.qt
    TestHelpers
    GTest::gtest
    GTest::gtest_main
    glog::glog
    Threads::Threads
    Qt5::Core
)

target_include_directories(SegfaultDiagnosisTests
    PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/Tests
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-HardwareLib/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Core
)

target_compile_features(SegfaultDiagnosisTests PRIVATE cxx_std_20)
target_compile_definitions(SegfaultDiagnosisTests PRIVATE RDK_QT RDK_LIB_CVS_REVISION=0 CMAKE_SOURCE_DIR="${CMAKE_SOURCE_DIR}")

# Add test
add_test(NAME SegfaultDiagnosisTests COMMAND SegfaultDiagnosisTests)

