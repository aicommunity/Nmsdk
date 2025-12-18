cmake_minimum_required(VERSION 3.16)
project(NeuroModeler LANGUAGES CXX)

# Для Qt GUI приложения на Windows нужен subsystem:windows
if(WIN32)
  add_executable(NeuroModeler WIN32)
else()
  add_executable(NeuroModeler)
endif()

# Устанавливаем DLL runtime библиотеку для совместимости с vcpkg
if(MSVC)
  # Используем генератор выражений для multi-config генераторов (Visual Studio)
  set_target_properties(NeuroModeler PROPERTIES
    MSVC_RUNTIME_LIBRARY "$<IF:$<CONFIG:Debug>,MultiThreadedDebugDLL,MultiThreadedDLL>"
  )
endif()

find_package(Qt5 REQUIRED COMPONENTS Core Widgets Gui Network PrintSupport Charts Sql Xml SerialPort Concurrent)

target_sources(NeuroModeler PRIVATE
  ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/static/res.qrc
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/USettingsReaderWidget.h
  ${CMAKE_SOURCE_DIR}/App/NeuroModeler/main.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UAboutDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGEngineControlWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UMatrixFormDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UVisualControllerMainWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatch.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChart.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChartView.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChartOption.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchSerie.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchSeriesOption.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchTab.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentsListWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UVisualControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UDrawEngineWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UDrawEngineImageWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UClassesListWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentLinksWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UImagesWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/USingleImageWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentPropertySelectionWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UPropertyXMLWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UCalculationChannelsWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UEngineControlQt.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGuiTelemetry.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGuiModelSnapshot.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/ULoggerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UCreateConfigurationWizardWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UImageLoader.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UCreateTestWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentPropertyChanger.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UStatusPanel.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/USingleImagePainter.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/qcustomplot.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGraphWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGraphControlDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGraphPaintWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UTableInfo.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchFormWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchSettingsDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UTcpServerControlWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UCurlFtpClientTestWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UClassDescriptionDisplay.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UClDescEditor.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UClassFavoritesEditor.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/USingleClassListWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UQuickLinkDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramWidget.cpp
)

# DEFINES из оригинального .pro
target_compile_definitions(NeuroModeler
  PRIVATE
    QT_DLL
    QT_WIDGETS_LIB
    RDK_DISABLE_EXT_GUI
)

# Подключаем заголовок со строковыми макросами (разный синтаксис для MSVC/GCC)
if (MSVC)
  target_compile_options(NeuroModeler PRIVATE /FI${CMAKE_SOURCE_DIR}/App/NeuroModeler/NeuroModelerAppDefs.h)
else()
  target_compile_options(NeuroModeler PRIVATE -include ${CMAKE_SOURCE_DIR}/App/NeuroModeler/NeuroModelerAppDefs.h)
endif()

target_link_libraries(NeuroModeler
  PRIVATE
    Qt5::Core Qt5::Widgets Qt5::Gui Qt5::Network Qt5::PrintSupport Qt5::Charts Qt5::Sql Qt5::Xml Qt5::SerialPort Qt5::Concurrent
    $<$<PLATFORM_ID:Windows>:Qt5::WinMain>
    Rdk-CvBasicLib.qt
    Rdk-BasicLib.qt
    Rdk-HardwareLib.qt
    Nmsdk-PulseLib.qt
    Nmsdk-MotionControlLib.qt
    rdk.static.qt
)

find_package(CURL QUIET)
if(CURL_FOUND)
  target_link_libraries(NeuroModeler PRIVATE CURL::libcurl)
endif()

# Boost libraries (required by rdk.static.qt)
find_package(Boost QUIET COMPONENTS program_options thread filesystem system chrono atomic)
if(Boost_FOUND)
  target_link_libraries(NeuroModeler PRIVATE 
    Boost::program_options 
    Boost::thread 
    Boost::filesystem 
    Boost::system
    Boost::chrono
    Boost::atomic
  )
endif()

target_include_directories(NeuroModeler PRIVATE
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt
  ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
  ${CMAKE_SOURCE_DIR}/Rdk/Core/Graphics
)

target_compile_definitions(NeuroModeler PRIVATE RDK_DISABLE_EXT_GUI QT_DLL QT_WIDGETS_LIB RDK_APP_VERSION=0)

target_link_libraries(NeuroModeler PRIVATE
  Qt5::Core Qt5::Widgets Qt5::Gui Qt5::Network Qt5::PrintSupport Qt5::Charts Qt5::Sql Qt5::Xml Qt5::SerialPort Qt5::Concurrent
  rdk.static.qt
  Rdk-BasicLib.qt
)

# Опциональные зависимости
if (RDK_USE_OPENCV AND OpenCV_FOUND)
  target_link_libraries(NeuroModeler PRIVATE ${OpenCV_LIBS})
endif()


