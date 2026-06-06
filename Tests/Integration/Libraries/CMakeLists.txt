cmake_minimum_required(VERSION 3.16)

message(STATUS "Libraries integration tests directory created")

if(WIN32)
    set(PULSELIB_TEST_OUTPUT_DIR "${CMAKE_SOURCE_DIR}/Bin/Platform/Win")
else()
    set(PULSELIB_TEST_OUTPUT_DIR "${CMAKE_SOURCE_DIR}/Bin/Platform/Linux")
endif()

add_executable(Test_PulseLib_StorageComponents
    Test_PulseLib_StorageComponents.cpp
    Test_PulseLib_NeuronGrowth.cpp
    Test_PulseLib_Main.cpp
)

target_sources(Test_PulseLib_StorageComponents PRIVATE
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
    ${CMAKE_SOURCE_DIR}/Tests/Integration/Support/ConsoleLikeInit.cpp
)

target_link_libraries(Test_PulseLib_StorageComponents
    PRIVATE
        rdk.static.qt
        Rdk-HardwareLib.qt
        Nmsdk-MotionControlLib.qt
        Nmsdk-PulseLib.qt
        gtest
)

target_include_directories(Test_PulseLib_StorageComponents
    PRIVATE
        ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
        ${CMAKE_SOURCE_DIR}/Rdk/Core
        ${CMAKE_SOURCE_DIR}/Libraries
)

set_target_properties(Test_PulseLib_StorageComponents PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY                 "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG           "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE         "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO  "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL      "${PULSELIB_TEST_OUTPUT_DIR}"
)

add_test(NAME PulseLib_StorageComponents COMMAND Test_PulseLib_StorageComponents)

add_executable(PulseLibIntervalTuner
    PulseLibIntervalTuner.cpp
)

target_sources(PulseLibIntervalTuner PRIVATE
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
    ${CMAKE_SOURCE_DIR}/Tests/Integration/Support/ConsoleLikeInit.cpp
)

target_link_libraries(PulseLibIntervalTuner
    PRIVATE
        rdk.static.qt
        Rdk-HardwareLib.qt
        Nmsdk-MotionControlLib.qt
        Nmsdk-PulseLib.qt
)

target_include_directories(PulseLibIntervalTuner
    PRIVATE
        ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
        ${CMAKE_SOURCE_DIR}/Rdk/Core
        ${CMAKE_SOURCE_DIR}/Libraries
)

set_target_properties(PulseLibIntervalTuner PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY                 "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG           "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE         "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO  "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL      "${PULSELIB_TEST_OUTPUT_DIR}"
)


