cmake_minimum_required(VERSION 3.16)

project(ConfigValidationTests)

# Находим исполняемый файл NeuroModelerConsole
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

# Путь к тестовым конфигурациям
set(TEST_CONFIGS_DIR "${CMAKE_SOURCE_DIR}/Bin/Configs/TestValidation")

# Создаем тестовый исполняемый файл
add_executable(Test_ConfigValidation Test_ConfigValidation.cpp)

# Настройка компиляции
target_include_directories(Test_ConfigValidation PRIVATE
    ${CMAKE_SOURCE_DIR}
)

# Линковка с необходимыми библиотеками (если нужно)
# target_link_libraries(Test_ConfigValidation ...)

# Добавляем определение для передачи путей в тест
target_compile_definitions(Test_ConfigValidation PRIVATE
    NEUROMODELER_CONSOLE_EXE="${NEUROMODELER_CONSOLE_EXE}"
    TEST_CONFIGS_DIR="${TEST_CONFIGS_DIR}"
)

# Добавляем тест в CTest
enable_testing()
add_test(NAME ConfigValidationTests COMMAND Test_ConfigValidation)
