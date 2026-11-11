cmake_minimum_required(VERSION 3.16)
project(NeuroModeler LANGUAGES CXX)

# Include helper function to get version from Git
include(${CMAKE_SOURCE_DIR}/cmake/GetGitVersion.cmake)

# Obtain version string from Git
get_git_version(GIT_VERSION_STRING)

# For a Qt GUI application on Windows we need subsystem:windows
if(WIN32)
  add_executable(NeuroModeler WIN32)
else()
  add_executable(NeuroModeler)
endif()

# Set DLL runtime library for compatibility with vcpkg
# Enable AUTOUIC at the target level to avoid conflicts with global settings
# This is especially important on Windows, where duplicate rule issues may appear
if(MSVC)
  # Use generator expressions for multi-config generators (Visual Studio)
  set_target_properties(NeuroModeler PROPERTIES
    MSVC_RUNTIME_LIBRARY "$<IF:$<CONFIG:Debug>,MultiThreadedDebugDLL,MultiThreadedDLL>"
    AUTOUIC ON
  )
else()
  set_target_properties(NeuroModeler PROPERTIES
    AUTOUIC ON
  )
endif()

# Configure Qt (Qt5/Qt6) via shared module
include(${CMAKE_SOURCE_DIR}/cmake/SelectQt.cmake)

# Qt WebEngine is optional: if absent, the description is shown via QTextEdit::setMarkdown()
set(RDK_USE_QT_WEBENGINE 0)
if(NMSDK_QT_WEBENGINE_AVAILABLE)
  set(RDK_USE_QT_WEBENGINE 1)
endif()

# Enable AUTOMOC for automatic handling of Q_OBJECT classes
set(CMAKE_AUTOMOC ON)

# Use a relative path to the UI file
# AUTOUIC is disabled for MarkdownMermaidTest, so there will be no duplication
set(UI_FILE_NORMALIZED "${CMAKE_CURRENT_SOURCE_DIR}/../../Rdk/GUI/Qt/UComponentsListWidgetModern.ui")
# Normalize the path for consistency
get_filename_component(UI_FILE_NORMALIZED "${UI_FILE_NORMALIZED}" ABSOLUTE)

target_sources(NeuroModeler PRIVATE
  ${CMAKE_SOURCE_DIR}/Libraries/Libraries.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/static/res.qrc
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/USettingsReaderWidget.h
  ${CMAKE_SOURCE_DIR}/App/NeuroModeler/main.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UAboutDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UHelpWindow.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentFormRegistry.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentGuiService.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentGuiDndPayload.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentGuiTabHostWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGenericComponentControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentGuiBootstrap.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGEngineControlWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UGuiShellController.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UEngineControlStripWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UMatrixFormDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UVisualControllerMainWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatch.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UProjectDescriptionWindow.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChart.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChartView.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchSerie.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchTab.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Plot/PlotDocument.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Plot/PlotDataAdapter.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Plot/PlotSettingsSidePanel.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Plot/PlotSurface.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Plot/UWatchLayoutDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Plot/UWatchMatrixSelector.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Plot/UWatchSourcePickerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Plot/UWatchSeriesWizard.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Plot/WatchPresetCatalog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentsListWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentsListWidgetModern.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UEngineSelectionSync.cpp
  ${UI_FILE_NORMALIZED}
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
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UTableInfo.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UTcpServerControlWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UCurlFtpClientTestWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UClassDescriptionDisplay.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UClDescEditor.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UClassFavoritesEditor.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/USingleClassListWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UQuickLinkDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UMarkdownViewerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UMarkdownDocWindow.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramScene.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramView.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramLinkItem.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramNodeItem.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramViewportManager.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramCoordinateManager.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramCacheManager.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramPortManager.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramTooltipGenerator.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramContextMenu.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UStyleManager.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/GUI/Qt/MotionControlComponentGuiRegistration.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/GUI/Qt/MotionControlComponentControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/GUI/Qt/MotionControlManipulatorComponentControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/GUI/Qt/MotionControlAstaticGyroComponentControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/GUI/Qt/MotionControlNewPositionControlElementControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/GUI/Qt/PulseLibComponentGuiRegistration.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/GUI/Qt/PulseLibComponentControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/GUI/Qt/PulseLibNeuronTrainerComponentControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/GUI/Qt/PulseLibNeuronLearnerComponentControllerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/GUI/Qt/BasicLibComponentGuiRegistration.cpp
  ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/GUI/Qt/CvBasicLibComponentGuiRegistration.cpp
)

if(RDK_USE_QT_WEBENGINE)
  # A conditional Q_OBJECT header must only enter AUTOMOC when enabled.
  # Keeping its disabled, empty moc output in the graph can leave stale output
  # when WebEngine is subsequently enabled in the same build tree.
  target_sources(NeuroModeler PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UMarkdownWebEnginePage.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UMarkdownWebEnginePage.h)
endif()

# Explicitly state that the UI file must be processed only once
# This prevents duplicate generation rules on Windows
# Important: this must come AFTER target_sources but BEFORE other commands
# Explicitly enable AUTOUIC for the UI file to guarantee its processing
set_source_files_properties(${UI_FILE_NORMALIZED} PROPERTIES
  AUTOUIC ON
)

# DEFINES from the original .pro file
target_compile_definitions(NeuroModeler
  PRIVATE
    QT_DLL
    QT_WIDGETS_LIB
    RDK_DISABLE_EXT_GUI
)

