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

# Очищаем CMAKE_PREFIX_PATH от локальных установок Qt и устанавливаем правильные пути
# Получаем текущее значение CMAKE_PREFIX_PATH (может быть установлено QtCreator или preset'ом)
get_property(_current_prefix_path CACHE CMAKE_PREFIX_PATH PROPERTY VALUE)

# Начинаем с пустого списка, добавляя только vcpkg пути
set(_filtered_paths "")

# Если CMAKE_PREFIX_PATH уже установлен, обрабатываем его
if(_current_prefix_path)
    # Преобразуем в список, используя безопасный метод
    # CMAKE_PREFIX_PATH может быть строкой или списком
    string(REPLACE ";" "|SEPARATOR|" _temp_string "${_current_prefix_path}")
    string(REPLACE "|SEPARATOR|" ";" _prefix_list "${_temp_string}")

    # Фильтруем пути, исключая локальные установки Qt
    foreach(_path IN LISTS _prefix_list)
        # Пропускаем пустые пути
        if("${_path}" STREQUAL "")
            continue()
        endif()

        # Пропускаем пути с неразрешенными переменными (например, ${binaryDir} от QtCreator)
        if("${_path}" MATCHES "\\$\\{[^}]+\\}")
            message(STATUS "ForceQtFromVcpkg: Skipping path with unresolved variables: ${_path}")
            continue()
        endif()

        # Нормализуем путь для сравнения (приводим к единому формату)
        # Используем try-catch для безопасной нормализации
        get_filename_component(_normalized_path "${_path}" ABSOLUTE)

        # Исключаем локальные установки Qt (различные варианты путей)
        # Проверяем различные паттерны:
        # - C:/Qt/5.15.2/msvc2019_64
        # - C:\Qt\5.15.2\msvc2019_64
        # - C:/Qt/5.15.2/...
        # - Любые пути, содержащие /Qt/ с версией
        if(NOT _normalized_path MATCHES "[/\\\\]Qt[/\\\\][0-9]+([/\\\\][0-9]+)+"
           AND NOT _normalized_path MATCHES "[/\\\\]Qt[/\\\\][0-9]+\\.[0-9]+\\.[0-9]+"
           AND NOT _path MATCHES "^[Cc]:[/\\\\]Qt[/\\\\]"
           AND NOT _path MATCHES "Qt[/\\\\][0-9]+[/\\\\]")
            # Сохраняем путь, если он не является локальной установкой Qt
            # Но исключаем пути vcpkg, которые мы добавим позже
            if(NOT _path MATCHES "vcpkg_installed")
                list(APPEND _filtered_paths "${_path}")
            endif()
        else()
            message(STATUS "ForceQtFromVcpkg: Removing local Qt installation from CMAKE_PREFIX_PATH: ${_path}")
        endif()
    endforeach()
endif()

# Всегда добавляем vcpkg пути в начало списка (высший приоритет)
# Сначала debug, потом release (для multi-config генераторов)
list(INSERT _filtered_paths 0 "${_vcpkg_qt_path}/debug")
list(INSERT _filtered_paths 0 "${_vcpkg_qt_path}")

# Удаляем дубликаты, сохраняя порядок
list(REMOVE_DUPLICATES _filtered_paths)

# Устанавливаем CMAKE_PREFIX_PATH с FORCE, чтобы переопределить любые значения от QtCreator
set(CMAKE_PREFIX_PATH "${_filtered_paths}" CACHE PATH "Qt from vcpkg only (local Qt installations filtered out)" FORCE)

message(STATUS "ForceQtFromVcpkg: CMAKE_PREFIX_PATH set to: ${_filtered_paths}")

message(STATUS "ForceQtFromVcpkg: Qt5_DIR = ${Qt5_DIR}")
message(STATUS "ForceQtFromVcpkg: Configuration complete.")
