# The full production decision implementations are compiled directly here.
# The same test files also remain in StorageComponents. This unit target does
# not replace native storage/scheduler, Console or scientific model A/B gates.
set(_tl_core "${NMSDK_TRAINING_ALGORITHM_SOURCE_ROOT}/Libraries/Nmsdk-PulseLib/Core/TimeLearner")
set(_tl_tests "${NMSDK_TRAINING_ALGORITHM_SOURCE_ROOT}/Tests/Integration")
add_executable(Test_PulseLib_TrainingAlgorithms
    "${_tl_tests}/Libraries/Test_PulseLib_BoundedTraining.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_MeasuredResistanceSearch.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_MeasuredLengthSearch.cpp"
    "${_tl_tests}/Libraries/Test_PulseLib_MeasuredCapacitanceSearch.cpp"
    "${_tl_tests}/Support/ProbeAlgorithmMain.cpp"
    "${_tl_core}/BoundedTraining.cpp"
    "${_tl_core}/ProbeObservation.cpp"
    "${_tl_core}/MeasuredResponse.cpp"
    "${_tl_core}/FinalVerification.cpp"
    "${_tl_core}/CandidateWindowContractValidation.cpp"
    "${_tl_core}/CompositeTrainingMeasurement.cpp"
    "${_tl_core}/StimulusSubset.cpp"
    "${_tl_core}/MeasuredResistanceSearch.cpp"
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