# Include header with string macros (different syntax for MSVC/GCC)
if (MSVC)
  target_compile_options(NeuroModeler PRIVATE /FI${CMAKE_SOURCE_DIR}/App/NeuroModeler/NeuroModelerAppDefs.h)
else()
  target_compile_options(NeuroModeler PRIVATE -include ${CMAKE_SOURCE_DIR}/App/NeuroModeler/NeuroModelerAppDefs.h)
endif()

if(RDK_USE_LLM)
  target_sources(NeuroModeler PRIVATE
    ${CMAKE_SOURCE_DIR}/App/NeuroModeler/NmsdkBuiltinKnowledgeCatalog.cpp
    ${CMAKE_SOURCE_DIR}/App/NeuroModeler/NmsdkLlmProjectContext.cpp
    ${CMAKE_SOURCE_DIR}/App/NeuroModeler/NmsdkRegisterLlm.cpp
    ${CMAKE_SOURCE_DIR}/App/NeuroModeler/NmsdkLlmSettings.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-HardwareLib/Llm/RegisterHardwareLibLlmTools.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Llm/RegisterBasicLibLlmTools.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Llm/UPackBasicDocs.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Llm/RegisterCvBasicLibLlmTools.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Llm/UPackCvBasicDocs.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Llm/RegisterPulseLibLlmTools.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Llm/UPackPulseDocs.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Llm/RegisterMotionControlLibLlmTools.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/LlmGuiBootstrap.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmGuiLocale.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmQtProviderSettingsSource.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmProviderSettingsWidget.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmAssistantDockWidget.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmChatInputCompleter.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmChatMarkdown.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmDetailsHtml.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmCollapsibleDetailsWidget.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmChatHistoryPanel.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmChatHistoryArchive.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmChatHistoryDialog.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmChangePreviewWidget.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmGuiContextBridge.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmQtPresentationSink.cpp
  )
  target_compile_definitions(NeuroModeler PRIVATE RDK_USE_LLM=1)
  target_include_directories(NeuroModeler PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/LLM/Core
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm
  )
  target_link_libraries(NeuroModeler PRIVATE rdk.llm.core)
  if(RDK_LLM_BUILD_EMBEDDED)
    target_include_directories(NeuroModeler PRIVATE ${CMAKE_SOURCE_DIR}/Rdk/LLM/Embedded)
    target_compile_definitions(NeuroModeler PRIVATE RDK_LLM_EMBEDDED=1)
  endif()
endif()

target_link_libraries(NeuroModeler
  PRIVATE
    Nmsdk::Qt::Core
    Nmsdk::Qt::Widgets
    Nmsdk::Qt::Gui
    Nmsdk::Qt::Network
    Nmsdk::Qt::Charts
    Nmsdk::Qt::Svg
    Nmsdk::Qt::Sql
    Nmsdk::Qt::Xml
    Nmsdk::Qt::Concurrent
    Nmsdk::Qt::Test
    Nmsdk::Qt::WebEngineWidgets
    Nmsdk::Qt::CoreCompat
    Rdk-CvBasicLib.qt
    Rdk-BasicLib.qt
    Rdk-HardwareLib.qt
    Rdk-HardwareLib.gui
    Nmsdk-PulseLib.qt
    Nmsdk-MotionControlLib.qt
    rdk.static.qt
)

target_include_directories(NeuroModeler PRIVATE
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt
  ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
  ${CMAKE_SOURCE_DIR}/Rdk/Core/Graphics
)

# Pass version from Git into a compiler definition
# CMake automatically escapes the string when passing it to the preprocessor
# Format: RDK_APP_VERSION="1.2.1.0 (develop:b4ff447)"
target_compile_definitions(NeuroModeler PRIVATE
  RDK_DISABLE_EXT_GUI
  QT_DLL
  QT_WIDGETS_LIB
  RDK_APP_VERSION="${GIT_VERSION_STRING}"
  $<$<BOOL:${RDK_USE_QT_WEBENGINE}>:RDK_USE_QT_WEBENGINE>
)

# Optional dependencies
if (RDK_USE_OPENCV AND OpenCV_FOUND)
  target_link_libraries(NeuroModeler PRIVATE ${OpenCV_LIBS})
endif()

# App-local styles and shared help preserve the GUI's existing lookup rules
# with isolated runtime/<configuration> output directories.
add_custom_command(TARGET NeuroModeler POST_BUILD
  COMMAND "${CMAKE_COMMAND}" -E copy_directory
    "${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Styles" "$<TARGET_FILE_DIR:NeuroModeler>/Styles"
  COMMAND "${CMAKE_COMMAND}" -E copy_directory
    "${CMAKE_SOURCE_DIR}/Bin/Help" "$<TARGET_FILE_DIR:NeuroModeler>/../Help"
  VERBATIM COMMENT "Deploy application styles and help")

# Include function for deploying DLLs from vcpkg
include(${CMAKE_SOURCE_DIR}/cmake/DeployVcpkgDlls.cmake)

# Deploy all required DLLs from vcpkg
deploy_vcpkg_dlls(NeuroModeler)

# rdk.llm.embedded after other libs so EnsureEmbeddedLlamaProviderRegistered resolves.
if(RDK_USE_LLM AND RDK_LLM_BUILD_EMBEDDED)
  target_link_libraries(NeuroModeler PRIVATE rdk.llm.embedded)
endif()
