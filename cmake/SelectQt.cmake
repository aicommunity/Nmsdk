#
# SelectQt.cmake
# Унифицированный выбор Qt5/Qt6 и создание алиасов Nmsdk::Qt::*
#

include_guard(GLOBAL)

# Позволяем задавать версию явно: -DQT_MAJOR=5 или -DQT_MAJOR=6
if(DEFINED QT_MAJOR AND NOT DEFINED QT_VERSION_MAJOR)
  set(QT_VERSION_MAJOR "${QT_MAJOR}")
endif()

# Если версия ещё не определена — пробуем Qt6, затем Qt5
if(NOT DEFINED QT_VERSION_MAJOR)
  find_package(Qt6 QUIET COMPONENTS Core)
  if(Qt6_FOUND)
    set(QT_VERSION_MAJOR 6)
  else()
    find_package(Qt5 REQUIRED COMPONENTS Core)
    set(QT_VERSION_MAJOR 5)
  endif()
endif()

message(STATUS "Nmsdk: using Qt${QT_VERSION_MAJOR}")

if(QT_VERSION_MAJOR EQUAL 6)
  # Qt 6: базовые модули
  find_package(Qt6 REQUIRED COMPONENTS
    Core
    Gui
    Widgets
    Network
    PrintSupport
    Sql
    Xml
    Concurrent
    Test
  )

  # Дополнительные модули (опционально)
  find_package(Qt6 COMPONENTS SerialPort QUIET)
  find_package(Qt6 COMPONENTS WebEngineWidgets QUIET)
  find_package(Qt6 COMPONENTS Core5Compat QUIET)
  find_package(Qt6 COMPONENTS Charts QUIET)

  # Создаём таргеты без :: (CMake не позволяет :: в add_library)
  add_library(Nmsdk_Qt_Core       INTERFACE)
  add_library(Nmsdk_Qt_Gui        INTERFACE)
  add_library(Nmsdk_Qt_Widgets    INTERFACE)
  add_library(Nmsdk_Qt_Network    INTERFACE)
  add_library(Nmsdk_Qt_Print      INTERFACE)
  add_library(Nmsdk_Qt_Sql        INTERFACE)
  add_library(Nmsdk_Qt_Xml        INTERFACE)
  add_library(Nmsdk_Qt_Concurrent INTERFACE)
  add_library(Nmsdk_Qt_Test       INTERFACE)
  add_library(Nmsdk_Qt_SerialPort INTERFACE)
  add_library(Nmsdk_Qt_WebEngineWidgets INTERFACE)
  add_library(Nmsdk_Qt_CoreCompat INTERFACE)
  add_library(Nmsdk_Qt_Charts     INTERFACE)

  # Создаём алиасы с :: для удобства использования
  add_library(Nmsdk::Qt::Core ALIAS Nmsdk_Qt_Core)
  add_library(Nmsdk::Qt::Gui ALIAS Nmsdk_Qt_Gui)
  add_library(Nmsdk::Qt::Widgets ALIAS Nmsdk_Qt_Widgets)
  add_library(Nmsdk::Qt::Network ALIAS Nmsdk_Qt_Network)
  add_library(Nmsdk::Qt::Print ALIAS Nmsdk_Qt_Print)
  add_library(Nmsdk::Qt::Sql ALIAS Nmsdk_Qt_Sql)
  add_library(Nmsdk::Qt::Xml ALIAS Nmsdk_Qt_Xml)
  add_library(Nmsdk::Qt::Concurrent ALIAS Nmsdk_Qt_Concurrent)
  add_library(Nmsdk::Qt::Test ALIAS Nmsdk_Qt_Test)
  add_library(Nmsdk::Qt::WebEngineWidgets ALIAS Nmsdk_Qt_WebEngineWidgets)
  add_library(Nmsdk::Qt::CoreCompat ALIAS Nmsdk_Qt_CoreCompat)
  add_library(Nmsdk::Qt::SerialPort ALIAS Nmsdk_Qt_SerialPort)
  add_library(Nmsdk::Qt::Charts ALIAS Nmsdk_Qt_Charts)

  target_link_libraries(Nmsdk_Qt_Core       INTERFACE Qt6::Core)
  target_link_libraries(Nmsdk_Qt_Gui        INTERFACE Qt6::Gui)
  target_link_libraries(Nmsdk_Qt_Widgets    INTERFACE Qt6::Widgets)
  target_link_libraries(Nmsdk_Qt_Network    INTERFACE Qt6::Network)
  target_link_libraries(Nmsdk_Qt_Print      INTERFACE Qt6::PrintSupport)
  target_link_libraries(Nmsdk_Qt_Sql        INTERFACE Qt6::Sql)
  target_link_libraries(Nmsdk_Qt_Xml        INTERFACE Qt6::Xml)
  target_link_libraries(Nmsdk_Qt_Concurrent INTERFACE Qt6::Concurrent)
  target_link_libraries(Nmsdk_Qt_Test       INTERFACE Qt6::Test)

  if(TARGET Qt6::WebEngineWidgets)
    target_link_libraries(Nmsdk_Qt_WebEngineWidgets INTERFACE Qt6::WebEngineWidgets)
    set(NMSDK_QT_WEBENGINE_AVAILABLE TRUE)
  else()
    set(NMSDK_QT_WEBENGINE_AVAILABLE FALSE)
  endif()

  if(TARGET Qt6::Core5Compat)
    target_link_libraries(Nmsdk_Qt_CoreCompat INTERFACE Qt6::Core5Compat)
  endif()

  if(TARGET Qt6::SerialPort)
    target_link_libraries(Nmsdk_Qt_SerialPort INTERFACE Qt6::SerialPort)
  endif()

  if(TARGET Qt6::Charts)
    target_link_libraries(Nmsdk_Qt_Charts INTERFACE Qt6::Charts)
  endif()

