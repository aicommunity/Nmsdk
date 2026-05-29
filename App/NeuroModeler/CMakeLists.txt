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
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UMatrixFormDialog.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UVisualControllerMainWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatch.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UProjectDescriptionWindow.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChart.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChartView.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChartOption.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchSerie.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchSeriesOption.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchTab.cpp
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
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UMarkdownViewerWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UMarkdownWebEnginePage.cpp
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
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Llm/RegisterPulseLibLlmTools.cpp
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Llm/RegisterMotionControlLibLlmTools.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/LlmGuiBootstrap.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmGuiLocale.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmQtProviderSettingsSource.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmProviderSettingsWidget.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/Llm/ULlmAssistantDockWidget.cpp
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
    Nmsdk::Qt::Print
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

find_package(CURL QUIET)
if(CURL_FOUND)
  target_link_libraries(NeuroModeler PRIVATE CURL::libcurl)
endif()

# Google glog for logging (same as in Rdk/CMakeLists.txt)
find_package(glog QUIET)
if(NOT glog_FOUND)
  find_path(GLOG_INCLUDE_DIR glog/logging.h
    PATHS
      /usr/include
      /usr/local/include
      /opt/homebrew/include
  )
  find_library(GLOG_LIBRARY
    NAMES glog
    PATHS
      /usr/lib
      /usr/local/lib
      /opt/homebrew/lib
  )
  if(GLOG_INCLUDE_DIR AND GLOG_LIBRARY)
    add_library(glog::glog UNKNOWN IMPORTED)
    set_target_properties(glog::glog PROPERTIES
      IMPORTED_LOCATION "${GLOG_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${GLOG_INCLUDE_DIR}"
    )
    set(glog_FOUND TRUE)
  endif()
endif()
if(glog_FOUND)
  target_link_libraries(NeuroModeler PRIVATE glog::glog)
endif()

# Boost libraries (required by rdk.static.qt)
# Use MODULE mode on all platforms (FindBoost.cmake correctly determines library names)
find_package(Boost QUIET COMPONENTS program_options thread filesystem system chrono atomic)
if(Boost_FOUND)
  # Use modern targets if available, otherwise fall back to variables
  if(TARGET Boost::program_options)
    target_link_libraries(NeuroModeler PRIVATE
      Boost::program_options
      Boost::thread
      Boost::filesystem
      Boost::system
      Boost::chrono
      Boost::atomic
    )
  else()
    # Fallback to the legacy approach if targets are not available
    target_link_libraries(NeuroModeler PRIVATE ${Boost_LIBRARIES})
    target_include_directories(NeuroModeler PRIVATE ${Boost_INCLUDE_DIRS})
  endif()
endif()

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
  $<$<BOOL:${glog_FOUND}>:RDK_USE_GLOG>
)

# Optional dependencies
if (RDK_USE_OPENCV AND OpenCV_FOUND)
  target_link_libraries(NeuroModeler PRIVATE ${OpenCV_LIBS})
endif()

# Copy style files to the output directory
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

# Copy help files to the output directory
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

# Include function for deploying DLLs from vcpkg
include(${CMAKE_SOURCE_DIR}/cmake/DeployVcpkgDlls.cmake)

# Deploy all required DLLs from vcpkg
deploy_vcpkg_dlls(NeuroModeler)

