# The full production decision implementations are compiled directly here.
# The same test files also remain in StorageComponents. This unit target does
# not replace native storage/scheduler, Console or scientific model A/B gates.
set(_tl_core "${NMSDK_TRAINING_ALGORITHM_SOURCE_ROOT}/Libraries/Nmsdk-PulseLib/Core/TimeLearner")
set(_tl_tests "${NMSDK_TRAINING_ALGORITHM_SOURCE_ROOT}/Tests/Integration")
add_executable(Test_PulseLib_TrainingAlgorithms
    "${_tl_tests}/Libraries/Test_PulseLib_BoundedTraining.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_N0Geometry.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_N0LengthFamily.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_MeasuredResistanceSearch.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_MeasuredSynapseCountSearch.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_MeasuredLengthSearch.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_ModerateLengthSearch.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_MeasuredCapacitanceSearch.cpp"
    "${_tl_tests}/Support/ProbeAlgorithmMain.cpp"
    "${_tl_core}/BoundedTraining.cpp"
    "${_tl_core}/CandidateRecoveryEvidenceJson.cpp"
    "${_tl_core}/ProbeObservation.cpp"
    "${_tl_core}/MeasuredResponse.cpp"
    "${_tl_core}/FinalVerification.cpp"
    "${_tl_core}/CandidateWindowContractValidation.cpp"
    "${_tl_core}/CompositeTrainingMeasurement.cpp"
    "${_tl_core}/StimulusSubset.cpp"
    "${_tl_core}/MeasuredResistanceSearch.cpp"
    "${_tl_core}/MeasuredSynapseCountSearch.cpp"
    "${_tl_core}/MeasuredLengthSearch.cpp"
    "${_tl_core}/MeasuredCapacitanceSearch.cpp"
    "${_tl_core}/TrainingCapacitance.cpp"
    "${_tl_core}/CapacitanceRegion.cpp"
)
target_include_directories(Test_PulseLib_TrainingAlgorithms PRIVATE "${_tl_core}/..")
target_link_libraries(Test_PulseLib_TrainingAlgorithms PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_PulseLib_TrainingAlgorithms PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${NMSDK_TRAINING_ALGORITHM_RUNTIME}")
add_test(NAME PulseLib_TrainingAlgorithms COMMAND Test_PulseLib_TrainingAlgorithms)
set_tests_properties(PulseLib_TrainingAlgorithms PROPERTIES LABELS "unit;timelearner;decision")

# A new API is exercised only on the candidate source. The historical A/B
# cohort above remains compilable on the old public API. Both use complete
# production translation units; neither is native SDK/physics admission.
option(NMSDK_TEST_CLASSIC_INPUT_ROUND_ROBIN "Build opt-in Classic input traversal decision tests" OFF)
if(NMSDK_TEST_CLASSIC_INPUT_ROUND_ROBIN)
    get_target_property(_tl_decision_sources Test_PulseLib_TrainingAlgorithms SOURCES)
    list(FILTER _tl_decision_sources EXCLUDE REGEX "Test_PulseLib_.*\\.cpp$")
    add_executable(Test_PulseLib_ClassicInputRoundRobin
        "${_tl_tests}/Libraries/Test_PulseLib_ClassicInputRoundRobin.cpp"
        ${_tl_decision_sources})
    target_include_directories(Test_PulseLib_ClassicInputRoundRobin PRIVATE "${_tl_core}/..")
    target_link_libraries(Test_PulseLib_ClassicInputRoundRobin PRIVATE GTest::gtest Nmsdk::Qt::Core)
    set_target_properties(Test_PulseLib_ClassicInputRoundRobin PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${NMSDK_TRAINING_ALGORITHM_RUNTIME}")
    add_test(NAME PulseLib_ClassicInputRoundRobin COMMAND Test_PulseLib_ClassicInputRoundRobin)
    set_tests_properties(PulseLib_ClassicInputRoundRobin PROPERTIES LABELS "unit;timelearner;decision;round-robin")
endif()
