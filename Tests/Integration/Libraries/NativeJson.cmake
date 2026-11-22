# Compile the actual production parser without a full Rdk/neuron SDK rebuild.
# The same cases also belong to StorageComponents; this target does not prove
# native learned-state import, model equivalence or scientific convergence.
set(_tl_json_core "${NMSDK_TRAINING_ALGORITHM_SOURCE_ROOT}/Libraries/Nmsdk-PulseLib/Core/TimeLearner")
set(_tl_json_tests "${NMSDK_TRAINING_ALGORITHM_SOURCE_ROOT}/Tests/Integration")
add_executable(Test_PulseLib_NativeJson
    "${_tl_json_tests}/Libraries/Test_PulseLib_NativeJson.cpp"
    "${_tl_json_tests}/Support/ProbeAlgorithmMain.cpp"
    "${_tl_json_core}/StrictNativeJson.cpp")
target_include_directories(Test_PulseLib_NativeJson PRIVATE "${_tl_json_core}/..")
target_link_libraries(Test_PulseLib_NativeJson PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_PulseLib_NativeJson PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${NMSDK_TRAINING_ALGORITHM_RUNTIME}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${NMSDK_TRAINING_ALGORITHM_RUNTIME}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${NMSDK_TRAINING_ALGORITHM_RUNTIME}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${NMSDK_TRAINING_ALGORITHM_RUNTIME}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${NMSDK_TRAINING_ALGORITHM_RUNTIME}")
add_test(NAME PulseLib_NativeJson COMMAND Test_PulseLib_NativeJson)
set_tests_properties(PulseLib_NativeJson PROPERTIES LABELS "unit;timelearner;transport")
