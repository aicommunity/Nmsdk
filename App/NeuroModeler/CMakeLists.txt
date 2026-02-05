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
# Устанавливаем AUTOUIC на уровне target для предотвращения конфликтов с глобальной настройкой
# Это особенно важно на Windows, где могут возникать проблемы с дублированием правил
if(MSVC)
  # Используем генератор выражений для multi-config генераторов (Visual Studio)
  set_target_properties(NeuroModeler PROPERTIES
    MSVC_RUNTIME_LIBRARY "$<IF:$<CONFIG:Debug>,MultiThreadedDebugDLL,MultiThreadedDLL>"
    AUTOUIC ON
  )
else()
  set_target_properties(NeuroModeler PROPERTIES
    AUTOUIC ON
  )
endif()

# Настройка Qt (Qt5/Qt6) через общий модуль
include(${CMAKE_SOURCE_DIR}/cmake/SelectQt.cmake)

# Qt WebEngine опционален: при отсутствии описание показывается через QTextEdit::setMarkdown()
set(RDK_USE_QT_WEBENGINE 0)
if(NMSDK_QT_WEBENGINE_AVAILABLE)
  set(RDK_USE_QT_WEBENGINE 1)
endif()

# Включаем AUTOMOC для автоматической обработки Q_OBJECT классов
set(CMAKE_AUTOMOC ON)

# Используем относительный путь к UI файлу
# AUTOUIC отключен для MarkdownMermaidTest, поэтому дублирования не будет
set(UI_FILE_NORMALIZED "${CMAKE_CURRENT_SOURCE_DIR}/../../Rdk/GUI/Qt/UComponentsListWidgetModern.ui")
# Нормализуем путь для единообразия
get_filename_component(UI_FILE_NORMALIZED "${UI_FILE_NORMALIZED}" ABSOLUTE)

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
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UProjectDescriptionWindow.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChart.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChartView.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchChartOption.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchSerie.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchSeriesOption.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UWatchTab.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentsListWidget.cpp
  ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UComponentsListWidgetModern.cpp
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
)

# Явно указываем, что UI файл должен обрабатываться только один раз
# Это предотвращает дублирование правил генерации на Windows
# Важно: это должно быть ПОСЛЕ target_sources, но ДО других команд
# Явно включаем AUTOUIC для UI файла, чтобы гарантировать его обработку
set_source_files_properties(${UI_FILE_NORMALIZED} PROPERTIES
  AUTOUIC ON
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
# Используем MODULE режим для всех платформ (FindBoost.cmake правильно определяет имена библиотек)
find_package(Boost QUIET COMPONENTS program_options thread filesystem system chrono atomic)
if(Boost_FOUND)
  # Используем современные target'ы, если доступны, иначе используем переменные
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
    # Fallback на старый способ, если target'ы не доступны
    target_link_libraries(NeuroModeler PRIVATE ${Boost_LIBRARIES})
    target_include_directories(NeuroModeler PRIVATE ${Boost_INCLUDE_DIRS})
  endif()
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
  $<$<BOOL:${RDK_USE_QT_WEBENGINE}>:RDK_USE_QT_WEBENGINE>
  $<$<BOOL:${glog_FOUND}>:RDK_USE_GLOG>
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

# Подключаем функцию развёртывания DLL из vcpkg
include(${CMAKE_SOURCE_DIR}/cmake/DeployVcpkgDlls.cmake)

# Развёртываем все необходимые DLL из vcpkg
deploy_vcpkg_dlls(NeuroModeler)

# Copy Qt WebEngine files to output directory (Windows only)
# Qt WebEngine требует QtWebEngineProcess.exe и другие файлы для работы
if(WIN32 AND RDK_USE_QT_WEBENGINE AND Qt5WebEngineWidgets_FOUND)
    # Получаем путь к Qt из vcpkg или локальной установки
    get_target_property(QT_QMAKE_EXECUTABLE Qt5::qmake IMPORTED_LOCATION)
    if(QT_QMAKE_EXECUTABLE)
        get_filename_component(QT_BIN_DIR "${QT_QMAKE_EXECUTABLE}" DIRECTORY)

        # Также проверяем путь из vcpkg_installed
        if(EXISTS "${CMAKE_BINARY_DIR}/vcpkg_installed/${VCPKG_TARGET_TRIPLET}/bin")
            set(_vcpkg_bin_dir "${CMAKE_BINARY_DIR}/vcpkg_installed/${VCPKG_TARGET_TRIPLET}/bin")
            set(_vcpkg_debug_bin_dir "${CMAKE_BINARY_DIR}/vcpkg_installed/${VCPKG_TARGET_TRIPLET}/debug/bin")
        endif()

        # Список возможных путей к QtWebEngineProcess.exe (release)
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

        # Ищем и копируем release версию
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

        # Список возможных путей к QtWebEngineProcessd.exe (debug)
        get_filename_component(QT_ROOT_DIR "${QT_BIN_DIR}" DIRECTORY)
        set(_webengine_processd_paths
            # Типичное расположение для системного Qt 5.15.2 на Windows
            "${QT_BIN_DIR}/QtWebEngineProcessd.exe"
            # Альтернативные layout'ы (debug/tools), в т.ч. для vcpkg Qt5
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

        # Ищем и копируем debug версию
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

        # Копируем директорию resources (если существует)
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

        # Копируем директорию translations/qtwebengine_locales (если существует)
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