# Copy Qt WebEngine files to the output directory (Windows only)
# Qt WebEngine requires QtWebEngineProcess.exe and other files to work
if(WIN32 AND RDK_USE_QT_WEBENGINE AND Qt5WebEngineWidgets_FOUND)
    # Get the Qt path from vcpkg or a local installation
    get_target_property(QT_QMAKE_EXECUTABLE Qt5::qmake IMPORTED_LOCATION)
    if(QT_QMAKE_EXECUTABLE)
        get_filename_component(QT_BIN_DIR "${QT_QMAKE_EXECUTABLE}" DIRECTORY)

        # Also check the path from vcpkg_installed
        if(EXISTS "${CMAKE_BINARY_DIR}/vcpkg_installed/${VCPKG_TARGET_TRIPLET}/bin")
            set(_vcpkg_bin_dir "${CMAKE_BINARY_DIR}/vcpkg_installed/${VCPKG_TARGET_TRIPLET}/bin")
            set(_vcpkg_debug_bin_dir "${CMAKE_BINARY_DIR}/vcpkg_installed/${VCPKG_TARGET_TRIPLET}/debug/bin")
        endif()

        # List of possible paths to QtWebEngineProcess.exe (release)
        set(_webengine_process_paths
            "${QT_BIN_DIR}/QtWebEngineProcess.exe"
            "${QT_BIN_DIR}/../tools/qt5/bin/QtWebEngineProcess.exe"
        )
        if(DEFINED _vcpkg_bin_dir)
            list(APPEND _webengine_process_paths
                "${_vcpkg_bin_dir}/QtWebEngineProcess.exe"
                "${_vcpkg_bin_dir}/../tools/qt5/bin/QtWebEngineProcess.exe"
            )
        endif()

        # Search for and copy the release version
        set(_found_release FALSE)
        foreach(_path IN LISTS _webengine_process_paths)
            if(EXISTS "${_path}")
                add_custom_command(TARGET NeuroModeler POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different
                        "${_path}"
                        "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/QtWebEngineProcess.exe"
                    COMMENT "Copying QtWebEngineProcess.exe from ${_path}"
                )
                set(_found_release TRUE)
                break()
            endif()
        endforeach()
        if(NOT _found_release)
            message(WARNING "QtWebEngineProcess.exe not found. Checked: ${_webengine_process_paths}")
        endif()

        # List of possible paths to QtWebEngineProcessd.exe (debug)
        get_filename_component(QT_ROOT_DIR "${QT_BIN_DIR}" DIRECTORY)
        set(_webengine_processd_paths
            # Typical location for system Qt 5.15.2 on Windows
            "${QT_BIN_DIR}/QtWebEngineProcessd.exe"
            # Alternative layouts (debug/tools), including vcpkg Qt5
            "${QT_ROOT_DIR}/debug/bin/QtWebEngineProcessd.exe"
            "${QT_BIN_DIR}/../debug/bin/QtWebEngineProcessd.exe"
            "${QT_ROOT_DIR}/tools/qt5/bin/QtWebEngineProcessd.exe"
        )
        if(DEFINED _vcpkg_debug_bin_dir)
            list(APPEND _webengine_processd_paths
                "${_vcpkg_debug_bin_dir}/QtWebEngineProcessd.exe"
                "${_vcpkg_debug_bin_dir}/../tools/qt5/bin/QtWebEngineProcessd.exe"
            )
        endif()

        # Search for and copy the debug version
        set(_found_debug FALSE)
        foreach(_path IN LISTS _webengine_processd_paths)
            if(EXISTS "${_path}")
                add_custom_command(TARGET NeuroModeler POST_BUILD
                    COMMAND ${CMAKE_COMMAND} -E copy_if_different
                        "${_path}"
                        "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/QtWebEngineProcessd.exe"
                    COMMENT "Copying QtWebEngineProcessd.exe from ${_path}"
                )
                set(_found_debug TRUE)
                break()
            endif()
        endforeach()
        if(NOT _found_debug)
            message(WARNING "QtWebEngineProcessd.exe not found. Checked: ${_webengine_processd_paths}")
        endif()

        # Copy the resources directory (if it exists)
        get_filename_component(QT_ROOT_DIR "${QT_BIN_DIR}" DIRECTORY)
        set(QT_RESOURCES_DIR "${QT_ROOT_DIR}/resources")
        if(EXISTS "${QT_RESOURCES_DIR}")
            add_custom_command(TARGET NeuroModeler POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_directory
                    "${QT_RESOURCES_DIR}"
                    "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/resources"
                COMMENT "Copying Qt WebEngine resources to output directory"
            )
        endif()

        # Copy the translations/qtwebengine_locales directory (if it exists)
        set(QT_TRANSLATIONS_DIR "${QT_ROOT_DIR}/translations")
        if(EXISTS "${QT_TRANSLATIONS_DIR}")
            add_custom_command(TARGET NeuroModeler POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/translations"
                COMMAND ${CMAKE_COMMAND} -E copy_directory
                    "${QT_TRANSLATIONS_DIR}"
                    "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/translations"
                COMMENT "Copying Qt WebEngine translations to output directory"
            )
        endif()
    else()
        message(WARNING "Cannot find Qt5::qmake to locate Qt WebEngine files")
    endif()
endif()

# rdk.llm.embedded after other libs so EnsureEmbeddedLlamaProviderRegistered resolves.
if(RDK_USE_LLM AND RDK_LLM_BUILD_EMBEDDED)
  target_link_libraries(NeuroModeler PRIVATE rdk.llm.embedded)
endif()
