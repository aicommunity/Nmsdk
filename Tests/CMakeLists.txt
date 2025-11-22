cmake_minimum_required(VERSION 3.16)
project(NmsdkTests LANGUAGES CXX)

# Стандарт C++
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Поиск Google Test
find_package(GTest QUIET)
if(NOT GTest_FOUND)
    # Если GTest не найден, используем FetchContent для загрузки
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.12.1
    )
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)
endif()

# Включить тестирование
enable_testing()

# Подпроекты
add_subdirectory(Unit)
add_subdirectory(Integration)

