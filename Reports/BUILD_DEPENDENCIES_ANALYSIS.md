# Анализ зависимостей сборки NeuroModeler

**Дата анализа:** 2025-01-08 (обновлено)  
**Директория сборки:** `build` (новая чистая сборка)  
**Целевая платформа:** Windows x64  
**Генератор CMake:** Ninja

## Краткая сводка

### Критические находки:

1. **⚠️ КРИТИЧЕСКОЕ РАСХОЖДЕНИЕ ВЕРСИЙ Qt:**
   - При сборке используется Qt **5.15.10** из vcpkg
   - В `Bin/Platform/Win` находятся DLL Qt **5.15.2** из локальной установки
   - Это может привести к несовместимости и ошибкам времени выполнения

2. **⚠️ Несоответствие qmake и библиотек Qt:**
   - `QT_QMAKE_EXECUTABLE` указывает на локальную установку Qt 5.15.2
   - Библиотеки Qt берутся из vcpkg 5.15.10
   - Рекомендуется использовать qmake из той же установки, что и библиотеки

3. **✅ Положительные изменения:**
   - Все зависимости теперь из единого источника (vcpkg)
   - Используется современный генератор Ninja
   - Консистентные версии зависимостей

### Основные зависимости:

- **Qt:** 5.15.10 (из vcpkg) - **НЕ совпадает с Bin/Platform/Win (5.15.2)!**
- **Boost:** 1.82.0 (из vcpkg, vc141)
- **Компилятор:** MSVC 14.44.35207 (Visual Studio 2022)
- **Генератор:** Ninja
- **CMake:** 3.25.1 (из vcpkg)

## 1. Компилятор и инструменты сборки

### Компилятор C++
- **Тип:** MSVC (Microsoft Visual C++)
- **Версия:** 14.44.35207
- **Путь:** `C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207/bin/HostX64/x64/cl.exe`
- **Генератор CMake:** **Ninja** (не Visual Studio!)
- **CMake версия:** 3.25.1 (из vcpkg: `E:/vcpkg/downloads/tools/cmake-3.25.1-windows/cmake-3.25.1-windows-i386/bin/cmake.exe`)
- **Инстанс:** `C:/Program Files/Microsoft Visual Studio/2022/Community`
- **Build Type:** Debug (по умолчанию)

### Runtime библиотека
- **Тип:** MultiThreaded DLL (MD) / MultiThreadedDebug DLL (MDd)
- **Настройка:** `CMAKE_MSVC_RUNTIME_LIBRARY = MultiThreaded$<IF:$<CONFIG:Debug>,Debug,>DLL`
- **Причина:** Совместимость с vcpkg и внешними библиотеками

### Windows SDK
- **Версия:** 10.0.26100.0
- **Путь:** `C:/Program Files (x86)/Windows Kits/10/bin/10.0.26100.0/x64/`

## 2. Qt Framework

### Установка Qt

#### build (новая чистая сборка)
- **Версия:** **5.15.10** (из vcpkg, не 5.15.2!)
- **Путь:** `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/`
- **Источник:** **vcpkg** (через манифест `vcpkg.json`)
- **CMake пути:** Все Qt5*_DIR указывают на `vcpkg_installed/x64-windows/share/cmake/Qt5*`
- **QT_QMAKE_EXECUTABLE:** `C:/Qt/5.15.2/msvc2019_64/bin/qmake.exe` (локальная установка используется только для qmake)
- **Версия компилятора Qt:** vc141 (из vcpkg, совместимо с MSVC 2022)

**ВАЖНО:** 
- Qt версия в vcpkg - **5.15.10**, а не 5.15.2!
- qmake берется из локальной установки Qt 5.15.2, но сами библиотеки Qt из vcpkg 5.15.10
- Это может вызвать проблемы совместимости!

### Компоненты Qt, используемые при сборке

Из `CMakeCache.txt` (build):
- `Qt5Core_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Core`
- `Qt5Gui_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Gui`
- `Qt5Widgets_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Widgets`
- `Qt5Network_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Network`
- `Qt5Sql_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Sql`
- `Qt5Xml_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Xml`
- `Qt5Charts_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Charts`
- `Qt5Concurrent_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Concurrent`
- `Qt5PrintSupport_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5PrintSupport`
- `Qt5SerialPort_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5SerialPort`
- `Qt5Test_DIR`: `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/share/cmake/Qt5Test`

