cmake_minimum_required(VERSION 3.14)
project(NeuroModeler VERSION 1.1.3.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt5 REQUIRED COMPONENTS Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Gui Widgets Network Sql Xml SerialPort PrintSupport Charts)

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
    -DRDK_DISABLE_EXT_GUI
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

set(RESOURCES ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/static/res.qrc)

set(SOURCES
    ${CMAKE_SOURCE_DIR}/../../../Libraries/Libraries.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UAboutDialog.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGEngineControlWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UMatrixFormDialog.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UVisualControllerMainWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatch.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchChart.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchChartView.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchChartOption.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchSerie.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchSeriesOption.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchTab.cpp
    ${CMAKE_SOURCE_DIR}/main.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentsListWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UVisualControllerWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UDrawEngineWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UDrawEngineImageWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClassesListWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentLinksWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UImagesWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/USingleImageWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentPropertySelectionWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UPropertyXMLWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCalculationChannelsWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UEngineControlQt.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/ULoggerWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCreateConfigurationWizardWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UImageLoader.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCreateTestWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentPropertyChanger.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UStatusPanel.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/USingleImagePainter.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/qcustomplot.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGraphWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGraphControlDialog.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGraphPaintWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UTableInfo.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchFormWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchSettingsDialog.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UTcpServerControlWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCurlFtpClientTestWidget.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClassDescriptionDisplay.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClDescEditor.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClassFavoritesEditor.cpp
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/USingleClassListWidget.cpp
)

set(HEADERS
    ${CMAKE_SOURCE_DIR}/../../../Libraries/Libraries.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UAboutDialog.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentsListWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGEngineControlWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UMatrixFormDialog.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UVisualControllerMainWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UVisualControllerWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UDrawEngineWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UDrawEngineImageWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClassesListWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentLinksWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UImagesWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/USingleImageWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentPropertySelectionWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UPropertyXMLWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCalculationChannelsWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UEngineControlQt.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/ULoggerWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCreateConfigurationWizardWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/USingleImagePainter.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UImageLoader.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCreateTestWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentPropertyChanger.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UStatusPanel.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/USettingsReaderWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatch.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchChart.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchChartView.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchChartOption.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchSerie.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchSeriesOption.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchTab.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/qcustomplot.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGraphWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UStructSingleGraph.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGraphControlDialog.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGraphPaintWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UTableInfo.h
    ${CMAKE_SOURCE_DIR}/UWatchWidgetForm.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchFormWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchSettingsDialog.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UTcpServerControlWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCurlFtpClientTestWidget.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClassDescriptionDisplay.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClDescEditor.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClassFavoritesEditor.h
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/USingleClassListWidget.h
)

set(FORMS
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UAboutDialog.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentsListWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGEngineControllWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UDrawEngineWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClassesListWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentLinksWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UImagesWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UMatrixFormDialog.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/USingleImageWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentPropertySelectionWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UPropertyXMLWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCalculationChannelsWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCreateConfigurationWizardWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCreateTestWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UComponentPropertyChanger.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UStatusPanel.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGraphWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGraphControlDialog.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UGraphPaintWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UTableInfo.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatch.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchChart.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchChartOption.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchFormWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchSeriesOption.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchSettingsDialog.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UTcpServerControlWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UCurlFtpClientTestWidget.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UWatchTab.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClassDescriptionDisplay.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClDescEditor.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/UClassFavoritesEditor.ui
    ${CMAKE_SOURCE_DIR}/../../../Rdk/GUI/Qt/USingleClassListWidget.ui
)

add_executable(NeuroModeler)

target_link_libraries(NeuroModeler PRIVATE
    Qt5::Core
    Qt5::Gui
    Qt5::Widgets
    Qt5::Network
    Qt5::Sql
    Qt5::Xml
    Qt5::SerialPort
    Qt5::PrintSupport
    Qt5::Charts
)

if(WIN32)
    target_link_libraries(NeuroModeler PRIVATE
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
#        target_link_libraries(NeuroModeler PRIVATE ${CMAKE_SOURCE_DIR}/../../../Bin/Platform/Win/Lib.Qt/${lib}.qt.lib)
    else()
#        target_link_libraries(NeuroModeler PRIVATE ${CMAKE_SOURCE_DIR}/../../../Bin/Platform/Linux/Lib.Qt/lib${lib}.qt.a)
    endif()
endforeach()

# Подключение OpenCV, Boost, Darknet, TensorFlow, MATLAB (если определены)
if(DEFINED RDK_USE_OPENCV)
    if(WIN32)
        target_link_libraries(NeuroModeler PRIVATE ${OPENCV_WIN_LINKER_LINE})
    else()
        target_link_libraries(NeuroModeler PRIVATE ${OPENCV_UNIX_LINKER_LINE})
    endif()
endif()

if(WIN32)
    target_link_libraries(NeuroModeler PRIVATE ${BOOST_WIN_LINKER_LINE})
else()
    target_link_libraries(NeuroModeler PRIVATE ${BOOST_UNIX_LINKER_LINE})
endif()

if(DEFINED RDK_USE_DARKNET AND UNIX)
    target_link_libraries(NeuroModeler PRIVATE ${DARKNET_UNIX_LINKER_LINE})
endif()

if(DEFINED RDK_USE_TENSORFLOW)
    if(WIN32)
        target_link_libraries(NeuroModeler PRIVATE ${TENSORFLOW_WIN_LINKER_LINE})
    else()
        target_link_libraries(NeuroModeler PRIVATE ${TENSORFLOW_UNIX_LINKER_LINE})
    endif()
endif()

if(DEFINED RDK_USE_MATLAB)
    if(WIN32)
        target_link_libraries(NeuroModeler PRIVATE ${MATLAB_WIN_LINKER_LINE})
    else()
        target_link_libraries(NeuroModeler PRIVATE ${MATLAB_UNIX_LINKER_LINE})
    endif()
endif()
