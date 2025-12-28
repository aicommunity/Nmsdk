cmake_minimum_required(VERSION 3.16)

# Тест для проверки работы меню
add_executable(Test_MenuBar Test_MenuBar.cpp)

# Поиск Qt5 или Qt6
find_package(Qt5 COMPONENTS Core Test Widgets REQUIRED)
find_package(Qt6 COMPONENTS Core Test Widgets QUIET)

if(Qt6_FOUND)
    target_link_libraries(Test_MenuBar Qt6::Core Qt6::Test Qt6::Widgets)
    target_compile_definitions(Test_MenuBar PRIVATE QT_VERSION_MAJOR=6)
else()
    target_link_libraries(Test_MenuBar Qt5::Core Qt5::Test Qt5::Widgets)
    target_compile_definitions(Test_MenuBar PRIVATE QT_VERSION_MAJOR=5)
endif()

# Добавляем пути для включения заголовков
target_include_directories(Test_MenuBar PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt
    ${CMAKE_SOURCE_DIR}/Rdk/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
)

# Добавляем тест в CTest
add_test(NAME MenuBarTest COMMAND Test_MenuBar)

