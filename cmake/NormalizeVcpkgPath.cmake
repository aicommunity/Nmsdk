# NormalizeVcpkgPath.cmake
# Нормализует путь к vcpkg toolchain файлу, заменяя обратные слеши на прямые
# Это необходимо только на Windows, где пути могут содержать обратные слеши
# которые интерпретируются CMake как escape-последовательности

# Выполняем нормализацию только на Windows
if(WIN32)
    # Когда используется CMakePresets.json, CMAKE_TOOLCHAIN_FILE уже установлен в кеше
    # Проверяем значение переменной (может быть установлено через кеш или как обычная переменная)
    if(CMAKE_TOOLCHAIN_FILE)
        set(_toolchain_file "${CMAKE_TOOLCHAIN_FILE}")

        # Нормализуем путь: заменяем обратные слеши на прямые
        string(REPLACE "\\" "/" _normalized_path "${_toolchain_file}")

        # Если путь изменился, обновляем кеш
        if(NOT "${_toolchain_file}" STREQUAL "${_normalized_path}")
            set(CMAKE_TOOLCHAIN_FILE "${_normalized_path}" CACHE FILEPATH "Path to vcpkg toolchain file" FORCE)
            message(STATUS "NormalizeVcpkgPath: Normalized toolchain path from ${_toolchain_file} to ${_normalized_path}")
        endif()
    elseif(DEFINED ENV{VCPKG_ROOT})
        # Если CMAKE_TOOLCHAIN_FILE не установлен, проверяем переменную окружения VCPKG_ROOT
        set(_vcpkg_root "$ENV{VCPKG_ROOT}")

        if(_vcpkg_root)
            # Нормализуем путь VCPKG_ROOT
            string(REPLACE "\\" "/" _normalized_vcpkg_root "${_vcpkg_root}")

            # Формируем нормализованный путь к toolchain файлу
            set(_toolchain_file "${_normalized_vcpkg_root}/scripts/buildsystems/vcpkg.cmake")

            # Устанавливаем нормализованный путь в кеш
            set(CMAKE_TOOLCHAIN_FILE "${_toolchain_file}" CACHE FILEPATH "Path to vcpkg toolchain file" FORCE)
            message(STATUS "NormalizeVcpkgPath: Set toolchain path from VCPKG_ROOT: ${_toolchain_file}")
        endif()
    endif()
else()
    # На Linux ничего не делаем - проблемы нет
    message(STATUS "NormalizeVcpkgPath: Skipping on non-Windows platform")
endif()