**Версии из vcpkg-manifest-install.log:**
- `qt5-base`: **5.15.10#2**
- `qt5-charts`: **5.15.10**
- `qt5-serialport`: **5.15.10**
- `qt5-svg`: **5.15.10** (также установлен, но не используется напрямую)
- `qt5-imageformats`: **5.15.10** (также установлен)
- `qt5-declarative`: **5.15.10** (также установлен)
- `qt5-multimedia`: **5.15.10** (также установлен)

**CMAKE_PREFIX_PATH:**
- `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/debug`
- `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows`
- `C:/Qt/5.15.2/msvc2019_64` (локальная установка также в пути поиска!)

### Qt DLL в Bin/Platform/Win

**Release версии (дата: 06.11.2020):**
- `Qt5Core.dll` - 6,023,664 байт
- `Qt5Gui.dll` - 7,008,240 байт
- `Qt5Widgets.dll` - 5,498,352 байт
- `Qt5Network.dll` - 1,340,400 байт
- `Qt5Sql.dll` - 208,880 байт
- `Qt5Charts.dll` - 1,419,248 байт
- `Qt5PrintSupport.dll` - 317,424 байт
- `Qt5SerialPort.dll` - 75,760 байт
- `Qt5Svg.dll` - 330,736 байт
- `Qt5Help.dll` - 428,528 байт
- `Qt5NetworkAuth.dll` - 158,704 байт

**Debug версии (дата: 24.09.2025, 07.12.2025):**
- `Qt5Cored.dll` - 14,908,416 байт
- `Qt5Guid.dll` - 20,100,096 байт
- `Qt5Widgetsd.dll` - 16,329,728 байт
- `Qt5Networkd.dll` - 6,022,656 байт
- `Qt5Sqld.dll` - 676,864 байт
- `Qt5Chartsd.dll` - 3,630,592 байт
- `Qt5PrintSupportd.dll` - 869,376 байт
- `Qt5SerialPortd.dll` - 267,264 байт
- `Qt5Svgd.dll` - 1,062,400 байт
- `Qt5Testd.dll` - 846,848 байт

**Важное наблюдение:**
- Release DLL имеют дату **06.11.2020** (оригинальная установка Qt 5.15.2)
- Debug DLL имеют дату **24.09.2025** и **07.12.2025** (пересобранные или обновленные)

### Qt плагины

#### Плагины в установке Qt (`C:/Qt/5.15.2/msvc2019_64/plugins`)

Всего **34 категории плагинов**, включая:
- `assetimporters` (4 плагина)
- `audio` (4 плагина)
- `bearer` (2 плагина)
- `canbus` (12 плагинов)
- `designer` (3 плагина)
- `gamepads` (2 плагина)
- `generic` (2 плагина)
- `geometryloaders` (4 плагина)
- `geoservices` (10 плагинов)
- `iconengines` (2 плагина)
- `imageformats` (18 плагинов)
- `mediaservice` (6 плагинов)
- `platforminputcontexts` (2 плагина)
- `platforms` (10 плагинов)
- `platformthemes` (2 плагина)
- `playlistformats` (2 плагина)
- `position` (6 плагинов)
- `printsupport` (2 плагина)
- `qmltooling` (22 плагина)
- `renderers` (2 плагина)
- `renderplugins` (2 плагина)
- `scenegraph` (2 плагина)
- `sceneparsers` (4 плагина)
- `sensorgestures` (4 плагина)
- `sensors` (2 плагина)
- `sqldrivers` (6 плагинов)
- `styles` (2 плагина)
- `texttospeech` (2 плагина)
- `virtualkeyboard` (10 плагинов)
- `webview` (2 плагина)

#### Плагины в Bin/Platform/Win (`Bin/Platform/Win/plugins`)

