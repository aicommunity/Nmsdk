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
  Nmsdk-MotionControlLib.qt
  Nmsdk-PulseLib.qt
  Nmsdk::Qt::Core
  Nmsdk::Qt::Network
  Nmsdk::Qt::Sql
  Nmsdk::Qt::Xml
  Nmsdk::Qt::Concurrent
)

find_package(CURL QUIET)
if(CURL_FOUND)
  target_link_libraries(NeuroModelerConsole PRIVATE CURL::libcurl)
endif()

# Boost libraries (required by rdk.static.qt)
# Use MODULE mode on all platforms (FindBoost.cmake correctly determines library names)
find_package(Boost QUIET COMPONENTS program_options thread filesystem system chrono atomic)
if(Boost_FOUND)
  # Use modern targets if available, otherwise fall back to variables
  if(TARGET Boost::program_options)
    target_link_libraries(NeuroModelerConsole PRIVATE
      Boost::program_options
      Boost::thread
      Boost::filesystem
      Boost::system
      Boost::chrono
      Boost::atomic
    )
  else()
    # Fallback to the legacy approach if targets are not available
    target_link_libraries(NeuroModelerConsole PRIVATE ${Boost_LIBRARIES})
    target_include_directories(NeuroModelerConsole PRIVATE ${Boost_INCLUDE_DIRS})
  endif()
endif()


