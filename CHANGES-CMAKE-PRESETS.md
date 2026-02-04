# Изменения в CMakePresets.json для исправления win-msvc-debug/release

## Проблема
Пресеты `win-msvc-debug` и `win-msvc-release` перестали работать с ошибкой:
```
CMake Error: CMake was unable to find a build program corresponding to "Ninja".
CMAKE_MAKE_PROGRAM is not set.
```

## Причина
Пресет `win-msvc-base` использует генератор `Ninja`, но не указывает путь к исполняемому файлу `ninja.exe`.

## Решение
Добавлена переменная `CMAKE_MAKE_PROGRAM` в `cacheVariables` пресета `win-msvc-base`:
```json
"CMAKE_MAKE_PROGRAM": "$env{VCPKG_ROOT}/downloads/tools/ninja-1.13.2-windows/ninja.exe"
```

## Различия между пресетами

### win-msvc-base (Ninja генератор)
- **generator**: "Ninja"
- **CMAKE_MAKE_PROGRAM**: указан путь к ninja.exe из vcpkg
- **environment**: включает VCINSTALLDIR/VSINSTALLDIR (для vcpkg при сборке atlmfc)

### win-vs2022-base (Visual Studio генератор)
- **generator**: "Visual Studio 17 2022"
- **CMAKE_MAKE_PROGRAM**: не требуется (VS генератор использует MSBuild)
- **environment**: не включает VCINSTALLDIR/VSINSTALLDIR (не требуется)

## Статус
✅ Пресеты `win-msvc-debug` и `win-msvc-release` должны теперь работать корректно.