**Только 7 категорий плагинов** (минимальный набор):
- `bearer` (2 плагина: `qgenericbearer.dll`, `qgenericbearerd.dll`)
- `iconengines` (2 плагина: `qsvgicon.dll`, `qsvgicond.dll`)
- `imageformats` (18 плагинов: `qgif.dll`, `qjpeg.dll`, `qsvg.dll`, `qtiff.dll`, `qwebp.dll` и др.)
- `platforms` (10 плагинов: `qwindows.dll`, `qdirect2d.dll`, `qminimal.dll`, `qoffscreen.dll`, `qwebgl.dll` и др.)
- `printsupport` (2 плагина: `windowsprintersupport.dll`, `windowsprintersupportd.dll`)
- `sqldrivers` (6 плагинов: `qsqlite.dll`, `qsqlodbc.dll`, `qsqlpsql.dll` и debug версии)
- `styles` (2 плагина: `qwindowsvistastyle.dll`, `qwindowsvistastyled.dll`)

**Расхождения:**
- В `Bin/Platform/Win` отсутствуют многие плагины, присутствующие в полной установке Qt
- Это нормально, так как используются только необходимые плагины для работы приложения
- Все плагины имеют как release, так и debug версии

## 3. Boost Libraries

### Установка Boost

#### build (новая чистая сборка)
- **Версия:** **1.82.0** (из vcpkg)
- **Путь:** `E:/Science-Repo/nmsdk-git/build/vcpkg_installed/x64-windows/`
- **Источник:** **vcpkg** (через манифест `vcpkg.json`)
- **Компилятор:** **vc141** (Visual Studio 2017), совместимо с MSVC 2022
- **Библиотеки:** Все Boost библиотеки находятся в `vcpkg_installed/x64-windows/lib/` и `vcpkg_installed/x64-windows/debug/lib/`
- **DLL в bin:** `boost_*-vc141-mt-x64-1_82.dll` (Release) и `boost_*-vc141-mt-gd-x64-1_82.dll` (Debug)

**Примечание:** 
- В CMakeCache.txt библиотеки указаны как `boost_*-vc140-mt.lib`, но фактические DLL в `vcpkg_installed/x64-windows/bin/` имеют суффикс `vc141`
- Это нормально, так как vc140 и vc141 совместимы

### Используемые компоненты Boost

Из `CMakeLists.txt` и `RdkDefines.cmake`:
- `boost_program_options` - версия **1.82.0#2** (из vcpkg)
- `boost_thread` - версия **1.82.0#2** (из vcpkg)
- `boost_filesystem` - версия **1.82.0#2** (из vcpkg)
- `boost_system` - версия **1.82.0#2** (из vcpkg)
- `boost_chrono` - версия **1.82.0#2** (из vcpkg)
- `boost_atomic` - версия **1.82.0#3** (из vcpkg)

**Пути библиотек из CMakeCache.txt:**
- Release: `build/vcpkg_installed/x64-windows/lib/boost_*-vc140-mt.lib`
- Debug: `build/vcpkg_installed/x64-windows/debug/lib/boost_*-vc140-mt-gd.lib`

**Фактические DLL:**
- Release: `build/vcpkg_installed/x64-windows/bin/boost_*-vc141-mt-x64-1_82.dll`
- Debug: `build/vcpkg_installed/x64-windows/debug/bin/boost_*-vc141-mt-gd-x64-1_82.dll`

**Примечание:** В CMakeCache.txt указаны библиотеки с суффиксом `vc140`, но фактические DLL имеют суффикс `vc141`. Это нормально, так как они совместимы.

### Boost DLL в Bin/Platform/Win

**Release версии (vc141-mt-x64-1_82):**
- `boost_atomic-vc141-mt-x64-1_82.dll` - 17,408 байт
- `boost_chrono-vc141-mt-x64-1_82.dll` - 36,864 байт
- `boost_filesystem-vc141-mt-x64-1_82.dll` - 137,728 байт
- `boost_program_options-vc141-mt-x64-1_82.dll` - 384,000 байт
- `boost_system-vc141-mt-x64-1_82.dll` - 9,728 байт
- `boost_thread-vc141-mt-x64-1_82.dll` - 83,968 байт

**Debug версии (vc141-mt-gd-x64-1_82):**
- `boost_atomic-vc141-mt-gd-x64-1_82.dll` - 84,480 байт
- `boost_chrono-vc141-mt-gd-x64-1_82.dll` - 135,168 байт
- `boost_filesystem-vc141-mt-gd-x64-1_82.dll` - 492,032 байт
- `boost_program_options-vc141-mt-gd-x64-1_82.dll` - 1,269,760 байт
- `boost_system-vc141-mt-gd-x64-1_82.dll` - 48,640 байт
- `boost_thread-vc141-mt-gd-x64-1_82.dll` - 365,056 байт

