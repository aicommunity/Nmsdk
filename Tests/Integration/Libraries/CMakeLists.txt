cmake_minimum_required(VERSION 3.16)

message(STATUS "Libraries integration tests directory created")

set(PULSELIB_TEST_OUTPUT_DIR "${DEPLOY_ROOT}")

# Fast observer/clock checks compile the actual production implementation.
# Keep the same cases in the full storage target: this unit executable does
# not replace native lifecycle, storage, routing or physical response gates.
add_executable(Test_PulseLib_ProbeAlgorithms
    Test_PulseLib_ProbeObservation.cpp
    ../Support/ProbeAlgorithmMain.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/ProbeObservation.cpp
)
target_link_libraries(Test_PulseLib_ProbeAlgorithms PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_PulseLib_ProbeAlgorithms PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PULSELIB_TEST_OUTPUT_DIR}"
)
add_test(NAME PulseLib_ProbeAlgorithms COMMAND Test_PulseLib_ProbeAlgorithms)
set_tests_properties(PulseLib_ProbeAlgorithms PROPERTIES
    WORKING_DIRECTORY "${DEPLOY_ROOT}" LABELS "unit;timelearner")

add_executable(Test_PulseLib_StorageComponents
    Test_PulseLib_StorageComponents.cpp
    Test_PulseLib_DatasetFileValidation.cpp
    Test_PulseLib_DatasetClock.cpp
    Test_PulseLib_NeuronGrowth.cpp
    Test_PulseLib_TimeLearnerResistance.cpp
    Test_PulseLib_Observations.cpp
    Test_PulseLib_IsiTemplateValidation.cpp
    Test_PulseLib_LifecycleContracts.cpp
    Test_PulseLib_TimingPropertyContracts.cpp
    Test_PulseLib_HotReadoutReset.cpp
    Test_PulseLib_LoadedLearnerReadout.cpp
    Test_PulseLib_ModelInspection.cpp
    Test_PulseLib_ModelRoundtrip.cpp
    Test_PulseLib_ClassImages.cpp
    Test_PulseLib_StorageProfiles.cpp
    Test_PulseLib_ModelIdentity.cpp
    Test_PulseLib_ModelArchive.cpp
    Test_PulseLib_ControllerCompatibility.cpp
    Test_PulseLib_LegacyController.cpp
    Test_PulseLib_ProbeObservation.cpp
    Test_PulseLib_NativeProbe.cpp
    Test_PulseLib_NativeExecution.cpp
    Test_PulseLib_SinglePulseCharacterization.cpp
    Test_PulseLib_PreparedModel.cpp
    Test_PulseLib_FinalVerification.cpp
    Test_PulseLib_BoundedTraining.cpp
    Test_PulseLib_MeasuredResistanceSearch.cpp
    Test_PulseLib_MeasuredLengthSearch.cpp
    Test_PulseLib_MeasuredCapacitanceSearch.cpp
    Test_PulseLib_TrainingCapacitance.cpp
    Test_PulseLib_CapacitanceContexts.cpp
    Test_PulseLib_NativeModelEditor.cpp
    Test_PulseLib_InitialThreshold.cpp
    Test_PulseLib_CalibrationOwnership.cpp
    Test_PulseLib_PostTuneConfiguration.cpp
    Test_PulseLib_FixedPostTune.cpp
    Test_PulseLib_PhaseLifecycle.cpp
    Test_PulseLib_PostTuneProbeThreshold.cpp
    Test_PulseLib_FinalizationBoundary.cpp
    Test_PulseLib_SoloThresholdTrace.cpp
    Test_PulseLib_ConfigDialect.cpp
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

if(MSVC)
    # Real model-editor/lifecycle fixtures instantiate enough component and
    # property templates to exceed the standard COFF section count.
    target_compile_options(Test_PulseLib_StorageComponents PRIVATE /bigobj)
endif()

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
set_tests_properties(PulseLib_StorageComponents PROPERTIES WORKING_DIRECTORY "${DEPLOY_ROOT}")

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


