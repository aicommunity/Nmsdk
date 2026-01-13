# Настройка Qt из vcpkg

## Проблема

QtCreator автоматически добавляет локальную установку Qt (`C:/Qt/5.15.2/msvc2019_64`) в `CMAKE_PREFIX_PATH`, что может привести к использованию неправильной версии Qt при сборке и запуске приложения.

## Решение

Создан модуль `ForceQtFromVcpkg.cmake`, который:
1. Принудительно устанавливает `Qt5_DIR` на путь из vcpkg
2. Удаляет локальные установки Qt из `CMAKE_PREFIX_PATH`
3. Гарантирует использование Qt только из vcpkg

## Использование

Модуль автоматически включается в `CMakeLists.txt` перед `find_package(Qt5)`:

```cmake
# В CMakeLists.txt (уже добавлено)
if(EXISTS "${CMAKE_SOURCE_DIR}/cmake/ForceQtFromVcpkg.cmake")
    include("${CMAKE_SOURCE_DIR}/cmake/ForceQtFromVcpkg.cmake")
endif()

find_package(Qt5 REQUIRED COMPONENTS ...)
```

## Файлы

- `cmake/ForceQtFromVcpkg.cmake` - основной модуль для принудительного использования Qt из vcpkg
- `cmake/QtVcpkgSetup.cmake` - альтернативный модуль (более сложный, но менее надежный)
- `build/qtcsettings_override.cmake` - переопределение настроек QtCreator

## Проверка

После пересборки проекта проверьте:

1. **CMakeCache.txt:**
   ```cmake
   Qt5_DIR:PATH=E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5
   ```

2. **CMAKE_PREFIX_PATH не должен содержать:**
   ```
   C:/Qt/5.15.2/msvc2019_64
   ```

3. **Все Qt5*_DIR должны указывать на vcpkg:**
   ```
   Qt5Core_DIR: E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Core
   ```

## Примечания

- `QT_QMAKE_EXECUTABLE` может оставаться на локальной установке Qt для генерации MOC файлов
- Это нормально, так как qmake используется только для метаобъектной компиляции
- Важно, что библиотеки Qt берутся из vcpkg через `Qt5_DIR`