**Важное наблюдение:**
- Boost DLL имеют дату **24.09.2025** (большинство)
- `boost_filesystem` имеет дату **07.12.2025** (возможно, пересобран)

## 4. Другие зависимости

### Google Logging (glog)
- **Версия:** **0.6.0#2** (из vcpkg)
- **DLL:** `glog.dll`, `gflags.dll` в `build/vcpkg_installed/x64-windows/bin/`
- **Источник:** vcpkg
- **В `Bin/Platform/Win`:** `glog.dll` (156,672 байт, дата: 07.12.2025), `gflags.dll` (135,680 байт), `gflags_debug.dll` (528,896 байт)

### OpenSSL
- **Версия:** **3.1.1** (из vcpkg)
- **DLL:** `libcrypto-3-x64.dll`, `libssl-3-x64.dll` в `build/vcpkg_installed/x64-windows/bin/`
- **В `Bin/Platform/Win`:** `libcrypto-3-x64.dll` (4,452,864 байт), `libssl-3-x64.dll` (547,328 байт)

### cURL
- **Версия:** **8.1.2** (из vcpkg)
- **DLL:** `libcurl.dll` в `build/vcpkg_installed/x64-windows/bin/`
- **В `Bin/Platform/Win`:** `libcurl.dll` (510,976 байт), `libcurl-d.dll` (1,520,128 байт)

### Библиотеки изображений
- `jpeg62.dll` - 623,104 байт
- `libpng16.dll` - 192,512 байт (Release)
- `libpng16d.dll` - 428,544 байт (Debug)
- `tiff.dll` - 452,608 байт (Release)
- `tiffd.dll` - 1,066,496 байт (Debug)
- `libwebp.dll` - 399,360 байт
- `libwebpdemux.dll` - 19,968 байт
- `libwebpmux.dll` - 39,936 байт
- `libsharpyuv.dll` - 22,016 байт

### Другие системные библиотеки

**Версии из vcpkg:**
- `double-conversion`: **3.2.1#1** → `double-conversion.dll`
- `freetype`: **2.12.1#3** → `freetype.dll`
- `harfbuzz`: **7.3.0** → `harfbuzz.dll`, `harfbuzz-subset.dll`
- `pcre2`: **10.42** → `pcre2-16.dll`, `pcre2-32.dll`, `pcre2-8.dll`, `pcre2-posix.dll`
- `sqlite3`: **3.42.0** → `sqlite3.dll`
- `zlib`: **1.2.13** → `zlib1.dll`
- `zstd`: **1.5.5** → `zstd.dll`
- `bzip2`: **1.0.8#4** → `bz2.dll`
- `brotli`: **1.0.9#5** → `brotlicommon.dll`, `brotlidec.dll`, `brotlienc.dll`
- `liblzma`: **5.4.3** → `liblzma.dll`
- `expat`: **2.5.0#3** → `libexpat.dll`
- `libffi`: **3.4.4#1** → `libffi.dll`

**В `Bin/Platform/Win`:**
- `double-conversion.dll` - 80,384 байт
- `freetype.dll` - 665,088 байт (Release), `freetyped.dll` - 1,545,728 байт (Debug)
- `harfbuzz.dll` - 978,944 байт
- `pcre2-16.dll` - 484,352 байт (Release), `pcre2-16d.dll` - 1,005,568 байт (Debug)
- `sqlite3.dll` - 945,152 байт
- `zlib1.dll` - 87,552 байт (Release), `zlibd1.dll` - 210,944 байт (Debug)
- `zstd.dll` - 635,904 байт
- `bz2.dll` - 70,656 байт (Release), `bz2d.dll` - 187,904 байт (Debug)
- `brotlicommon.dll` - 136,704 байт
- `brotlidec.dll` - 47,104 байт
- `liblzma.dll` - 187,392 байт

### Дополнительные зависимости из vcpkg

