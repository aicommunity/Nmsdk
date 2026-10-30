# NormalizeVcpkgPath.cmake
# Normalizes the path to the vcpkg toolchain file, replacing backslashes with forward slashes
# This is needed only on Windows, where paths may contain backslashes
# which CMake interprets as escape sequences

# Perform normalization only on Windows
if(WIN32)
    # When CMakePresets.json is used, CMAKE_TOOLCHAIN_FILE is already set in the cache
    # Check the variable value (it may be set via cache or as a regular variable)
    if(CMAKE_TOOLCHAIN_FILE)
        set(_toolchain_file "${CMAKE_TOOLCHAIN_FILE}")

        # Normalize the path: replace backslashes with forward slashes
        string(REPLACE "\\" "/" _normalized_path "${_toolchain_file}")

        # If the path has changed, update the cache
        if(NOT "${_toolchain_file}" STREQUAL "${_normalized_path}")
            set(CMAKE_TOOLCHAIN_FILE "${_normalized_path}" CACHE FILEPATH "Path to vcpkg toolchain file" FORCE)
            message(STATUS "NormalizeVcpkgPath: Normalized toolchain path from ${_toolchain_file} to ${_normalized_path}")
        endif()
    elseif(DEFINED ENV{VCPKG_ROOT})
        # If CMAKE_TOOLCHAIN_FILE is not set, check the VCPKG_ROOT environment variable
        set(_vcpkg_root "$ENV{VCPKG_ROOT}")

        if(_vcpkg_root)
            # Normalize VCPKG_ROOT path
            string(REPLACE "\\" "/" _normalized_vcpkg_root "${_vcpkg_root}")

            # Build the normalized path to the toolchain file
            set(_toolchain_file "${_normalized_vcpkg_root}/scripts/buildsystems/vcpkg.cmake")

            # Store the normalized path in the cache
            set(CMAKE_TOOLCHAIN_FILE "${_toolchain_file}" CACHE FILEPATH "Path to vcpkg toolchain file" FORCE)
            message(STATUS "NormalizeVcpkgPath: Set toolchain path from VCPKG_ROOT: ${_toolchain_file}")
        endif()
    endif()
else()
    # Do nothing on Linux - there is no such problem
    message(STATUS "NormalizeVcpkgPath: Skipping on non-Windows platform")
endif()
