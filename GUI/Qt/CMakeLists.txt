cmake_minimum_required(VERSION 3.16)
project(NeuroModelerGuiQt LANGUAGES CXX)

set(TARGET_NAME NeuroModelerGuiQt)

add_library(${TARGET_NAME} STATIC)

target_include_directories(${TARGET_NAME}
  PUBLIC
    ${CMAKE_SOURCE_DIR}/Rdk/GUI/Qt
    ${CMAKE_SOURCE_DIR}/GUI/Qt
)

target_sources(${TARGET_NAME}
  PRIVATE
    ${CMAKE_SOURCE_DIR}/GUI/Qt/NeuroModelerGuiRegistration.cpp
    ${CMAKE_SOURCE_DIR}/GUI/Qt/TNManipulatorControlWidget.cpp
    ${CMAKE_SOURCE_DIR}/GUI/Qt/TNDrawManipulatorWidget.cpp
    ${CMAKE_SOURCE_DIR}/GUI/Qt/TNDCEngineControlWidget.cpp
    ${CMAKE_SOURCE_DIR}/GUI/Qt/NNeuronTrainerWidget.cpp
    ${CMAKE_SOURCE_DIR}/GUI/Qt/TNNewPositionControlElementWidget.cpp
)

include(${CMAKE_SOURCE_DIR}/cmake/SelectQt.cmake)

target_link_libraries(${TARGET_NAME}
  PUBLIC
    Nmsdk::Qt::Core
    Nmsdk::Qt::Widgets
    rdk.static.qt
)

# Отключаем внешние GUI-зависимости в общем Rdk GUI
# (иначе UGEngineControlWidget попытается подключить UVideoAnalyticsSimpleSettingsWidget.h)
target_compile_definitions(${TARGET_NAME}
  PUBLIC
    RDK_DISABLE_EXT_GUI
)

