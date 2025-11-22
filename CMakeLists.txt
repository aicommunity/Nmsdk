cmake_minimum_required(VERSION 3.16)
project(Nmsdk LANGUAGES CXX)

# Политики и стандарт
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

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


