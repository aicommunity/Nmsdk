# ForceQtFromVcpkg.cmake
# Принудительная настройка Qt только из vcpkg
# Этот файл должен быть включен в самом начале CMakeLists.txt, ДО find_package(Qt5)
# ВАЖНО: vcpkg используется только на Windows, на Linux этот модуль не выполняется

# Выполняем только на Windows
if(NOT WIN32)
    message(STATUS "ForceQtFromVcpkg: Skipping on non-Windows platform (vcpkg is Windows-only)")
    return()
endif()

# Проверяем, что vcpkg используется
if(NOT DEFINED VCPKG_TARGET_TRIPLET)
    message(WARNING "ForceQtFromVcpkg: VCPKG_TARGET_TRIPLET not defined. vcpkg may not be configured correctly.")
    return()
endif()

# Определяем путь к установленным пакетам vcpkg
if(DEFINED VCPKG_INSTALLED_DIR)
    set(_vcpkg_installed_dir "${VCPKG_INSTALLED_DIR}")
elseif(EXISTS "${CMAKE_BINARY_DIR}/vcpkg_installed")
    set(_vcpkg_installed_dir "${CMAKE_BINARY_DIR}/vcpkg_installed")
elseif(EXISTS "${CMAKE_SOURCE_DIR}/build/vcpkg_installed")
    set(_vcpkg_installed_dir "${CMAKE_SOURCE_DIR}/build/vcpkg_installed")
else()
    message(WARNING "ForceQtFromVcpkg: Cannot find vcpkg_installed directory.")
    return()
endif()

set(_vcpkg_qt_path "${_vcpkg_installed_dir}/${VCPKG_TARGET_TRIPLET}")

if(NOT EXISTS "${_vcpkg_qt_path}")
    message(WARNING "ForceQtFromVcpkg: vcpkg Qt path not found: ${_vcpkg_qt_path}")
    return()
endif()

message(STATUS "ForceQtFromVcpkg: Forcing Qt from vcpkg: ${_vcpkg_qt_path}")

# Явно устанавливаем Qt5_DIR на путь из vcpkg
set(Qt5_DIR "${_vcpkg_qt_path}/share/cmake/Qt5" CACHE PATH "Qt5 CMake config directory from vcpkg" FORCE)

# Очищаем CMAKE_PREFIX_PATH от локальных установок Qt
get_property(_current_prefix_path CACHE CMAKE_PREFIX_PATH PROPERTY VALUE)
if(_current_prefix_path)
    string(REPLACE ";" "|" _temp_string "${_current_prefix_path}")
    string(REPLACE "|" ";" _prefix_list "${_temp_string}")

    set(_filtered_paths "")
    foreach(_path IN LISTS _prefix_list)
        # Исключаем локальные установки Qt
        if(NOT _path MATCHES "^[Cc]:[/\\\\]Qt[/\\\\][0-9]+[/\\\\][0-9]+[/\\\\][0-9]+"
           AND NOT _path MATCHES "^[Cc]:[/\\\\]Qt[/\\\\][0-9]+\\.[0-9]+\\.[0-9]+")
            list(APPEND _filtered_paths "${_path}")
        endif()
    endforeach()

    # Добавляем vcpkg пути в начало (приоритет)
    list(INSERT _filtered_paths 0 "${_vcpkg_qt_path}/debug")
    list(INSERT _filtered_paths 0 "${_vcpkg_qt_path}")

    list(REMOVE_DUPLICATES _filtered_paths)
    set(CMAKE_PREFIX_PATH "${_filtered_paths}" CACHE PATH "Qt from vcpkg only" FORCE)
endif()

message(STATUS "ForceQtFromVcpkg: Qt5_DIR = ${Qt5_DIR}")
message(STATUS "ForceQtFromVcpkg: Configuration complete.")
