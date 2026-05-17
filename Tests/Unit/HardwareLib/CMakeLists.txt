add_executable(Test_ArduinoHardwareLib Test_ArduinoHardwareLib.cpp)

target_link_libraries(Test_ArduinoHardwareLib PRIVATE
  Rdk-HardwareLib.qt
  GTest::gtest
  GTest::gtest_main
  Nmsdk::Qt::Core
)

add_executable(Test_ArduinoComponentGuiRegistry Test_ArduinoComponentGuiRegistry.cpp)

target_sources(Test_ArduinoComponentGuiRegistry PRIVATE
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentFormRegistry.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UVisualControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGenericComponentControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGuiTelemetry.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include/RdkDummyLibraries.cpp
)

target_compile_definitions(Test_ArduinoComponentGuiRegistry PRIVATE RDK_QT RDK_LIB_TYPE= RDK_CALL=)

target_include_directories(Test_ArduinoComponentGuiRegistry PRIVATE
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt
)

target_link_libraries(Test_ArduinoComponentGuiRegistry PRIVATE
  Rdk-HardwareLib.gui
  rdk.static.qt
  GTest::gtest
  GTest::gtest_main
  Nmsdk::Qt::Widgets
  Nmsdk::Qt::Gui
)

include(GoogleTest)
add_executable(Test_ArduinoBoardEdges Test_ArduinoBoardEdges.cpp)

target_sources(Test_ArduinoBoardEdges PRIVATE
  ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include/RdkDummyLibraries.cpp
)

target_compile_definitions(Test_ArduinoBoardEdges PRIVATE RDK_LIB_TYPE= RDK_CALL=)

target_link_libraries(Test_ArduinoBoardEdges PRIVATE
  Rdk-HardwareLib.qt
  rdk.static.qt
  GTest::gtest
  GTest::gtest_main
  Nmsdk::Qt::Core
)

gtest_discover_tests(Test_ArduinoHardwareLib)
gtest_discover_tests(Test_ArduinoBoardEdges)
gtest_discover_tests(Test_ArduinoComponentGuiRegistry)
