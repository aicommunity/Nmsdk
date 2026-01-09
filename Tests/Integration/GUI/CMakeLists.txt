cmake_minimum_required(VERSION 3.16)

# Тест для проверки работы меню
add_executable(Test_MenuBar Test_MenuBar.cpp)

# Тест для проверки QMessageBox::question в Windows
# Используем обычный executable (не WIN32), так как это консольное приложение для тестирования
add_executable(Test_QMessageBox Test_QMessageBox.cpp)

# Production тест - использует Qt из Bin/Platform/<OS> (те же DLL и плагины, что и штатное приложение)
# Собирается в DEPLOY_ROOT для использования тех же бинарников Qt
add_executable(Test_QMessageBox_Production Test_QMessageBox_Production.cpp)

# Включаем автоматическую генерацию MOC файлов
set(CMAKE_AUTOMOC ON)
set_target_properties(Test_QMessageBox PROPERTIES AUTOMOC ON)
set_target_properties(Test_QMessageBox_Production PROPERTIES AUTOMOC ON)

# Настройка вывода для production теста в DEPLOY_ROOT
# Используем те же настройки, что и для штатного приложения
set_target_properties(Test_QMessageBox_Production PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${DEPLOY_ROOT}"
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${DEPLOY_ROOT}"
)

# Поиск Qt5 или Qt6
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
    # Production тест использует те же настройки Qt, что и штатное приложение
    target_link_libraries(Test_QMessageBox_Production Qt5::Core Qt5::Widgets Qt5::Gui)
    target_compile_definitions(Test_MenuBar PRIVATE QT_VERSION_MAJOR=5)
    target_compile_definitions(Test_QMessageBox PRIVATE QT_VERSION_MAJOR=5)
    target_compile_definitions(Test_QMessageBox_Production PRIVATE QT_VERSION_MAJOR=5 QT_DLL QT_WIDGETS_LIB)
endif()

# Добавляем пути для включения заголовков
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

# Добавляем тест в CTest
add_test(NAME MenuBarTest COMMAND Test_MenuBar)
add_test(NAME QMessageBoxTest COMMAND Test_QMessageBox)
add_test(NAME QMessageBoxProductionTest COMMAND Test_QMessageBox_Production)
add_test(NAME PluginLoadingTest COMMAND Test_PluginLoading)
add_test(NAME AppStartupTest COMMAND Test_AppStartup)
add_test(NAME QMessageBoxStyleCrashTest COMMAND Test_QMessageBoxStyleCrash)
add_test(NAME QMessageBoxWithStylesTest COMMAND Test_QMessageBoxWithStyles)

