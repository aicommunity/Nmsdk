# Compile the actual Console handshake, including a real acknowledgement later
# than the former ten-second deadline. This target does not calculate a model.
add_executable(Test_TimeLearner_RuntimeCapture
    "${CMAKE_CURRENT_LIST_DIR}/Test_TimeLearner_RuntimeCapture.cpp"
    "${CMAKE_CURRENT_LIST_DIR}/../Support/ProbeAlgorithmMain.cpp")
target_link_libraries(Test_TimeLearner_RuntimeCapture PRIVATE GTest::gtest Nmsdk::Qt::Core)
set_target_properties(Test_TimeLearner_RuntimeCapture PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${DEPLOY_ROOT}")
add_test(NAME TimeLearner_RuntimeCapture COMMAND Test_TimeLearner_RuntimeCapture)
set_tests_properties(TimeLearner_RuntimeCapture PROPERTIES LABELS "unit;timelearner;runtime")
