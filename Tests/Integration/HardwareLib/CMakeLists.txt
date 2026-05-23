cmake_minimum_required(VERSION 3.16)

add_executable(Test_ArduinoHardwareIntegration Test_ArduinoHardwareIntegration.cpp)

target_sources(Test_ArduinoHardwareIntegration PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include/RdkDummyLibraries.cpp
)

target_compile_definitions(Test_ArduinoHardwareIntegration PRIVATE RDK_LIB_TYPE= RDK_CALL=)

target_link_libraries(Test_ArduinoHardwareIntegration PRIVATE
    Rdk-HardwareLib.qt
    rdk.static.qt
    GTest::gtest
    GTest::gtest_main
    Nmsdk::Qt::Core
    Nmsdk::Qt::SerialPort
)

include(GoogleTest)
gtest_discover_tests(
    Test_ArduinoHardwareIntegration
    PROPERTIES
        LABELS "hardware;arduino;integration"
        TIMEOUT 300
)
