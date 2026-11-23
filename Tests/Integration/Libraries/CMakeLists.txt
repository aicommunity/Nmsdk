cmake_minimum_required(VERSION 3.16)

message(STATUS "Libraries integration tests directory created")

set(PULSELIB_TEST_OUTPUT_DIR "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}")

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
        GTest::gtest
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

# Historical experiments are controlled externally; production learner/trainer
# implementations are linked unchanged. All replay tooling lives in Scripts.
find_package(nlohmann_json CONFIG REQUIRED)
add_executable(ClassicStructTrainReplay
    ${CMAKE_SOURCE_DIR}/Scripts/ClassicStructTrain/replay.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
    ${CMAKE_SOURCE_DIR}/Tests/Integration/Support/ConsoleLikeInit.cpp
)
target_link_libraries(ClassicStructTrainReplay PRIVATE
    rdk.static.qt Rdk-BasicLib.qt Rdk-CvBasicLib.qt
    Rdk-HardwareLib.qt Nmsdk-MotionControlLib.qt Nmsdk-PulseLib.qt
    Nmsdk::Qt::Core Nmsdk::Qt::Network Nmsdk::Qt::Sql
    Nmsdk::Qt::Xml Nmsdk::Qt::Concurrent nlohmann_json::nlohmann_json
)
target_include_directories(ClassicStructTrainReplay PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include ${CMAKE_SOURCE_DIR}/Libraries
)
if(MSVC)
    target_compile_options(ClassicStructTrainReplay PRIVATE /utf-8)
endif()
include(${CMAKE_SOURCE_DIR}/cmake/DeployVcpkgDlls.cmake)
deploy_vcpkg_dlls(ClassicStructTrainReplay)

# A separate Release executable allows read-only saved-project/context audits
# without replacing the controller while a long inference matrix is running.
add_executable(ClassicSavedStateCheck
    ${CMAKE_SOURCE_DIR}/Scripts/ClassicStructTrain/replay.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
    ${CMAKE_SOURCE_DIR}/Tests/Integration/Support/ConsoleLikeInit.cpp
)
target_link_libraries(ClassicSavedStateCheck PRIVATE
    rdk.static.qt Rdk-BasicLib.qt Rdk-CvBasicLib.qt
    Rdk-HardwareLib.qt Nmsdk-MotionControlLib.qt Nmsdk-PulseLib.qt
    Nmsdk::Qt::Core Nmsdk::Qt::Network Nmsdk::Qt::Sql
    Nmsdk::Qt::Xml Nmsdk::Qt::Concurrent nlohmann_json::nlohmann_json
)
target_include_directories(ClassicSavedStateCheck PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include ${CMAKE_SOURCE_DIR}/Libraries
)
if(MSVC)
    target_compile_options(ClassicSavedStateCheck PRIVATE /utf-8)
endif()
deploy_vcpkg_dlls(ClassicSavedStateCheck)

# Opt-in canonical runtime location for the historical experiment workflow.
# The shared folder is used only by Release, never by a Debug configuration.
set(NMSDK_CLASSIC_RUNTIME_DIR "" CACHE PATH "Classic experiment Release runtime directory")
if(NMSDK_CLASSIC_RUNTIME_DIR)
    if(NOT CMAKE_BUILD_TYPE STREQUAL "Release")
        message(FATAL_ERROR "NMSDK_CLASSIC_RUNTIME_DIR requires a single-config Release build")
    endif()
    foreach(_classic_target NeuroModelerConsole ClassicStructTrainReplay ClassicSavedStateCheck Test_PulseLib_StorageComponents)
        set_target_properties(${_classic_target} PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${NMSDK_CLASSIC_RUNTIME_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_RELEASE "${NMSDK_CLASSIC_RUNTIME_DIR}")
    endforeach()
endif()

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


