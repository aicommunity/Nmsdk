cmake_minimum_required(VERSION 3.19)
project(TimeLearnerAudit LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
get_filename_component(REPO "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(GTEST_SOURCE "${REPO}/build/win-vs2019-release/_deps/googletest-src" CACHE PATH "Existing googletest source; no download")
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
add_subdirectory("${GTEST_SOURCE}" "${CMAKE_BINARY_DIR}/gtest")
find_package(Qt5 REQUIRED COMPONENTS Core Gui)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
  "${REPO}/Libraries/Nmsdk-PulseLib/Core/NPatternResponseAnalyzer.cpp"
  "${REPO}/Libraries/Nmsdk-PulseLib/Core/NAxoneDelay.cpp"
  "${REPO}/Libraries/Nmsdk-PulseLib/Core/NAperiodicLink.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/generate_probes.py")
execute_process(COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_LIST_DIR}/generate_probes.py"
  "${CMAKE_BINARY_DIR}/extracted_probes.cpp" COMMAND_ERROR_IS_FATAL ANY)
enable_testing()
add_executable(audit_existing_gui
  "${REPO}/Rdk/Tests/Unit/GUI/Test_UModernDiagramLinkRouter.cpp"
  "${REPO}/Rdk/Tests/Unit/GUI/Test_UModernDiagramScopePath.cpp"
  "${REPO}/Rdk/GUI/Qt/UModernDiagramLinkRouter.cpp")
target_include_directories(audit_existing_gui PRIVATE "${REPO}/Rdk/GUI/Qt")
target_link_libraries(audit_existing_gui PRIVATE gtest_main Qt5::Core Qt5::Gui)
add_test(NAME existing_gui COMMAND audit_existing_gui)
add_executable(audit_counterexamples counterexamples.cpp "${CMAKE_BINARY_DIR}/extracted_probes.cpp"
  "${REPO}/Libraries/Nmsdk-PulseLib/Core/NNeuronPostTrainTune.cpp"
  "${REPO}/Rdk/GUI/Qt/UModernDiagramLinkRouter.cpp")
target_include_directories(audit_counterexamples PRIVATE "${REPO}/Libraries/Nmsdk-PulseLib/Core" "${REPO}/Rdk/GUI/Qt")
target_link_libraries(audit_counterexamples PRIVATE gtest_main Qt5::Core Qt5::Gui)
add_test(NAME counterexamples COMMAND audit_counterexamples)

# Incremental audit of Branch commits daf9c23..9a6cee0.
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
  "${REPO}/Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.cpp"
  "${CMAKE_CURRENT_LIST_DIR}/generate_branch_update_probes.py")
execute_process(COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_LIST_DIR}/generate_branch_update_probes.py"
  "${CMAKE_BINARY_DIR}/branch_update_probes.cpp" COMMAND_ERROR_IS_FATAL ANY)
add_executable(audit_branch_update "${CMAKE_BINARY_DIR}/branch_update_probes.cpp"
  "${REPO}/Libraries/Nmsdk-PulseLib/Core/NNeuronPostTrainTune.cpp")
target_include_directories(audit_branch_update PRIVATE "${REPO}/Libraries/Nmsdk-PulseLib/Core")
target_link_libraries(audit_branch_update PRIVATE gtest_main)
add_test(NAME branch_update COMMAND audit_branch_update)
