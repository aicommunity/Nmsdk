# QtVcpkgSetup.cmake
# Explicit Qt setup from vcpkg, excluding local Qt installations

# This file must be included BEFORE find_package(Qt5) in CMakeLists.txt
# Usage: include(cmake/QtVcpkgSetup.cmake) before find_package(Qt5)

# Verify that vcpkg is in use
if(NOT DEFINED VCPKG_TARGET_TRIPLET)
    message(WARNING "QtVcpkgSetup: VCPKG_TARGET_TRIPLET not defined. vcpkg may not be configured correctly.")
    return()
endif()

# Determine path to installed vcpkg packages
if(DEFINED VCPKG_INSTALLED_DIR)
    set(_vcpkg_installed_dir "${VCPKG_INSTALLED_DIR}")
else()
    # Try to find vcpkg_installed relative to CMAKE_BINARY_DIR or CMAKE_SOURCE_DIR
    if(EXISTS "${CMAKE_BINARY_DIR}/vcpkg_installed")
        set(_vcpkg_installed_dir "${CMAKE_BINARY_DIR}/vcpkg_installed")
    elseif(EXISTS "${CMAKE_SOURCE_DIR}/build/vcpkg_installed")
        set(_vcpkg_installed_dir "${CMAKE_SOURCE_DIR}/build/vcpkg_installed")
    else()
        message(WARNING "QtVcpkgSetup: Cannot find vcpkg_installed directory. Qt may not be configured correctly.")
        return()
    endif()
endif()

# Path to Qt from vcpkg
set(_vcpkg_qt_path "${_vcpkg_installed_dir}/${VCPKG_TARGET_TRIPLET}")

if(NOT EXISTS "${_vcpkg_qt_path}")
    message(WARNING "QtVcpkgSetup: vcpkg Qt path not found: ${_vcpkg_qt_path}")
    return()
endif()

message(STATUS "QtVcpkgSetup: Using Qt from vcpkg: ${_vcpkg_qt_path}")

# Remove local Qt installations from CMAKE_PREFIX_PATH
# Save the current CMAKE_PREFIX_PATH
get_property(_current_prefix_path CACHE CMAKE_PREFIX_PATH PROPERTY VALUE)
if(_current_prefix_path)
    # Split into a list
    string(REPLACE ";" "|" _prefix_path_string "${_current_prefix_path}")
    string(REPLACE "|" ";" _prefix_path_list "${_prefix_path_string}")

    # Filter paths, excluding local Qt installations
    set(_filtered_prefix_path "")
    foreach(_path IN LISTS _prefix_path_list)
        # Exclude standard Qt installation paths
        if(NOT _path MATCHES "C:/Qt/[0-9]+\\.[0-9]+\\.[0-9]+"
           AND NOT _path MATCHES "C:\\\\Qt\\\\[0-9]+\\\\[0-9]+\\\\[0-9]+"
           AND NOT _path MATCHES "/Qt/[0-9]+\\.[0-9]+\\.[0-9]+")
            list(APPEND _filtered_prefix_path "${_path}")
        else()
            message(STATUS "QtVcpkgSetup: Removing local Qt installation from CMAKE_PREFIX_PATH: ${_path}")
        endif()
    endforeach()

    # Add vcpkg Qt path to the beginning of the list (priority)
    list(INSERT _filtered_prefix_path 0 "${_vcpkg_qt_path}/debug")
    list(INSERT _filtered_prefix_path 0 "${_vcpkg_qt_path}")

    # Remove duplicates
    list(REMOVE_DUPLICATES _filtered_prefix_path)

    # Set the updated CMAKE_PREFIX_PATH
    set(CMAKE_PREFIX_PATH "${_filtered_prefix_path}" CACHE PATH "Qt from vcpkg only" FORCE)
    message(STATUS "QtVcpkgSetup: Updated CMAKE_PREFIX_PATH to use only vcpkg Qt")
else()
    # If CMAKE_PREFIX_PATH is empty, set only vcpkg paths
    set(CMAKE_PREFIX_PATH
        "${_vcpkg_qt_path}/debug"
        "${_vcpkg_qt_path}"
        CACHE PATH "Qt from vcpkg only" FORCE
    )
endif()

# Explicitly set Qt5_DIR to the path from vcpkg
set(Qt5_DIR "${_vcpkg_qt_path}/share/cmake/Qt5" CACHE PATH "Qt5 CMake config directory from vcpkg" FORCE)

# If QT_QMAKE_EXECUTABLE points to a local installation, try to find qmake in vcpkg
# But usually qmake is not needed for CMake if the proper Qt5*_DIR values are used
if(EXISTS "${QT_QMAKE_EXECUTABLE}")
    get_filename_component(_qmake_path "${QT_QMAKE_EXECUTABLE}" REALPATH)
    if(_qmake_path MATCHES "C:/Qt/[0-9]+\\.[0-9]+\\.[0-9]+" OR _qmake_path MATCHES "C:\\\\Qt\\\\[0-9]+\\\\[0-9]+\\\\[0-9]+")
        message(STATUS "QtVcpkgSetup: QT_QMAKE_EXECUTABLE points to local Qt installation: ${_qmake_path}")
        message(STATUS "QtVcpkgSetup: This is OK for MOC generation, but libraries will come from vcpkg")
        # Do not override QT_QMAKE_EXECUTABLE, as it may be needed for MOC
        # But ensure that libraries are taken from vcpkg via Qt5_DIR
    endif()
endif()

message(STATUS "QtVcpkgSetup: Configuration complete. Qt will be found from vcpkg only.")
