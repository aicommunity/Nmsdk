# Инструкция по настройке Qt Creator для сборки Nmsdk с vcpkg

## Предварительные требования

1. **Переменная окружения `VCPKG_ROOT`**:
   - Убедитесь, что переменная окружения `VCPKG_ROOT` установлена и указывает на каталог vcpkg (например, `E:\vcpkg`).
   - Проверить можно в PowerShell: `$env:VCPKG_ROOT`
   - Если не установлена, установите: `$env:VCPKG_ROOT = "E:\vcpkg"` (для текущей сессии) или через системные настройки Windows (постоянно).

2. **Qt‑пакеты из vcpkg должны быть установлены**:
   - Убедитесь, что Qt‑пакеты (`qtbase`, `qttools`, `qtserialport`, `qtcharts`, `qtwebengine`) установлены через vcpkg.
   - **ВАЖНО**: `qtwebengine` должен быть установлен с использованием overlay порта из проекта и коротким buildtrees‑путём.
   - Для установки используйте скрипт `install-qtwebengine.bat` из корня проекта:
     ```cmd
     install-qtwebengine.bat
     ```
   - Или вручную выполните:
     ```powershell
     cd E:\vcpkg
     .\vcpkg.exe install qtwebengine:x64-windows --triplet x64-windows --x-buildtrees-root=C:\bt --overlay-ports=E:\Science-Repo\nmsdk-git\vcpkg-overlay-ports
     ```
   - Остальные Qt‑пакеты обычно устанавливаются автоматически как зависимости `qtwebengine`.

## Настройка Qt Creator

### Шаг 1: Открыть проект

1. Запустите Qt Creator.
2. Откройте проект: `File` → `Open File or Project...` → выберите `CMakeLists.txt` в корне репозитория `E:\Science-Repo\nmsdk-git`.

### Шаг 2: Настроить использование CMake Presets

1. В Qt Creator перейдите в раздел **Projects** (вкладка слева или через меню).
2. Убедитесь, что выбран правильный **Kit** (например, "Desktop Qt 6.x.x MSVC2022 64bit" или "MSVC2022 64bit").
3. В разделе **Build Settings** найдите опцию **"Use CMake Presets"** и **включите её** (галочка должна быть установлена).
4. В выпадающем списке **"Configure Preset"** выберите один из пресетов:
   - `win-vs2022-release-vcpkgqt` — для Release сборки с Qt из vcpkg
   - `win-vs2022-debug-vcpkgqt` — для Debug сборки с Qt из vcpkg

### Шаг 3: Проверить настройки CMake

1. В разделе **CMake Configuration** убедитесь, что:
   - `CMAKE_TOOLCHAIN_FILE` установлен в значение из пресета (должно быть `E:/vcpkg/scripts/buildsystems/vcpkg.cmake` или `${sourceDir}/cmake/vcpkg_toolchain_from_env.cmake` для Ninja).
   - **НЕ** должно быть пути вида `build/.../vcpkg-dependencies/toolchain.cmake` (это означает, что Qt Creator создал свой wrapper, что не нужно).

2. Если видите `build/.../vcpkg-dependencies/toolchain.cmake`:
   - Убедитесь, что в пресете установлено `QT_CREATOR_SKIP_VCPKG_SETUP=ON`.
   - Переконфигурируйте проект: **Build** → **Run CMake** или нажмите кнопку "Configure Project".

### Шаг 4: Отключить встроенный vcpkg‑интегратор Qt Creator (если есть)

1. В настройках проекта **Build Settings** → **CMake** проверьте, нет ли отдельной опции **"Use vcpkg"** или **"vcpkg integration"**.
2. Если такая опция есть, **отключите её** (галочка должна быть снята).
3. Мы используем vcpkg через CMake toolchain из пресета, а не через встроенный интегратор Qt Creator.

### Шаг 5: Запустить конфигурацию

1. Нажмите кнопку **"Configure Project"** или выберите **Build** → **Run CMake**.
2. Дождитесь завершения конфигурации.
3. Если всё настроено правильно, vcpkg должен обнаружить уже установленные пакеты и быстро завершить manifest‑install без пересборки `qtwebengine`.

## Устранение проблем

### Ошибка: "vcpkg install failed" при конфигурации

**Причина**: vcpkg пытается пересобрать пакеты, но возникает ошибка (например, с `qtwebengine` из‑за длины пути или с другими пакетами).

**Решение**:
1. Убедитесь, что Qt‑пакеты установлены вручную через vcpkg с опцией `--x-buildtrees-root=C:\bt` (см. раздел "Предварительные требования").
2. Проверьте, что `VCPKG_ROOT` установлен правильно.
3. Очистите кэш CMake: **Build** → **Clear CMake Configuration** и переконфигурируйте проект.

### Ошибка: "CMAKE_TOOLCHAIN_FILE not found"

**Причина**: Переменная окружения `VCPKG_ROOT` не установлена или путь к vcpkg неверный.

**Решение**:
1. Установите `VCPKG_ROOT=E:\vcpkg` в переменных окружения Windows или в текущей сессии PowerShell.
2. Перезапустите Qt Creator после установки переменной окружения.

### Ошибка: "Buildtree path is too long" для qtwebengine

**Причина**: Путь к buildtrees слишком длинный для сборки QtWebEngine.

**Решение**:
1. Установите `qtwebengine` вручную с коротким buildtrees‑путём:
   ```powershell
   cd E:\vcpkg
   .\vcpkg.exe install qtwebengine:x64-windows --triplet x64-windows --x-buildtrees-root=C:\bt
   ```
2. После успешной установки переконфигурируйте проект в Qt Creator.

### Qt Creator использует свой vcpkg‑wrapper вместо пресета

**Причина**: Qt Creator автоматически создал `vcpkg-dependencies/toolchain.cmake`, игнорируя настройки пресета.

**Решение**:
1. Убедитесь, что в пресете `CMakePresets.json` установлено:
   - `QT_CREATOR_SKIP_VCPKG_SETUP=ON`
   - `QT_CREATOR_SKIP_PACKAGE_MANAGER_SETUP=ON`
2. Удалите каталог `build/win-vs2022-*-vcpkgqt/vcpkg-dependencies` (если существует).
3. Переконфигурируйте проект.

## Проверка успешной настройки

После успешной конфигурации вы должны увидеть в выводе CMake:
- Сообщения о найденных пакетах vcpkg (Boost, OpenCV, Qt и т.д.).
- Отсутствие ошибок вида "vcpkg install failed".
- Успешное завершение конфигурации без пересборки уже установленных пакетов.

## Дополнительные замечания

- **Использование пресетов**: Рекомендуется всегда использовать CMake Presets из `CMakePresets.json` вместо ручной настройки CMake переменных.
- **Генератор**: Пресеты `win-vs2022-*-vcpkgqt` используют генератор **Visual Studio 17 2022**, что обеспечивает лучшую интеграцию с отладчиком Visual Studio.
- **Manifest‑режим**: Проект использует manifest‑режим vcpkg (`vcpkg.json` в корне), поэтому все зависимости автоматически подтягиваются при конфигурации CMake.
