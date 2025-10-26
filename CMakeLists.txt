cmake_minimum_required(VERSION 3.16)
project(Nmsdk LANGUAGES CXX)

# Установка типа сборки по умолчанию
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Debug" CACHE STRING "Choose the type of build." FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

# Убедимся, что CMAKE_BUILD_TYPE установлен правильно
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

# Установка переменных для всех типов сборки
set(CMAKE_CONFIGURATION_TYPES "Debug;Release;MinSizeRel;RelWithDebInfo" CACHE STRING "Available build types" FORCE)

# Специальная настройка для Qt Creator
if(DEFINED ENV{QTCREATOR_CMAKE_BUILD_TYPE})
    set(CMAKE_BUILD_TYPE $ENV{QTCREATOR_CMAKE_BUILD_TYPE} CACHE STRING "Build type from Qt Creator" FORCE)
endif()

# Define Boost macros to suppress warnings
add_definitions(-DBOOST_BIND_GLOBAL_PLACEHOLDERS)

# Add compiler flags to suppress warnings
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    add_compile_options(-Wno-unused-function -Wno-sign-conversion -Wno-deprecated-enum-enum-conversion)
endif()

# Политики и стандарт
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Современные флаги компилятора для C++20
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion")
    
    # Debug flags
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0")
    
    # Release flags with LTO
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG -flto")
    
    # RelWithDebInfo flags
    set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} -O2 -g -DNDEBUG")
    
    # MinSizeRel flags
    set(CMAKE_CXX_FLAGS_MINSIZEREL "${CMAKE_CXX_FLAGS_MINSIZEREL} -Os -DNDEBUG")
    
    # Sanitizers (optional, can be enabled via CMake options)
    option(USE_ADDRESS_SANITIZER "Enable AddressSanitizer" OFF)
    option(USE_THREAD_SANITIZER "Enable ThreadSanitizer" OFF)
    option(USE_UNDEFINED_SANITIZER "Enable UndefinedBehaviorSanitizer" OFF)
    
    if(USE_ADDRESS_SANITIZER)
        set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fsanitize=address -fno-omit-frame-pointer")
        set(CMAKE_LINKER_FLAGS_DEBUG "${CMAKE_LINKER_FLAGS_DEBUG} -fsanitize=address")
    endif()
    
    if(USE_THREAD_SANITIZER)
        set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fsanitize=thread -fno-omit-frame-pointer")
        set(CMAKE_LINKER_FLAGS_DEBUG "${CMAKE_LINKER_FLAGS_DEBUG} -fsanitize=thread")
    endif()
    
    if(USE_UNDEFINED_SANITIZER)
        set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -fsanitize=undefined -fno-omit-frame-pointer")
        set(CMAKE_LINKER_FLAGS_DEBUG "${CMAKE_LINKER_FLAGS_DEBUG} -fsanitize=undefined")
    endif()
    
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4 /permissive-")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Od /Zi")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2 /Ob2 /DNDEBUG /GL")
endif()

# Precompiled headers для ускорения компиляции
set(CMAKE_PCH_INSTANTIATE_TEMPLATES ON)

# Каталог общих модулей CMake
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

# Вывод бинарей и библиотек в Bin/Platform/<OS>
if (WIN32)
  set(PLATFORM_DIR "Win")
else()
  set(PLATFORM_DIR "Linux")
endif()

set(DEPLOY_ROOT "${CMAKE_SOURCE_DIR}/Bin/Platform/${PLATFORM_DIR}")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${DEPLOY_ROOT}/Lib.CMake")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${DEPLOY_ROOT}/Lib.CMake")

# Общие определения и зависимости (OpenCV/Boost/и т.д.)
include(RdkDefines OPTIONAL)

# Google glog для логирования
find_package(glog REQUIRED)

# Rdk core library
add_subdirectory(Rdk)

# Component libraries
add_subdirectory(Libraries/Rdk-BasicLib)
add_subdirectory(Libraries/Rdk-CvBasicLib)
add_subdirectory(Libraries/Rdk-HardwareLib)
add_subdirectory(Libraries/Nmsdk-MotionControlLib)
add_subdirectory(Libraries/Nmsdk-PulseLib)

# Applications
add_subdirectory(App/NeuroModeler)
add_subdirectory(App/NeuroModelerConsole)
add_subdirectory(Tests/TestStorage)

# Тесты
option(BUILD_TESTS "Build tests" ON)
if(BUILD_TESTS)
    add_subdirectory(tests)
endif()


