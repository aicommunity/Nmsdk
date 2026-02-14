cmake_minimum_required(VERSION 3.16)

project(ConfigValidationTests)

# Find NeuroModelerConsole executable
find_program(NEUROMODELER_CONSOLE_EXE
    NAMES NeuroModelerConsole
    PATHS
        ${CMAKE_BINARY_DIR}/Bin/Platform/Linux
        ${CMAKE_BINARY_DIR}/Bin/Platform/Windows
        ${CMAKE_SOURCE_DIR}/Bin/Platform/Linux
        ${CMAKE_SOURCE_DIR}/Bin/Platform/Windows
    NO_DEFAULT_PATH
)

if(NOT NEUROMODELER_CONSOLE_EXE)
    message(WARNING "NeuroModelerConsole executable not found. Tests will be skipped.")
    return()
endif()

message(STATUS "Found NeuroModelerConsole: ${NEUROMODELER_CONSOLE_EXE}")

# Path to test configurations
set(TEST_CONFIGS_DIR "${CMAKE_SOURCE_DIR}/Bin/Configs/TestValidation")

# Create test executable
add_executable(Test_ConfigValidation Test_ConfigValidation.cpp)

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
