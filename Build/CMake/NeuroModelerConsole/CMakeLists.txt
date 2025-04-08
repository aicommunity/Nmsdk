cmake_minimum_required(VERSION 3.14)
project(NeuroModelerConsole VERSION 1.1.3.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt5 REQUIRED COMPONENTS Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Network Sql Xml SerialPort)

if(WIN32)
    set(DESTDIR ${CMAKE_SOURCE_DIR}/../../../Bin/Platform/Win/)
    set(ANACONDA_PATH $ENV{ANACONDA_PATH})
    link_directories(${ANACONDA_PATH}/libs/)
else()
    set(DESTDIR ${CMAKE_SOURCE_DIR}/../../../Bin/Platform/Linux/)
endif()

if(MSVC)
    add_compile_options(/bigobj)
endif()

add_definitions(
    -DQT_DLL
    -DQT_WIDGETS_LIB
    -DRDK_APP_VERSION=0
    -DRDK_APP_URL="https://neuromodeler.ru"
#    -DRDK_APP_LICENSE="There is a public domain software (2000-2023)"
    -DRDK_APP_NAME="Neuro Modeler"
)

include_directories(
    ${CMAKE_SOURCE_DIR}/../../../Gui/Qt
    ${CMAKE_SOURCE_DIR}/../../../Deploy/Include
    ${CMAKE_SOURCE_DIR}/../../../Rdk/Core/Graphics
    ${CMAKE_SOURCE_DIR}/GeneratedFiles
    ${CMAKE_SOURCE_DIR}/GeneratedFiles/Debug
    ${CMAKE_SOURCE_DIR}/../../../Rdk/Deploy/Include
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt
)

if(UNIX)
    include_directories(/usr/local/include)
endif()

set(SOURCES
    ${CMAKE_SOURCE_DIR}/../../../Libraries/Libraries.cpp
    ${CMAKE_SOURCE_DIR}/main.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UEngineControlQt.cpp
)

set(HEADERS
    ${CMAKE_SOURCE_DIR}/../../../Libraries/Libraries.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UEngineControlQt.h
)

add_executable(NeuroModelerConsole)

target_link_libraries(NeuroModelerConsole PRIVATE
    Qt5::Core
    Qt5::Network
    Qt5::Sql
    Qt5::Xml
    Qt5::SerialPort
)

if(WIN32)
    target_link_libraries(NeuroModelerConsole PRIVATE
        Wldap32
        Ws2_32
        Crypt32
    )
endif()

set(NMSDK_LIBS_NAMES
    Rdk-BasicLib
    Rdk-CvBasicLib
    Rdk-HardwareLib
    Nmsdk-MotionControlLib
    Nmsdk-PulseLib
    rdk.static
)

if(DEFINED RDK_USE_PYTHON)
    list(APPEND NMSDK_LIBS_NAMES Rdk-PyMachineLearningLib)
endif()

if(DEFINED RDK_USE_DARKNET)
    list(APPEND NMSDK_LIBS_NAMES Rdk-DarknetLib)
endif()

if(DEFINED RDK_USE_TENSORFLOW)
    list(APPEND NMSDK_LIBS_NAMES Rdk-TensorflowLib)
endif()

foreach(lib ${NMSDK_LIBS_NAMES})
    if(WIN32)
#        target_link_libraries(NeuroModelerConsole PRIVATE ${CMAKE_SOURCE_DIR}/../../../Bin/Platform/Win/Lib.Qt/${lib}.qt.lib)
    else()
#        target_link_libraries(NeuroModelerConsole PRIVATE ${CMAKE_SOURCE_DIR}/../../../Bin/Platform/Linux/Lib.Qt/lib${lib}.qt.a)
    endif()
endforeach()

if(DEFINED RDK_USE_OPENCV)
    if(WIN32)
        target_link_libraries(NeuroModelerConsole PRIVATE ${OPENCV_WIN_LINKER_LINE})
    else()
        target_link_libraries(NeuroModelerConsole PRIVATE ${OPENCV_UNIX_LINKER_LINE})
    endif()
endif()

if(WIN32)
    target_link_libraries(NeuroModelerConsole PRIVATE ${BOOST_WIN_LINKER_LINE})
else()
    target_link_libraries(NeuroModelerConsole PRIVATE ${BOOST_UNIX_LINKER_LINE})
endif()

if(DEFINED RDK_USE_DARKNET AND UNIX)
    target_link_libraries(NeuroModelerConsole PRIVATE ${DARKNET_UNIX_LINKER_LINE})
endif()

if(DEFINED RDK_USE_TENSORFLOW)
    if(WIN32)
        target_link_libraries(NeuroModelerConsole PRIVATE ${TENSORFLOW_WIN_LINKER_LINE})
    else()
        target_link_libraries(NeuroModelerConsole PRIVATE ${TENSORFLOW_UNIX_LINKER_LINE})
    endif()
endif()

if(DEFINED RDK_USE_MATLAB)
    if(WIN32)
        target_link_libraries(NeuroModelerConsole PRIVATE ${MATLAB_WIN_LINKER_LINE})
    else()
        target_link_libraries(NeuroModelerConsole PRIVATE ${MATLAB_UNIX_LINKER_LINE})
    endif()
endif()