elseif(QT_VERSION_MAJOR EQUAL 5)
  # Qt 5: используем те же алиасы
  find_package(Qt5 REQUIRED COMPONENTS
    Core
    Gui
    Widgets
    Network
    PrintSupport
    Charts
    Sql
    Xml
    SerialPort
    Concurrent
    Test
  )

  find_package(Qt5WebEngineWidgets QUIET)

  # Создаём таргеты без :: (CMake не позволяет :: в add_library)
  add_library(Nmsdk_Qt_Core       INTERFACE)
  add_library(Nmsdk_Qt_Gui        INTERFACE)
  add_library(Nmsdk_Qt_Widgets    INTERFACE)
  add_library(Nmsdk_Qt_Network    INTERFACE)
  add_library(Nmsdk_Qt_Print      INTERFACE)
  add_library(Nmsdk_Qt_Sql        INTERFACE)
  add_library(Nmsdk_Qt_Xml        INTERFACE)
  add_library(Nmsdk_Qt_Concurrent INTERFACE)
  add_library(Nmsdk_Qt_Test       INTERFACE)
  add_library(Nmsdk_Qt_WebEngineWidgets INTERFACE)
  add_library(Nmsdk_Qt_CoreCompat INTERFACE)
  add_library(Nmsdk_Qt_SerialPort INTERFACE)
  add_library(Nmsdk_Qt_Charts     INTERFACE)

  # Создаём алиасы с :: для удобства использования
  add_library(Nmsdk::Qt::Core ALIAS Nmsdk_Qt_Core)
  add_library(Nmsdk::Qt::Gui ALIAS Nmsdk_Qt_Gui)
  add_library(Nmsdk::Qt::Widgets ALIAS Nmsdk_Qt_Widgets)
  add_library(Nmsdk::Qt::Network ALIAS Nmsdk_Qt_Network)
  add_library(Nmsdk::Qt::Print ALIAS Nmsdk_Qt_Print)
  add_library(Nmsdk::Qt::Sql ALIAS Nmsdk_Qt_Sql)
  add_library(Nmsdk::Qt::Xml ALIAS Nmsdk_Qt_Xml)
  add_library(Nmsdk::Qt::Concurrent ALIAS Nmsdk_Qt_Concurrent)
  add_library(Nmsdk::Qt::Test ALIAS Nmsdk_Qt_Test)
  add_library(Nmsdk::Qt::WebEngineWidgets ALIAS Nmsdk_Qt_WebEngineWidgets)
  add_library(Nmsdk::Qt::CoreCompat ALIAS Nmsdk_Qt_CoreCompat)
  add_library(Nmsdk::Qt::SerialPort ALIAS Nmsdk_Qt_SerialPort)
  add_library(Nmsdk::Qt::Charts ALIAS Nmsdk_Qt_Charts)

  target_link_libraries(Nmsdk_Qt_Core       INTERFACE Qt5::Core)
  target_link_libraries(Nmsdk_Qt_Gui        INTERFACE Qt5::Gui)
  target_link_libraries(Nmsdk_Qt_Widgets    INTERFACE Qt5::Widgets)
  target_link_libraries(Nmsdk_Qt_Network    INTERFACE Qt5::Network)
  target_link_libraries(Nmsdk_Qt_Print      INTERFACE Qt5::PrintSupport)
  target_link_libraries(Nmsdk_Qt_Sql        INTERFACE Qt5::Sql)
  target_link_libraries(Nmsdk_Qt_Xml        INTERFACE Qt5::Xml)
  target_link_libraries(Nmsdk_Qt_Concurrent INTERFACE Qt5::Concurrent)
  target_link_libraries(Nmsdk_Qt_Test       INTERFACE Qt5::Test)
  target_link_libraries(Nmsdk_Qt_SerialPort INTERFACE Qt5::SerialPort)
  target_link_libraries(Nmsdk_Qt_Charts     INTERFACE Qt5::Charts)

  if(Qt5WebEngineWidgets_FOUND)
    target_link_libraries(Nmsdk_Qt_WebEngineWidgets INTERFACE Qt5::WebEngineWidgets)
    set(NMSDK_QT_WEBENGINE_AVAILABLE TRUE)
  else()
    set(NMSDK_QT_WEBENGINE_AVAILABLE FALSE)
  endif()

else()
  message(FATAL_ERROR "Unsupported Qt major version: ${QT_VERSION_MAJOR}")
endif()