**Установленные, но не обязательно используемые напрямую:**
- `eigen3`: **3.4.0#2** - библиотека линейной алгебры
- `python3`: **3.10.7#6** - Python интерпретатор (опционально)
- `opencv`: **4.7.0#1** и `opencv4`: **4.7.0#6** - библиотека компьютерного зрения (опционально)
- `protobuf`: **3.21.12** - используется OpenCV
- `pkgconf`: **1.8.0#5** - утилита для pkg-config

### ODE Solver
- `ode-solver.dll` - 15,316,992 байт
- **Дата:** 08.07.2025
- **Источник:** Локальная сборка (не из vcpkg)
- **Примечание:** Не установлен через vcpkg, используется локальная сборка

## 5. vcpkg (опционально)

### Конфигурация vcpkg
- **Manifest файл:** `vcpkg.json`
- **Зависимости в манифесте:**
  - `qt5-base`
  - `qt5-serialport`
  - `qt5-charts`
  - `curl`
  - `opencv` (опционально)
  - `python3` (опционально)
  - `eigen3`
  - `zlib`
  - `boost-program-options`
  - `boost-thread`
  - `boost-filesystem`
  - `boost-system`
  - `boost-chrono`
  - `boost-atomic`
  - `glog`

#### build (новая чистая сборка)
- **Qt:** Берется из **vcpkg** (`vcpkg_installed/x64-windows/`) - версия **5.15.10**
- **Boost:** Берется из **vcpkg** (`vcpkg_installed/x64-windows/`) - версия **1.82.0**, компилятор **vc141**
- **Другие зависимости:** Также из vcpkg (glog, curl, OpenSSL, eigen3, python3, opencv и др.)

**Статус:** Все зависимости теперь из единого источника (vcpkg), что устраняет предыдущие расхождения!

## 6. Критические расхождения

### 6.1 Несоответствие версий Qt

**КРИТИЧЕСКАЯ ПРОБЛЕМА:** 

При сборке в `build` используется:
- Qt **5.15.10** из vcpkg (`vcpkg_installed/x64-windows/`)

Но в `Bin/Platform/Win` находятся DLL из:
- Qt **5.15.2** из локальной установки (`C:/Qt/5.15.2/msvc2019_64`)

**Также:** `QT_QMAKE_EXECUTABLE` указывает на локальную установку Qt 5.15.2, но библиотеки берутся из vcpkg 5.15.10.

**Последствия:**
- Версия Qt при сборке (5.15.10) не соответствует версии DLL в `Bin/Platform/Win` (5.15.2)
- Это может привести к несовместимости и ошибкам времени выполнения
- qmake из одной версии, библиотеки из другой версии

**Рекомендация:** 
- Либо обновить DLL в `Bin/Platform/Win` до версии 5.15.10 из vcpkg
- Либо использовать локальную установку Qt 5.15.2 для всего (включая сборку)

### 6.2 Qt DLL версии

**Проблема:** Release версии Qt DLL имеют дату **06.11.2020** (оригинальная установка), а Debug версии имеют дату **24.09.2025** и **07.12.2025**.

**Возможные причины:**
- Debug версии были пересобраны или обновлены
- Использовались разные источники для Release и Debug сборок
- Возможна несовместимость версий

**Рекомендация:** Проверить, что все Qt DLL из одной установки и одной версии.

### 6.3 Несоответствие версий Boost

**Проблема:** 

В `Bin/Platform/Win` находятся Boost DLL с суффиксом `vc141-mt-x64-1_82`, что соответствует версии из vcpkg. Однако в CMakeCache.txt библиотеки указаны как `vc140-mt.lib`.

**Статус:** Это не критично, так как vc140 и vc141 совместимы, но стоит обратить внимание на единообразие.

### 6.4 Qt плагины

**Расхождение:** В `Bin/Platform/Win` используется только **7 категорий** плагинов из **34 доступных** в полной установке Qt.

**Статус:** Это нормально, так как используются только необходимые плагины. Однако стоит убедиться, что все необходимые плагины присутствуют.

### 6.5 Boost компилятор

**Проблема:** Boost скомпилирован для **vc141** (Visual Studio 2017), но используется компилятор **MSVC 14.44** (Visual Studio 2022).

**Статус:** Обычно совместимо, но может вызвать проблемы в редких случаях. Рекомендуется пересобрать Boost для MSVC 2022.

### 6.6 Отсутствующие зависимости

