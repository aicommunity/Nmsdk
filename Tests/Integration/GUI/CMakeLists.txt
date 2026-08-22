cmake_minimum_required(VERSION 3.16)

option(NMSDK_ENABLE_INTERACTIVE_GUI_TESTS
    "Build and run interactive/flaky GUI integration tests"
    OFF)

if(NOT NMSDK_ENABLE_INTERACTIVE_GUI_TESTS)
    message(STATUS "Interactive GUI integration tests are disabled (NMSDK_ENABLE_INTERACTIVE_GUI_TESTS=OFF)")
    return()
endif()

# Test for verifying menu behavior
add_executable(Test_MenuBar Test_MenuBar.cpp)

# Test for verifying QMessageBox::question on Windows
# Use a regular executable (not WIN32), because this is a console test application
add_executable(Test_QMessageBox Test_QMessageBox.cpp)

# Production test — uses Qt from Bin/Platform/<OS> (same DLLs and plugins as the main application)
# Built into DEPLOY_ROOT to use the same Qt binaries
add_executable(Test_QMessageBox_Production Test_QMessageBox_Production.cpp)

# Enable automatic generation of MOC files
set(CMAKE_AUTOMOC ON)
set_target_properties(Test_QMessageBox PROPERTIES AUTOMOC ON)
set_target_properties(Test_QMessageBox_Production PROPERTIES AUTOMOC ON)

# Configure output for the production test into DEPLOY_ROOT
# Use the same settings as for the main application
set_target_properties(Test_QMessageBox_Production PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${DEPLOY_ROOT}"
)

# Find Qt5 or Qt6
find_package(Qt5 COMPONENTS Core Test Widgets REQUIRED)
find_package(Qt6 COMPONENTS Core Test Widgets QUIET)

if(Qt6_FOUND)
    target_link_libraries(Test_MenuBar Qt6::Core Qt6::Test Qt6::Widgets)
    target_link_libraries(Test_QMessageBox Qt6::Core Qt6::Widgets)
    target_link_libraries(Test_QMessageBox_Production Qt6::Core Qt6::Widgets)
    target_compile_definitions(Test_MenuBar PRIVATE QT_VERSION_MAJOR=6)
    target_compile_definitions(Test_QMessageBox PRIVATE QT_VERSION_MAJOR=6)
    target_compile_definitions(Test_QMessageBox_Production PRIVATE QT_VERSION_MAJOR=6)
else()
    target_link_libraries(Test_MenuBar Qt5::Core Qt5::Test Qt5::Widgets)
    target_link_libraries(Test_QMessageBox Qt5::Core Qt5::Widgets)
    # Production test uses the same Qt settings as the main application
    target_link_libraries(Test_QMessageBox_Production Qt5::Core Qt5::Widgets Qt5::Gui)
    target_compile_definitions(Test_MenuBar PRIVATE QT_VERSION_MAJOR=5)
    target_compile_definitions(Test_QMessageBox PRIVATE QT_VERSION_MAJOR=5)
    target_compile_definitions(Test_QMessageBox_Production PRIVATE QT_VERSION_MAJOR=5 QT_DLL QT_WIDGETS_LIB)
endif()

# Add include paths for headers
target_include_directories(Test_MenuBar PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
)

# Test for plugin loading verification
add_executable(Test_PluginLoading test_plugin_loading.cpp)
set_target_properties(Test_PluginLoading PROPERTIES
    AUTOMOC ON
    RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}"
)
if(Qt6_FOUND)
    target_link_libraries(Test_PluginLoading Qt6::Core Qt6::Test)
else()
    target_link_libraries(Test_PluginLoading Qt5::Core Qt5::Test)
    target_compile_definitions(Test_PluginLoading PRIVATE QT_DLL)
endif()

# Test for application startup verification
add_executable(Test_AppStartup test_app_startup.cpp)
set_target_properties(Test_AppStartup PROPERTIES
    AUTOMOC ON
    RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}"
)
if(Qt6_FOUND)
    target_link_libraries(Test_AppStartup Qt6::Core Qt6::Widgets Qt6::Gui Qt6::Test)
else()
    target_link_libraries(Test_AppStartup Qt5::Core Qt5::Widgets Qt5::Gui Qt5::Test)
    target_compile_definitions(Test_AppStartup PRIVATE QT_DLL QT_WIDGETS_LIB)
endif()

# Test for QMessageBox style crash reproduction
add_executable(Test_QMessageBoxStyleCrash test_qmessagebox_style_crash.cpp)
set_target_properties(Test_QMessageBoxStyleCrash PROPERTIES
    AUTOMOC ON
    RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}"
)
if(Qt6_FOUND)
    target_link_libraries(Test_QMessageBoxStyleCrash Qt6::Core Qt6::Widgets Qt6::Gui Qt6::Test)
