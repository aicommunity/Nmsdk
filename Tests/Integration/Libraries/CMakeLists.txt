cmake_minimum_required(VERSION 3.16)

message(STATUS "Libraries integration tests directory created")

set(PULSELIB_TEST_OUTPUT_DIR "${DEPLOY_ROOT}")

set(NMSDK_TRAINING_ALGORITHM_SOURCE_ROOT "${CMAKE_SOURCE_DIR}")
set(NMSDK_TRAINING_ALGORITHM_RUNTIME "${PULSELIB_TEST_OUTPUT_DIR}")
include("${CMAKE_CURRENT_LIST_DIR}/TrainingAlgorithms.cmake")

add_executable(Test_Rdk_RuntimeDescriptions
    Test_Rdk_RuntimeDescriptions.cpp ../Support/ProbeAlgorithmMain.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp)
target_link_libraries(Test_Rdk_RuntimeDescriptions PRIVATE rdk.static.qt
    Rdk-HardwareLib.qt Nmsdk-MotionControlLib.qt Nmsdk-PulseLib.qt
    GTest::gtest Nmsdk::Qt::Core)
target_include_directories(Test_Rdk_RuntimeDescriptions PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Libraries)
set_target_properties(Test_Rdk_RuntimeDescriptions PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PULSELIB_TEST_OUTPUT_DIR}")
add_test(NAME Rdk_RuntimeDescriptions COMMAND Test_Rdk_RuntimeDescriptions)
set_tests_properties(Rdk_RuntimeDescriptions PROPERTIES WORKING_DIRECTORY "${DEPLOY_ROOT}")

# Diagnostic domain hypotheses are distinct from accepted training evidence.
add_executable(Test_PulseLib_ResponseDomains
    Test_PulseLib_ResponseDomains.cpp ../Support/ProbeAlgorithmMain.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/MeasuredResponse.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/ResponseDomainAssociation.cpp)
target_link_libraries(Test_PulseLib_ResponseDomains PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_PulseLib_ResponseDomains PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PULSELIB_TEST_OUTPUT_DIR}")
add_test(NAME PulseLib_ResponseDomains COMMAND Test_PulseLib_ResponseDomains)
set_tests_properties(PulseLib_ResponseDomains PROPERTIES WORKING_DIRECTORY "${DEPLOY_ROOT}" LABELS "unit;timelearner;diagnostic")

# The matched-omission operational selector compiles its actual production
# implementation. This pure target does not replace native runner acceptance.
add_executable(Test_PulseLib_MatchedOmissionAssignment
    Test_PulseLib_MatchedOmissionAssignment.cpp ../Support/ProbeAlgorithmMain.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/MeasuredResponse.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/MatchedOmissionValidation.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/MatchedOmissionAssignment.cpp)
target_link_libraries(Test_PulseLib_MatchedOmissionAssignment PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_PulseLib_MatchedOmissionAssignment PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PULSELIB_TEST_OUTPUT_DIR}")
add_test(NAME PulseLib_MatchedOmissionAssignment COMMAND Test_PulseLib_MatchedOmissionAssignment)
set_tests_properties(PulseLib_MatchedOmissionAssignment PROPERTIES
    WORKING_DIRECTORY "${DEPLOY_ROOT}" LABELS "unit;timelearner")

# Geometry-only opt-in diagnostic. Context/native/Train gates remain separate.
add_executable(Test_PulseLib_DeclaredWindowBasinAssignment
    Test_PulseLib_DeclaredWindowBasinAssignment.cpp ../Support/ProbeAlgorithmMain.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/MeasuredResponse.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/DeclaredWindowBasinAssignment.cpp)
target_link_libraries(Test_PulseLib_DeclaredWindowBasinAssignment PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_PulseLib_DeclaredWindowBasinAssignment PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PULSELIB_TEST_OUTPUT_DIR}")
add_test(NAME PulseLib_DeclaredWindowBasinAssignment COMMAND Test_PulseLib_DeclaredWindowBasinAssignment)
set_tests_properties(PulseLib_DeclaredWindowBasinAssignment PROPERTIES
    WORKING_DIRECTORY "${DEPLOY_ROOT}" LABELS "unit;timelearner;diagnostic")

# Pure candidate-window arithmetic. No native/storage admission is provided.
add_executable(Test_PulseLib_CandidateWindowPolicy
    Test_PulseLib_CandidateWindowPolicy.cpp ../Support/ProbeAlgorithmMain.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/CandidateWindowPolicy.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/TrainingCapacitance.cpp)
target_link_libraries(Test_PulseLib_CandidateWindowPolicy PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_PulseLib_CandidateWindowPolicy PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PULSELIB_TEST_OUTPUT_DIR}")
add_test(NAME PulseLib_CandidateWindowPolicy COMMAND Test_PulseLib_CandidateWindowPolicy)
set_tests_properties(PulseLib_CandidateWindowPolicy PROPERTIES
    WORKING_DIRECTORY "${DEPLOY_ROOT}" LABELS "unit;timelearner;arithmetic")

