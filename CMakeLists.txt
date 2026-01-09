cmake_minimum_required(VERSION 3.16)

# Нормализация пути vcpkg toolchain файла (только для Windows)
# Это должно быть ДО project(), так как CMAKE_TOOLCHAIN_FILE используется при инициализации проекта
if(EXISTS "${CMAKE_SOURCE_DIR}/cmake/NormalizeVcpkgPath.cmake")
    include("${CMAKE_SOURCE_DIR}/cmake/NormalizeVcpkgPath.cmake")
endif()

# Включаем поддержку CMAKE_MSVC_RUNTIME_LIBRARY (CMP0091) чтобы управлять /MDd|/MD
if (MSVC AND POLICY CMP0091)
  cmake_policy(SET CMP0091 NEW)
endif()

project(Nmsdk LANGUAGES CXX)

# Автоматическая настройка параллельной сборки
# Определяем количество ядер процессора, если CMAKE_BUILD_PARALLEL_LEVEL не задан
# Эта настройка автоматически распространяется на все подпроекты через add_subdirectory()
if(NOT DEFINED ENV{CMAKE_BUILD_PARALLEL_LEVEL})
    include(ProcessorCount)
    ProcessorCount(N)
    if(NOT N EQUAL 0)
        # Устанавливаем переменную окружения для использования при сборке
        set(ENV{CMAKE_BUILD_PARALLEL_LEVEL} ${N})
        message(STATUS "CMAKE_BUILD_PARALLEL_LEVEL set to ${N} (auto-detected CPU cores)")
    else()
        # Fallback: используем значение по умолчанию
        set(ENV{CMAKE_BUILD_PARALLEL_LEVEL} "4")
        message(STATUS "CMAKE_BUILD_PARALLEL_LEVEL set to 4 (default fallback)")
    endif()
else()
    message(STATUS "CMAKE_BUILD_PARALLEL_LEVEL already set to $ENV{CMAKE_BUILD_PARALLEL_LEVEL}")
endif()

# Политики и стандарт
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

# Общие настройки для MSVC рантайма (DLL) — единообразно для всех таргетов
if (MSVC)
  set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<IF:$<CONFIG:Debug>,Debug,>DLL" CACHE STRING "" FORCE)
endif()

# Каталог общих модулей CMake
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

# Принудительная настройка Qt только из vcpkg (должно быть ДО find_package(Qt5))
# Это гарантирует использование Qt только из vcpkg, исключая локальные установки
if(EXISTS "${CMAKE_SOURCE_DIR}/cmake/ForceQtFromVcpkg.cmake")
    include("${CMAKE_SOURCE_DIR}/cmake/ForceQtFromVcpkg.cmake")
endif()

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

# Для multi-config генераторов (Visual Studio) убираем подпапки конфигурации
# Устанавливаем одинаковые пути для всех конфигураций
foreach(OUTPUTCONFIG DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
  string(TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} "${DEPLOY_ROOT}")
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${OUTPUTCONFIG} "${DEPLOY_ROOT}/Lib.CMake")
  set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_${OUTPUTCONFIG} "${DEPLOY_ROOT}/Lib.CMake")
endforeach()

# Общие определения и зависимости (OpenCV/Boost/и т.д.)
include(RdkDefines OPTIONAL)

# Подпроекты (постепенная миграция)
add_subdirectory(Rdk) # rdk.static
add_subdirectory(Libraries/Rdk-BasicLib) # Rdk-BasicLib
add_subdirectory(Libraries/Rdk-CvBasicLib) # Rdk-CvBasicLib
add_subdirectory(Libraries/Rdk-HardwareLib) # Rdk-HardwareLib
add_subdirectory(Libraries/Nmsdk-MotionControlLib) # Nmsdk-MotionControlLib
add_subdirectory(Libraries/Nmsdk-PulseLib) # Nmsdk-PulseLib
# add_subdirectory(Libraries/Rdk-CvBasicLib)
# add_subdirectory(Libraries/Rdk-HardwareLib)
# add_subdirectory(Libraries/Nmsdk-MotionControlLib)
# add_subdirectory(Libraries/Nmsdk-PulseLib)

# Приложения
add_subdirectory(App/NeuroModeler)
add_subdirectory(App/NeuroModelerConsole)

# Тесты (опционально, можно отключить для production сборки)
option(BUILD_TESTS "Build tests" ON)
if(BUILD_TESTS)
    add_subdirectory(Tests)
endif()


