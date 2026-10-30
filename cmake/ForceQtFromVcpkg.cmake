# ForceQtFromVcpkg.cmake
# Force Qt to be configured only from vcpkg
# This file must be included at the very beginning of CMakeLists.txt, BEFORE find_package(Qt5)
# IMPORTANT: vcpkg is used only on Windows; on Linux this module does nothing

# Run only on Windows
if(NOT WIN32)
    message(STATUS "ForceQtFromVcpkg: Skipping on non-Windows platform (vcpkg is Windows-only)")
    return()
endif()

# Verify that vcpkg is in use
if(NOT DEFINED VCPKG_TARGET_TRIPLET)
    message(WARNING "ForceQtFromVcpkg: VCPKG_TARGET_TRIPLET not defined. vcpkg may not be configured correctly.")
    return()
endif()

# Determine path to installed vcpkg packages
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

# Explicitly set Qt5_DIR to the path from vcpkg
set(Qt5_DIR "${_vcpkg_qt_path}/share/cmake/Qt5" CACHE PATH "Qt5 CMake config directory from vcpkg" FORCE)

# Clean CMAKE_PREFIX_PATH from local Qt installations and set correct paths
# Get the current CMAKE_PREFIX_PATH value (may be set by QtCreator or a preset)
get_property(_current_prefix_path CACHE CMAKE_PREFIX_PATH PROPERTY VALUE)

# Start with an empty list, adding only vcpkg paths
set(_filtered_paths "")

# If CMAKE_PREFIX_PATH is already set, process it
if(_current_prefix_path)
    # Convert to a list using a safe method
    # CMAKE_PREFIX_PATH can be a string or a list
    string(REPLACE ";" "|SEPARATOR|" _temp_string "${_current_prefix_path}")
    string(REPLACE "|SEPARATOR|" ";" _prefix_list "${_temp_string}")

    # Filter paths, excluding local Qt installations
    foreach(_path IN LISTS _prefix_list)
        # Skip empty paths
        if("${_path}" STREQUAL "")
            continue()
        endif()

        # Skip paths with unresolved variables (for example, ${binaryDir} from QtCreator)
        if("${_path}" MATCHES "\\$\\{[^}]+\\}")
            message(STATUS "ForceQtFromVcpkg: Skipping path with unresolved variables: ${_path}")
            continue()
        endif()

        # Normalize the path for comparison (bring to a common format)
        # Use a safe normalization method
        get_filename_component(_normalized_path "${_path}" ABSOLUTE)

        # Exclude local Qt installations (various path variants)
        # Check different patterns:
        # - C:/Qt/5.15.2/msvc2019_64
        # - C:\Qt\5.15.2\msvc2019_64
        # - C:/Qt/5.15.2/...
        # - Any paths containing /Qt/ with a version
        if(NOT _normalized_path MATCHES "[/\\\\]Qt[/\\\\][0-9]+([/\\\\][0-9]+)+"
           AND NOT _normalized_path MATCHES "[/\\\\]Qt[/\\\\][0-9]+\\.[0-9]+\\.[0-9]+"
           AND NOT _path MATCHES "^[Cc]:[/\\\\]Qt[/\\\\]"
           AND NOT _path MATCHES "Qt[/\\\\][0-9]+[/\\\\]")
            # Keep the path if it is not a local Qt installation
            # But exclude vcpkg paths, which will be added later
            if(NOT _path MATCHES "vcpkg_installed")
                list(APPEND _filtered_paths "${_path}")
            endif()
        else()
            message(STATUS "ForceQtFromVcpkg: Removing local Qt installation from CMAKE_PREFIX_PATH: ${_path}")
        endif()
    endforeach()
endif()

# Always add vcpkg paths at the beginning of the list (highest priority)
# First debug, then release (for multi-config generators)
list(INSERT _filtered_paths 0 "${_vcpkg_qt_path}/debug")
list(INSERT _filtered_paths 0 "${_vcpkg_qt_path}")

# Remove duplicates while preserving order
list(REMOVE_DUPLICATES _filtered_paths)

# Set CMAKE_PREFIX_PATH with FORCE to override any values coming from QtCreator
set(CMAKE_PREFIX_PATH "${_filtered_paths}" CACHE PATH "Qt from vcpkg only (local Qt installations filtered out)" FORCE)

message(STATUS "ForceQtFromVcpkg: CMAKE_PREFIX_PATH set to: ${_filtered_paths}")

message(STATUS "ForceQtFromVcpkg: Qt5_DIR = ${Qt5_DIR}")
message(STATUS "ForceQtFromVcpkg: Configuration complete.")