# Fast observer/clock checks compile the actual production implementation.
# Keep the same cases in the full storage target: this unit executable does
# not replace native lifecycle, storage, routing or physical response gates.
add_executable(Test_PulseLib_ProbeAlgorithms
    Test_PulseLib_ProbeObservation.cpp
    ../Support/ProbeAlgorithmMain.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/ProbeObservation.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/MeasuredResponse.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/StimulusSubset.cpp
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

# Exercise certificate validation against the production implementations.
# Physical storage/scheduler checks remain in StorageComponents below.
add_executable(Test_PulseLib_VerificationAlgorithms
    Test_PulseLib_FinalVerification.cpp
    ../Support/ProbeAlgorithmMain.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/ProbeObservation.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/MeasuredResponse.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/FinalVerification.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/CandidateWindowContractValidation.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/CompositeTrainingMeasurement.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/StimulusSubset.cpp
)
target_link_libraries(Test_PulseLib_VerificationAlgorithms PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_PulseLib_VerificationAlgorithms PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PULSELIB_TEST_OUTPUT_DIR}"
)
add_test(NAME PulseLib_VerificationAlgorithms COMMAND Test_PulseLib_VerificationAlgorithms)
set_tests_properties(PulseLib_VerificationAlgorithms PROPERTIES
    WORKING_DIRECTORY "${DEPLOY_ROOT}" LABELS "unit;timelearner")

# Presentation planning is distinct from a native response or training result.
add_executable(Test_PulseLib_StimulusSubset
    Test_PulseLib_StimulusSubset.cpp
    ../Support/ProbeAlgorithmMain.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/StimulusSubset.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/ProbeObservation.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/MeasuredResponse.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/FinalVerification.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/CandidateWindowContractValidation.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core/TimeLearner/CompositeTrainingMeasurement.cpp
)
target_link_libraries(Test_PulseLib_StimulusSubset PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_PulseLib_StimulusSubset PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${PULSELIB_TEST_OUTPUT_DIR}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${PULSELIB_TEST_OUTPUT_DIR}"
)
add_test(NAME PulseLib_StimulusSubset COMMAND Test_PulseLib_StimulusSubset)
set_tests_properties(PulseLib_StimulusSubset PROPERTIES
    WORKING_DIRECTORY "${DEPLOY_ROOT}" LABELS "unit;timelearner")

add_executable(Test_PulseLib_StorageComponents
    Test_PulseLib_DeclaredWindowBasinAssignment.cpp
    Test_PulseLib_MatchedOmissionEvidence.cpp
    Test_PulseLib_MatchedOmissionAssignment.cpp
    Test_PulseLib_StimulusSubset.cpp
    Test_PulseLib_StorageComponents.cpp
    Test_PulseLib_DatasetFileValidation.cpp
    Test_PulseLib_DatasetClock.cpp
    Test_PulseLib_NeuronGrowth.cpp
    Test_PulseLib_TimeLearnerResistance.cpp
    Test_PulseLib_Observations.cpp
    Test_PulseLib_IsiTemplateValidation.cpp
    Test_PulseLib_LifecycleContracts.cpp
    Test_PulseLib_TimingPropertyContracts.cpp
    Test_PulseLib_ResistanceStepOwnership.cpp
    Test_PulseLib_HotReadoutReset.cpp
    Test_PulseLib_LoadedLearnerReadout.cpp
    Test_PulseLib_ModelInspection.cpp
    Test_PulseLib_ModelRoundtrip.cpp
    Test_PulseLib_ClassImages.cpp
    Test_PulseLib_StorageProfiles.cpp
    Test_PulseLib_ModelIdentity.cpp
    Test_PulseLib_ModelArchive.cpp
    Test_PulseLib_NativeLoadHistory.cpp
    Test_PulseLib_ControllerCompatibility.cpp
    Test_PulseLib_LegacyController.cpp
    Test_PulseLib_ProbeObservation.cpp
    Test_PulseLib_NativeProbe.cpp
    Test_PulseLib_NativeExecution.cpp
    Test_PulseLib_SinglePulseCharacterization.cpp
    Test_PulseLib_PreparedModel.cpp
    Test_PulseLib_FinalVerification.cpp
    Test_PulseLib_BoundedTraining.cpp
    Test_PulseLib_N0Geometry.cpp
    Test_PulseLib_CompositeTraining.cpp
    Test_PulseLib_CandidateWindowDeclarations.cpp
    Test_PulseLib_CandidateWindowProposalData.cpp
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

option(NMSDK_BUILD_RECORDED_MODEL_INPUT_TESTS
    "Enable explicitly staged recorded-model tests for owned native gates" OFF)
if(NMSDK_BUILD_RECORDED_MODEL_INPUT_TESTS)
    target_compile_definitions(Test_PulseLib_StorageComponents PRIVATE NMSDK_RECORDED_MODEL_INPUT_TESTS=1)
endif()

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

# Recorded-model cases require hash-bound files staged by the owned gate.
# They are selected separately, including in builds with the opt-in enabled.
add_test(NAME PulseLib_StorageComponents COMMAND Test_PulseLib_StorageComponents
    --gtest_filter=-NativeRecordedRecoveryArchive.*)
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