**В `Bin/Platform/Win` отсутствуют некоторые библиотеки, которые могут быть нужны:**
- Некоторые Qt плагины (QML, multimedia и др.) - но они не используются в приложении
- Возможно, некоторые системные библиотеки Windows

## 7. Рекомендации

1. **КРИТИЧНО: Унифицировать версии Qt:** 
   - Сейчас при сборке используется Qt 5.15.10 из vcpkg, но в `Bin/Platform/Win` находятся DLL Qt 5.15.2
   - **Рекомендация:** Обновить DLL в `Bin/Platform/Win` до версии 5.15.10 из `build/vcpkg_installed/x64-windows/bin/`
   - Или использовать локальную установку Qt 5.15.2 для всего (но тогда нужно обновить vcpkg.json или использовать локальные пути)

2. **Унифицировать qmake и библиотеки Qt:**
   - Сейчас `QT_QMAKE_EXECUTABLE` указывает на локальную установку Qt 5.15.2, но библиотеки из vcpkg 5.15.10
   - **Рекомендация:** Использовать qmake из той же установки, что и библиотеки (либо из vcpkg, либо из локальной установки)

3. **Пересобрать Boost:** Рассмотреть возможность пересборки Boost для MSVC 2022 (vc143) для полной совместимости.

4. **Проверить зависимости:** Использовать `windeployqt` или `dependency walker` для проверки всех зависимостей.

5. **Документировать процесс деплоя:** Создать скрипт для автоматического копирования всех необходимых DLL и плагинов из правильного источника (vcpkg или локальные установки).

6. **Использовать vcpkg полностью:** Рекомендуется использовать vcpkg для всех зависимостей, включая Qt и Boost, для упрощения управления версиями и обеспечения консистентности.

## 8. Структура файлов сборки

### Директории сборки
- `build/` - новая чистая директория сборки (Ninja генератор)
- `build/vcpkg_installed/x64-windows/` - установленные пакеты vcpkg

### Кеш CMake
- `build/CMakeCache.txt` - основной кеш новой сборки

### Генератор сборки
- **Тип:** Ninja (не Visual Studio)
- **Файл:** `build/build.ninja`
- **Преимущества:** Быстрее чем Visual Studio генератор, лучше для CI/CD

### vcpkg установки
- `build/vcpkg_installed/x64-windows/` - установленные пакеты vcpkg
- `build/vcpkg-manifest-install.log` - лог установки пакетов vcpkg

## 9. Выводы

### Критические выводы:

1. **КРИТИЧЕСКОЕ РАСХОЖДЕНИЕ ВЕРСИЙ Qt:** 
   - При сборке в `build` используется Qt **5.15.10** из vcpkg
   - В `Bin/Platform/Win` находятся DLL Qt **5.15.2** из локальной установки
   - Это может привести к несовместимости и ошибкам времени выполнения!

2. **Qt 5.15.10 (из vcpkg):**
   - При сборке: из vcpkg (`build/vcpkg_installed/x64-windows/`)
   - Версия: **5.15.10** (не 5.15.2!)
   - Компилятор: vc141
   - qmake: из локальной установки Qt 5.15.2 (несоответствие!)

3. **Boost 1.82.0:**
   - При сборке: из vcpkg (`build/vcpkg_installed/x64-windows/`)
   - Компилятор: vc141
   - Версия: 1.82.0

4. **Компилятор MSVC 14.44** (Visual Studio 2022) используется для сборки

5. **Генератор:** Ninja (не Visual Studio)

6. **Runtime библиотека:** MultiThreaded DLL (MD/MDd) для совместимости с vcpkg

7. В `Bin/Platform/Win` присутствуют только необходимые Qt плагины (7 из 34 категорий)

8. **Все зависимости теперь из vcpkg** - это хорошо для консистентности, но версии должны совпадать с `Bin/Platform/Win`

**Основная рекомендация:** 
- **КРИТИЧНО:** Обновить DLL в `Bin/Platform/Win` до версии Qt 5.15.10 из `build/vcpkg_installed/x64-windows/bin/`
- Унифицировать qmake и библиотеки Qt (использовать из одного источника)
- Использовать `windeployqt` из vcpkg установки Qt для правильного деплоя Qt DLL и плагинов
- Проверить совместимость всех зависимостей между сборкой и runtime окружением
