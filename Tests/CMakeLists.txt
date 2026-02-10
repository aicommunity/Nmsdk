cmake_minimum_required(VERSION 3.16)
project(NmsdkTests LANGUAGES CXX)

# C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Google Test
find_package(GTest QUIET)
if(NOT GTest_FOUND)
    # If GTest is not found, use FetchContent to download it
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.12.1
    )
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)
endif()

# Enable testing
enable_testing()

# Subprojects
add_subdirectory(Unit)
add_subdirectory(Integration)

