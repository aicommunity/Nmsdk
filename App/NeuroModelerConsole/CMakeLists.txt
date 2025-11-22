cmake_minimum_required(VERSION 3.16)
project(NeuroModelerConsole LANGUAGES CXX)

add_executable(NeuroModelerConsole)

target_include_directories(NeuroModelerConsole
  PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries
)

target_sources(NeuroModelerConsole PRIVATE
  ${CMAKE_SOURCE_DIR}/App/NeuroModelerConsole/main.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/Core/Application/UEngineControl.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/Core/Application/UServerTransportTcp.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/Core/Application/UProjectDeployer.cpp
)

target_compile_definitions(NeuroModelerConsole PRIVATE QT_DLL)

find_package(Qt5 REQUIRED COMPONENTS Core Network Sql Xml SerialPort)

target_link_libraries(NeuroModelerConsole PRIVATE
  rdk.static.qt
  Rdk-BasicLib.qt
  Rdk-CvBasicLib.qt
  Rdk-HardwareLib.qt
  Nmsdk-MotionControlLib.qt
  Nmsdk-PulseLib.qt
  Qt5::Core Qt5::Network Qt5::Sql Qt5::Xml Qt5::SerialPort
)

find_package(CURL QUIET)
if(CURL_FOUND)
  target_link_libraries(NeuroModelerConsole PRIVATE CURL::libcurl)
endif()


