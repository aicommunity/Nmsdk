cmake_minimum_required(VERSION 3.23)
if(NOT TARGET NeuroModelerConsole)
  return()
endif()
add_executable(Test_ConfigValidation Test_ConfigValidation.cpp)
target_include_directories(Test_ConfigValidation PRIVATE "${CMAKE_SOURCE_DIR}")
target_compile_definitions(Test_ConfigValidation PRIVATE
  NEUROMODELER_CONSOLE_EXE="$<TARGET_FILE:NeuroModelerConsole>"
  TEST_CONFIGS_DIR="${CMAKE_SOURCE_DIR}/Bin/Configs/TestValidation")
add_dependencies(Test_ConfigValidation NeuroModelerConsole)
add_test(NAME ConfigValidationTests COMMAND Test_ConfigValidation)
