cmake_minimum_required(VERSION 3.16)
project(NeuroModelerConsole LANGUAGES CXX)

add_executable(NeuroModelerConsole)

# Set DLL runtime library for compatibility with vcpkg
if(MSVC)
  # Use generator expressions for multi-config generators (Visual Studio)
  set_target_properties(NeuroModelerConsole PROPERTIES
    MSVC_RUNTIME_LIBRARY "$<IF:$<CONFIG:Debug>,MultiThreadedDebugDLL,MultiThreadedDLL>"
  )
endif()

target_include_directories(NeuroModelerConsole
  PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Libraries
)

target_sources(NeuroModelerConsole PRIVATE
  ${CMAKE_SOURCE_DIR}/App/NeuroModelerConsole/main.cpp
  ${CMAKE_SOURCE_DIR}/App/NeuroModelerConsole/ClDescGenerator.cpp
  ${CMAKE_SOURCE_DIR}/App/NeuroModelerConsole/PropertyAliasAnalyzer.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/Core/Application/UEngineControl.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/Core/Application/UServerTransportTcp.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/Core/Application/UProjectDeployer.cpp
)

target_compile_definitions(NeuroModelerConsole PRIVATE QT_DLL)

# Configure Qt (Qt5/Qt6) via shared module
include(${CMAKE_SOURCE_DIR}/cmake/SelectQt.cmake)

target_link_libraries(NeuroModelerConsole PRIVATE
  rdk.static.qt
  Rdk-BasicLib.qt
  Rdk-CvBasicLib.qt
  Rdk-HardwareLib.qt
  Rdk-HardwareLib.gui
  Nmsdk-MotionControlLib.qt
  Nmsdk-PulseLib.qt
  Nmsdk::Qt::Core
  Nmsdk::Qt::Network
  Nmsdk::Qt::Sql
  Nmsdk::Qt::Xml
  Nmsdk::Qt::Concurrent
)

# Deploy non-Qt DLLs from vcpkg to Bin/Platform/Win (Qt is from C:\Qt)
include(${CMAKE_SOURCE_DIR}/cmake/DeployVcpkgDlls.cmake)
deploy_vcpkg_dlls(NeuroModelerConsole)


