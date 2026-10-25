cmake_minimum_required(VERSION 3.16)

project(ConfigValidationTests)

# Resolve the current target, including on a fresh tree before the first build.
# find_program could accidentally select a stale executable from another build.
if(NOT TARGET NeuroModelerConsole)
    message(WARNING "NeuroModelerConsole target is unavailable. Tests will be skipped.")
    return()
endif()
set(NEUROMODELER_CONSOLE_EXE "$<TARGET_FILE:NeuroModelerConsole>")

# Path to test configurations
set(TEST_CONFIGS_DIR "${CMAKE_SOURCE_DIR}/Bin/Configs/TestValidation")

# Create test executable
add_executable(Test_ConfigValidation Test_ConfigValidation.cpp)
add_dependencies(Test_ConfigValidation NeuroModelerConsole)

# Compilation settings
target_include_directories(Test_ConfigValidation PRIVATE
    ${CMAKE_SOURCE_DIR}
)

# Linking with required libraries (if needed)
# target_link_libraries(Test_ConfigValidation ...)

# Add definitions to pass paths into the test
target_compile_definitions(Test_ConfigValidation PRIVATE
    NEUROMODELER_CONSOLE_EXE="${NEUROMODELER_CONSOLE_EXE}"
    TEST_CONFIGS_DIR="${TEST_CONFIGS_DIR}"
)

# Register test in CTest
enable_testing()
add_test(NAME ConfigValidationTests COMMAND Test_ConfigValidation)
set_tests_properties(ConfigValidationTests PROPERTIES WORKING_DIRECTORY "${DEPLOY_ROOT}")