else()
    target_link_libraries(Test_QMessageBoxStyleCrash Qt5::Core Qt5::Widgets Qt5::Gui Qt5::Test)
    target_compile_definitions(Test_QMessageBoxStyleCrash PRIVATE QT_DLL QT_WIDGETS_LIB)
endif()

# Test for QMessageBox with various style scenarios
add_executable(Test_QMessageBoxWithStyles test_qmessagebox_with_styles.cpp)
set_target_properties(Test_QMessageBoxWithStyles PROPERTIES
    AUTOMOC ON
    RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}"
)
if(Qt6_FOUND)
    target_link_libraries(Test_QMessageBoxWithStyles Qt6::Core Qt6::Widgets Qt6::Gui Qt6::Test)
else()
    target_link_libraries(Test_QMessageBoxWithStyles Qt5::Core Qt5::Widgets Qt5::Gui Qt5::Test)
    target_compile_definitions(Test_QMessageBoxWithStyles PRIVATE QT_DLL QT_WIDGETS_LIB)
endif()

# Register tests in CTest
add_test(NAME MenuBarTest COMMAND Test_MenuBar)
add_test(NAME QMessageBoxTest COMMAND Test_QMessageBox)
add_test(NAME QMessageBoxProductionTest COMMAND Test_QMessageBox_Production)
add_test(NAME PluginLoadingTest COMMAND Test_PluginLoading)
add_test(NAME AppStartupTest COMMAND Test_AppStartup)
add_test(NAME QMessageBoxStyleCrashTest COMMAND Test_QMessageBoxStyleCrash)
add_test(NAME QMessageBoxWithStylesTest COMMAND Test_QMessageBoxWithStyles)

# Find GTest before defining the test that uses it
find_package(GTest QUIET)
if(NOT GTest_FOUND)
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.12.1
    )
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)
endif()

# Find glog for RDK logging
find_package(glog QUIET)
if(NOT glog_FOUND)
    # Try to find glog using pkg-config or standard paths (Unix)
    if(UNIX)
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
    else()
        # On Windows, glog should be found via vcpkg automatically
        # If not found, we'll just define RDK_USE_GLOG and hope it's linked via rdk.static.qt
        message(STATUS "glog not found via find_package, assuming it will be available at link time")
    endif()
endif()

# Test for component movement algorithms
# Compile UModernDiagramWidget files directly into test to avoid MOC conflicts with NeuroModeler
# Use stub implementations for classes not needed in movement tests
add_executable(Test_UModernDiagramWidget_Movement
    Test_UModernDiagramWidget_Movement.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramWidget.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramScene.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramView.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramLinkItem.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramExternalSourceItem.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramNodeItem.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramViewportManager.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramCoordinateManager.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramCacheManager.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramTooltipGenerator.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramContextMenu.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UModernDiagramPortManager.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UStyleManager.cpp
    # Stub implementations to avoid heavy dependencies
    UClassDescriptionDisplay_stub.cpp
    UClassFavoritesEditor_stub.cpp
    UQuickLinkDialog_stub.cpp
    UVisualControllerWidget_stub.cpp
    Libraries_stub.cpp
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include/RdkDummyLibraries.cpp
    # Headers for MOC processing
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UClassDescriptionDisplay.h
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UClassFavoritesEditor.h
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UQuickLinkDialog.h
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt/UVisualControllerWidget.h
)
set_target_properties(Test_UModernDiagramWidget_Movement PROPERTIES
    AUTOMOC ON
    AUTOUIC ON
    AUTORCC ON
)
set_target_properties(Test_UModernDiagramWidget_Movement PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${DEPLOY_ROOT}"
)
if(Qt6_FOUND)
    target_link_libraries(Test_UModernDiagramWidget_Movement Qt6::Core Qt6::Widgets Qt6::Gui Qt6::Test)
    target_compile_definitions(Test_UModernDiagramWidget_Movement PRIVATE QT_VERSION_MAJOR=6)
else()
    target_link_libraries(Test_UModernDiagramWidget_Movement Qt5::Core Qt5::Widgets Qt5::Gui Qt5::Test)
    target_compile_definitions(Test_UModernDiagramWidget_Movement PRIVATE QT_DLL QT_WIDGETS_LIB)
endif()
target_compile_definitions(Test_UModernDiagramWidget_Movement PRIVATE RDK_USE_GLOG)
target_include_directories(Test_UModernDiagramWidget_Movement PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Engine
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Graphics
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
)

target_link_libraries(Test_UModernDiagramWidget_Movement
    GTest::gtest
    GTest::gtest_main
)
if(glog_FOUND)
    target_link_libraries(Test_UModernDiagramWidget_Movement glog::glog)
endif()

# Link against RDK libraries that UModernDiagramWidget depends on
target_link_libraries(Test_UModernDiagramWidget_Movement
    rdk.static.qt
    Rdk-BasicLib.qt
    Rdk-CvBasicLib.qt
)

add_test(NAME UModernDiagramWidgetMovementTest COMMAND Test_UModernDiagramWidget_Movement)
