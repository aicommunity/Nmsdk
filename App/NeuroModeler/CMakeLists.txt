cmake_minimum_required(VERSION 3.16)
project(NeuroModeler LANGUAGES CXX)

# Подключаем функцию для получения версии из Git
include(${CMAKE_SOURCE_DIR}/cmake/GetGitVersion.cmake)

# Получаем версию из Git
get_git_version(GIT_VERSION_STRING)

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

# Настройка Qt из vcpkg (должно быть ДО find_package(Qt5))
# Это гарантирует использование Qt только из vcpkg
if(EXISTS "${CMAKE_SOURCE_DIR}/cmake/ForceQtFromVcpkg.cmake")
    include("${CMAKE_SOURCE_DIR}/cmake/ForceQtFromVcpkg.cmake")
endif()

find_package(Qt5 REQUIRED COMPONENTS Core Widgets Gui Network PrintSupport Charts Sql Xml SerialPort Concurrent)

# Включаем AUTOUIC для автоматической обработки .ui файлов
set(CMAKE_AUTOUIC ON)

target_sources(NeuroModeler PRIVATE
  ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/static/res.qrc
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/USettingsReaderWidget.h
  ${CMAKE_SOURCE_DIR}/App/NeuroModeler/main.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UAboutDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UHelpWindow.cpp
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
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentsListWidgetModern.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentsListWidgetModern.ui
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UBreadcrumbsWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UVisualControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramContainerWidget.cpp
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
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UStyleManager.cpp
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

# Передаем версию из Git в определение компилятора
# CMake автоматически экранирует строку для передачи в препроцессор
# Формат: RDK_APP_VERSION="1.2.1.0 (develop:b4ff447)"
target_compile_definitions(NeuroModeler PRIVATE 
  RDK_DISABLE_EXT_GUI 
  QT_DLL 
  QT_WIDGETS_LIB 
  RDK_APP_VERSION="${GIT_VERSION_STRING}"
)

target_link_libraries(NeuroModeler PRIVATE
  Qt5::Core Qt5::Widgets Qt5::Gui Qt5::Network Qt5::PrintSupport Qt5::Charts Qt5::Sql Qt5::Xml Qt5::SerialPort Qt5::Concurrent
  rdk.static.qt
  Rdk-BasicLib.qt
)

# Опциональные зависимости
if (RDK_USE_OPENCV AND OpenCV_FOUND)
  target_link_libraries(NeuroModeler PRIVATE ${OpenCV_LIBS})
endif()

# Copy style files to output directory
set(STYLES_SOURCE_DIR "${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Styles")
set(STYLES_DEST_DIR "${CMAKE_SOURCE_DIR}/Bin/Styles")

add_custom_command(TARGET NeuroModeler POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${STYLES_DEST_DIR}"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${STYLES_SOURCE_DIR}/default.qss"
        "${STYLES_DEST_DIR}/default.qss"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${STYLES_SOURCE_DIR}/theme.json"
        "${STYLES_DEST_DIR}/theme.json"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${STYLES_SOURCE_DIR}/dark.qss"
        "${STYLES_DEST_DIR}/dark.qss"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${STYLES_SOURCE_DIR}/dark-theme.json"
        "${STYLES_DEST_DIR}/dark-theme.json"
    COMMENT "Copying style files to Bin/Styles/"
)

# Copy help files to output directory
set(HELP_SOURCE_DIR "${CMAKE_SOURCE_DIR}/Bin/Help")
set(HELP_DEST_DIR "${CMAKE_SOURCE_DIR}/Bin/Help")

add_custom_command(TARGET NeuroModeler POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${HELP_DEST_DIR}/en"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${HELP_DEST_DIR}/ru"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${HELP_DEST_DIR}/styles"
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${HELP_SOURCE_DIR}/en"
        "${HELP_DEST_DIR}/en"
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${HELP_SOURCE_DIR}/ru"
        "${HELP_DEST_DIR}/ru"
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${HELP_SOURCE_DIR}/styles"
        "${HELP_DEST_DIR}/styles"
    COMMENT "Copying help files to Bin/Help/"
)

