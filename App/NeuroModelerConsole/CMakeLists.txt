# NeuroModelerConsole Application CMake Configuration
cmake_minimum_required(VERSION 3.16)

# C++20 configuration
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find required packages
find_package(Qt5 REQUIRED COMPONENTS Core)
# Boost dependencies removed - using modern C++20 alternatives
# Boost::program_options replaced with custom ModernCLI::CommandLineParser

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Engine
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Application
    ${CMAKE_SOURCE_DIR}/Rdk/Core/System
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Math
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Utilities
    ${CMAKE_SOURCE_DIR}/Libraries
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-HardwareLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-HardwareLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Deploy/Include
)

# Source files
set(SOURCES
    main.cpp
    ../../Libraries/Libraries_con.cpp
)

# Note: GUI files removed for console application
# Missing RDK functions will be stubbed out

# Create executable
add_executable(NeuroModelerConsole ${SOURCES})

# Modern compiler flags for GNU
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(NeuroModelerConsole PRIVATE
        -Wall -Wextra -Wpedantic
        -O3 -march=native -mtune=native
        -flto -fuse-linker-plugin
    )
endif()

# Precompiled headers
target_precompile_headers(NeuroModelerConsole PRIVATE
    <memory>
    <string>
    <vector>
    <QCoreApplication>
)

# Link libraries
target_link_libraries(NeuroModelerConsole
    Qt5::Core
    rdk.static.qt
    Rdk-BasicLib.qt
    Nmsdk-PulseLib.qt
    Nmsdk-MotionControlLib.qt
    Rdk-CvBasicLib.qt
    Rdk-HardwareLib.qt
    Threads::Threads
    # Boost dependencies removed - using modern C++20 alternatives
)

# Расширенные настройки отладки
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(NeuroModelerConsole PRIVATE
        -g3                    # Максимальная отладочная информация
        -O0                    # Отключение оптимизации
        -fno-omit-frame-pointer # Сохранение указателей фреймов
        -fno-inline           # Отключение инлайнинга для лучшей отладки
        -fno-optimize-sibling-calls # Отключение оптимизации хвостовых вызовов
        -rdynamic              # Экспорт всех символов для отладки
        -DDEBUG                # Определение DEBUG
        -D_DEBUG               # Определение _DEBUG
    )
    
    # Дополнительные флаги для детальной отладки
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        target_compile_options(NeuroModelerConsole PRIVATE
            -ggdb3              # Расширенная отладочная информация для GDB
            -fno-eliminate-unused-debug-symbols # Сохранение неиспользуемых символов
            -fno-merge-debug-strings # Отключение слияния строк отладки
        )
    endif()
    
    # Настройки для лучшей работы с отладчиком
    target_compile_definitions(NeuroModelerConsole PRIVATE
        RDK_DEBUG=1
        RDK_VERBOSE_DEBUG=1
        RDK_ENABLE_ASSERTIONS=1
        NEUROMODELER_DEBUG=1
        NEUROMODELER_CONSOLE_DEBUG=1
    )
endif()

# Настройки для RelWithDebInfo
if(CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
    target_compile_options(NeuroModelerConsole PRIVATE
        -g                    # Отладочная информация
        -O2                   # Умеренная оптимизация
        -fno-omit-frame-pointer
        -rdynamic
    )
    
    target_compile_definitions(NeuroModelerConsole PRIVATE
        RDK_DEBUG=1
        NEUROMODELER_DEBUG=1
    )
endif()

# Set output directory to Bin/Platform/Linux
set_target_properties(NeuroModelerConsole PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${DEPLOY_ROOT}
)