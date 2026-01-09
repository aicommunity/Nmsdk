# QtVcpkgSetup.cmake
# Явная настройка Qt из vcpkg, исключая локальные установки Qt

# Этот файл должен быть включен ДО find_package(Qt5) в CMakeLists.txt
# Использование: include(cmake/QtVcpkgSetup.cmake) перед find_package(Qt5)

# Проверяем, что vcpkg используется
if(NOT DEFINED VCPKG_TARGET_TRIPLET)
    message(WARNING "QtVcpkgSetup: VCPKG_TARGET_TRIPLET not defined. vcpkg may not be configured correctly.")
    return()
endif()

# Определяем путь к установленным пакетам vcpkg
if(DEFINED VCPKG_INSTALLED_DIR)
    set(_vcpkg_installed_dir "${VCPKG_INSTALLED_DIR}")
else()
    # Пытаемся найти vcpkg_installed относительно CMAKE_BINARY_DIR или CMAKE_SOURCE_DIR
    if(EXISTS "${CMAKE_BINARY_DIR}/vcpkg_installed")
        set(_vcpkg_installed_dir "${CMAKE_BINARY_DIR}/vcpkg_installed")
    elseif(EXISTS "${CMAKE_SOURCE_DIR}/build/vcpkg_installed")
        set(_vcpkg_installed_dir "${CMAKE_SOURCE_DIR}/build/vcpkg_installed")
    else()
        message(WARNING "QtVcpkgSetup: Cannot find vcpkg_installed directory. Qt may not be configured correctly.")
        return()
    endif()
endif()

# Путь к Qt из vcpkg
set(_vcpkg_qt_path "${_vcpkg_installed_dir}/${VCPKG_TARGET_TRIPLET}")

if(NOT EXISTS "${_vcpkg_qt_path}")
    message(WARNING "QtVcpkgSetup: vcpkg Qt path not found: ${_vcpkg_qt_path}")
    return()
endif()

message(STATUS "QtVcpkgSetup: Using Qt from vcpkg: ${_vcpkg_qt_path}")

# Удаляем локальные установки Qt из CMAKE_PREFIX_PATH
# Сохраняем текущий CMAKE_PREFIX_PATH
get_property(_current_prefix_path CACHE CMAKE_PREFIX_PATH PROPERTY VALUE)
if(_current_prefix_path)
    # Разделяем на список
    string(REPLACE ";" "|" _prefix_path_string "${_current_prefix_path}")
    string(REPLACE "|" ";" _prefix_path_list "${_prefix_path_string}")
    
    # Фильтруем пути, исключая локальные установки Qt
    set(_filtered_prefix_path "")
    foreach(_path IN LISTS _prefix_path_list)
        # Исключаем стандартные пути установки Qt
        if(NOT _path MATCHES "C:/Qt/[0-9]+\\.[0-9]+\\.[0-9]+" 
           AND NOT _path MATCHES "C:\\\\Qt\\\\[0-9]+\\\\[0-9]+\\\\[0-9]+"
           AND NOT _path MATCHES "/Qt/[0-9]+\\.[0-9]+\\.[0-9]+")
            list(APPEND _filtered_prefix_path "${_path}")
        else()
            message(STATUS "QtVcpkgSetup: Removing local Qt installation from CMAKE_PREFIX_PATH: ${_path}")
        endif()
    endforeach()
    
    # Добавляем путь vcpkg Qt в начало списка (приоритет)
    list(INSERT _filtered_prefix_path 0 "${_vcpkg_qt_path}/debug")
    list(INSERT _filtered_prefix_path 0 "${_vcpkg_qt_path}")
    
    # Удаляем дубликаты
    list(REMOVE_DUPLICATES _filtered_prefix_path)
    
    # Устанавливаем обновленный CMAKE_PREFIX_PATH
    set(CMAKE_PREFIX_PATH "${_filtered_prefix_path}" CACHE PATH "Qt from vcpkg only" FORCE)
    message(STATUS "QtVcpkgSetup: Updated CMAKE_PREFIX_PATH to use only vcpkg Qt")
else()
    # Если CMAKE_PREFIX_PATH пуст, устанавливаем только vcpkg пути
    set(CMAKE_PREFIX_PATH 
        "${_vcpkg_qt_path}/debug"
        "${_vcpkg_qt_path}"
        CACHE PATH "Qt from vcpkg only" FORCE
    )
endif()

# Явно устанавливаем Qt5_DIR на путь из vcpkg
set(Qt5_DIR "${_vcpkg_qt_path}/share/cmake/Qt5" CACHE PATH "Qt5 CMake config directory from vcpkg" FORCE)

# Если QT_QMAKE_EXECUTABLE установлен на локальную установку, пытаемся найти qmake в vcpkg
# Но обычно qmake не нужен для CMake, если используются правильные Qt5*_DIR
if(EXISTS "${QT_QMAKE_EXECUTABLE}")
    get_filename_component(_qmake_path "${QT_QMAKE_EXECUTABLE}" REALPATH)
    if(_qmake_path MATCHES "C:/Qt/[0-9]+\\.[0-9]+\\.[0-9]+" OR _qmake_path MATCHES "C:\\\\Qt\\\\[0-9]+\\\\[0-9]+\\\\[0-9]+")
        message(STATUS "QtVcpkgSetup: QT_QMAKE_EXECUTABLE points to local Qt installation: ${_qmake_path}")
        message(STATUS "QtVcpkgSetup: This is OK for MOC generation, but libraries will come from vcpkg")
        # Не переопределяем QT_QMAKE_EXECUTABLE, так как он может быть нужен для MOC
        # Но убеждаемся, что библиотеки берутся из vcpkg через Qt5_DIR
    endif()
endif()

message(STATUS "QtVcpkgSetup: Configuration complete. Qt will be found from vcpkg only.")
