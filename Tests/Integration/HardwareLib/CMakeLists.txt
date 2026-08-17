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
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)

add_executable(Test_ArduinoFirmataExtendedProtocols Test_ArduinoFirmataExtendedProtocols.cpp)

target_sources(Test_ArduinoFirmataExtendedProtocols PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include/RdkDummyLibraries.cpp
)

target_compile_definitions(Test_ArduinoFirmataExtendedProtocols PRIVATE RDK_LIB_TYPE= RDK_CALL=)

target_link_libraries(Test_ArduinoFirmataExtendedProtocols PRIVATE
    Rdk-HardwareLib.qt
    rdk.static.qt
    GTest::gtest
    GTest::gtest_main
    Nmsdk::Qt::Core
    Nmsdk::Qt::SerialPort
)

gtest_discover_tests(
    Test_ArduinoFirmataExtendedProtocols
    PROPERTIES
        LABELS "hardware;arduino;firmata;integration"
        TIMEOUT 180
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)

add_executable(Test_ArduinoHubLive Test_ArduinoHubLive.cpp)

target_sources(Test_ArduinoHubLive PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include/RdkDummyLibraries.cpp
)

target_compile_definitions(Test_ArduinoHubLive PRIVATE RDK_LIB_TYPE= RDK_CALL=)

target_link_libraries(Test_ArduinoHubLive PRIVATE
    Rdk-HardwareLib.qt
    rdk.static.qt
    GTest::gtest
    GTest::gtest_main
    Nmsdk::Qt::Core
    Nmsdk::Qt::SerialPort
)

gtest_discover_tests(
    Test_ArduinoHubLive
    PROPERTIES
        LABELS "hardware;arduino;hub;integration"
        TIMEOUT 420
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)
