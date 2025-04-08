cmake_minimum_required(VERSION 3.23)

project(Nmsdk VERSION 0.1 LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt5 REQUIRED COMPONENTS Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Widgets)

set(Rdk_Nmsdk_libs
    Rdk-BasicLib
    Rdk-CvBasicLib
    Rdk-HardwareLib
    Nmsdk-MotionControlLib
    Nmsdk-PulseLib
)

if(DEFINED RDK_USE_PYTHON)
    list(APPEND Rdk_Nmsdk_libs Rdk-PyMachineLearningLib)
endif()

if(DEFINED RDK_USE_DARKNET)
    list(APPEND Rdk_Nmsdk_libs Rdk-DarknetLib)
endif()

if(DEFINED RDK_USE_TENSORFLOW)
    list(APPEND Rdk_Nmsdk_libs Rdk-TensorflowLib)
endif()

foreach(lib ${Rdk_Nmsdk_libs})
    add_subdirectory(${CMAKE_SOURCE_DIR}/Libraries/${lib}/Build/CMake)
endforeach()

add_subdirectory(${CMAKE_SOURCE_DIR}/Rdk/Build/Lib/CMake)

if(WIN32)
#    add_subdirectory(${CMAKE_SOURCE_DIR}/Rdk/ThirdParty/curl/build/qt)
endif()

add_subdirectory(${CMAKE_SOURCE_DIR}/Build/CMake/NeuroModeler)
add_subdirectory(${CMAKE_SOURCE_DIR}/Build/CMake/NeuroModelerConsole)
