# Анализ зависимостей сборки и расхождений с Bin/Platform/Win

**Дата анализа:** 2025-01-XX  
**Папка сборки:** `build/win-vs2022-debug`  
**Проблема:** Приложение падает при старте в `init_platform` (QGuiApplication::createPlatformIntegration)

## 1. Компилятор и инструменты сборки

### Компилятор
- **Версия:** MSVC 14.44.35207 (Visual Studio 2022 Community)
- **Путь:** `C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.44.35207/bin/HostX64/x64/cl.exe`
- **Стандарт C++:** C++20 (требуется)
- **Runtime Library:** `MultiThreaded$<IF:$<CONFIG:Debug>,Debug,>DLL` (MD/MDd)

### CMake
- **Версия:** 3.25.1
- **Путь:** `E:/vcpkg/downloads/tools/cmake-3.25.1-windows/cmake-3.25.1-windows-i386/bin/cmake.exe`
- **Генератор:** Visual Studio 17 2022 (x64)

## 2. Qt Framework

### Версия и источник
- **Версия при сборке:** Qt 5.15.10#2 (из vcpkg)
- **Путь при сборке:** `E:/Science-Repo/nmsdk-git/build/win-vs2022-debug/vcpkg_installed/x64-windows`
- **Qt5_DIR:** `E:/Science-Repo/nmsdk-git/build/win-vs2022-debug/vcpkg_installed/x64-windows/share/cmake/Qt5`
- **CMAKE_PREFIX_PATH:** `E:/Science-Repo/nmsdk-git/build/win-vs2022-debug/vcpkg_installed/x64-windows;E:/Science-Repo/nmsdk-git/build/win-vs2022-debug/vcpkg_installed/x64-windows/debug`

### ⚠️ КРИТИЧЕСКОЕ РАСХОЖДЕНИЕ
- **QT_QMAKE_EXECUTABLE:** `C:/Qt/5.15.2/msvc2019_64/bin/qmake.exe` (локальная установка Qt 5.15.2)
  - **Проблема:** QtCreator передает путь к локальной установке Qt 5.15.2, но это НЕ влияет на сборку (используется только qmake для генерации файлов)
  - **Фактически используется:** Qt 5.15.10 из vcpkg (подтверждено через Qt5_DIR в CMakeCache)

### Qt DLL в vcpkg (build)
```
Qt5Charts.dll
Qt5Concurrent.dll
Qt5Core.dll
Qt5DBus.dll
Qt5Gui.dll
Qt5Multimedia.dll
Qt5MultimediaQuick.dll
Qt5MultimediaWidgets.dll
Qt5Network.dll
Qt5OpenGL.dll
Qt5PrintSupport.dll
Qt5Qml.dll
Qt5QmlModels.dll
Qt5QmlWorkerScript.dll
Qt5Quick.dll
Qt5QuickParticles.dll
Qt5QuickShapes.dll
Qt5QuickTest.dll
Qt5QuickWidgets.dll
Qt5SerialPort.dll
Qt5Sql.dll
Qt5Svg.dll
Qt5Test.dll
Qt5Widgets.dll
Qt5Xml.dll
```

### Qt модули, используемые в проекте
- Core, Widgets, Gui, Network, PrintSupport, Charts, Sql, Xml, SerialPort, Concurrent

## 3. Boost

### Версия и источник
- **Версия:** Boost 1.82.0#2 (из vcpkg)
- **Компилятор:** vc140 (MSVC 2015-2022 совместимый)
- **Путь:** `E:/Science-Repo/nmsdk-git/build/win-vs2022-debug/vcpkg_installed/x64-windows`

### Boost библиотеки (Release)
```
boost_atomic-vc141-mt-x64-1_82.dll
boost_chrono-vc141-mt-x64-1_82.dll
boost_container-vc141-mt-x64-1_82.dll
boost_date_time-vc141-mt-x64-1_82.dll
boost_filesystem-vc141-mt-x64-1_82.dll
boost_program_options-vc141-mt-x64-1_82.dll
boost_regex-vc141-mt-x64-1_82.dll
boost_system-vc141-mt-x64-1_82.dll
boost_thread-vc141-mt-x64-1_82.dll
```

**Примечание:** В vcpkg используются библиотеки с суффиксом `vc141`, но в CMakeCache указаны библиотеки `vc140-mt`. Это нормально, так как vc141 совместим с vc140.

## 4. Qt Plugins - КРИТИЧЕСКОЕ РАСХОЖДЕНИЕ

### Плагины в vcpkg (build/win-vs2022-debug/vcpkg_installed/x64-windows/plugins)

#### platforms/
- `qdirect2d.dll` ✅
- `qminimal.dll` ✅
- `qoffscreen.dll` ✅
- `qwindows.dll` ✅
- **ОТСУТСТВУЕТ:** `qwindowsd.dll` ❌ (debug версия)

#### styles/
- `qwindowsvistastyle.dll` ✅
- **ОТСУТСТВУЕТ:** `qwindowsvistastyled.dll` ❌ (debug версия)

#### imageformats/
- `qgif.dll`, `qicns.dll`, `qico.dll`, `qjpeg.dll`, `qsvg.dll`, `qtga.dll`, `qtiff.dll`, `qwbmp.dll`, `qwebp.dll` ✅
- **ОТСУТСТВУЮТ:** Все debug версии (`*d.dll`) ❌

#### iconengines/
- `qsvgicon.dll` ✅
- **ОТСУТСТВУЕТ:** `qsvgicond.dll` ❌

#### bearer/
- `qgenericbearer.dll` ✅
- **ОТСУТСТВУЕТ:** `qgenericbearerd.dll` ❌

#### printsupport/
- `windowsprintersupport.dll` ✅
- **ОТСУТСТВУЕТ:** `windowsprintersupportd.dll` ❌

#### sqldrivers/
- `qsqlite.dll`, `qsqlodbc.dll` ✅
- **ОТСУТСТВУЮТ:** `qsqlited.dll`, `qsqlodbcd.dll` ❌

### Плагины в Bin/Platform/Win

#### platforms/
- `qdirect2d.dll` ✅
- `qminimal.dll` ✅
- `qoffscreen.dll` ✅
- `qwindows.dll` ✅
- `qwindowsd.dll` ✅ **ЕСТЬ DEBUG ВЕРСИЯ**

#### styles/
- `qwindowsvistastyle.dll` ✅
- `qwindowsvistastyled.dll` ✅ **ЕСТЬ DEBUG ВЕРСИЯ**

#### imageformats/
- Все release версии ✅
- **ВСЕ debug версии присутствуют** (`*d.dll`) ✅

#### iconengines/
- `qsvgicon.dll` ✅
- `qsvgicond.dll` ✅ **ЕСТЬ DEBUG ВЕРСИЯ**

#### bearer/
- `qgenericbearer.dll` ✅
- `qgenericbearerd.dll` ✅ **ЕСТЬ DEBUG ВЕРСИЯ**

#### printsupport/
- `windowsprintersupport.dll` ✅
- `windowsprintersupportd.dll` ✅ **ЕСТЬ DEBUG ВЕРСИЯ**

#### sqldrivers/
- `qsqlite.dll`, `qsqlodbc.dll` ✅
- `qsqlited.dll`, `qsqlodbcd.dll` ✅ **ЕСТЬ DEBUG ВЕРСИИ**

## 5. Анализ проблемы падения

### Стек вызовов при падении
```
1 qt_message_fatal qlogging.cpp 1885
2 QMessageLogger::fatal qlogging.cpp 893
3 init_platform qguiapplication.cpp 1254
4 QGuiApplicationPrivate::createPlatformIntegration qguiapplication.cpp 1484
5 QGuiApplicationPrivate::createEventDispatcher qguiapplication.cpp 1504
6 QApplicationPrivate::createEventDispatcher qapplication.cpp 168
7 QCoreApplicationPrivate::init qcoreapplication.cpp 836
8 QGuiApplicationPrivate::init qguiapplication.cpp 1532
9 QApplicationPrivate::init qapplication.cpp 515
10 QApplication::QApplication qapplication.cpp 501
11 main main.cpp 56
```

### Вероятные причины падения

#### 1. Отсутствие debug плагинов в vcpkg
**Проблема:** При сборке в Debug конфигурации Qt пытается загрузить debug плагины (`qwindowsd.dll`, `qwindowsvistastyled.dll` и т.д.), но vcpkg предоставляет только release версии.

**Доказательства:**
- В `build/win-vs2022-debug/vcpkg_installed/x64-windows/plugins` отсутствуют все debug плагины
- В `Bin/Platform/Win/plugins` присутствуют debug плагины (из локальной установки Qt 5.15.2)
- Приложение собирается в Debug конфигурации (`CMAKE_BUILD_TYPE:STRING=Debug`)

**Решение:**
- Либо использовать Release конфигурацию для сборки
- Либо скопировать debug плагины из локальной установки Qt 5.15.2 в `Bin/Platform/Win`
- Либо настроить Qt для использования release плагинов в debug режиме

#### 2. Несовместимость версий плагинов
**Проблема:** Debug плагины в `Bin/Platform/Win` могут быть из Qt 5.15.2, а release плагины из Qt 5.15.10 (vcpkg).

**Доказательства:**
- Qt DLL в `Bin/Platform/Win` имеют дату 24.09.2025 (синхронизированы с vcpkg)
- Debug плагины могут быть из старой локальной установки Qt 5.15.2

**Решение:**
- Убедиться, что все плагины (release и debug) из одной версии Qt

#### 3. Проблема с загрузкой стилей
**Проблема:** Приложение использует `UStyleManager` и применяет QSS стили сразу после создания `QApplication`. Если плагин стилей (`qwindowsvistastyle.dll`) не загружен корректно, это может вызвать падение.

**Доказательства:**
```cpp
// App/NeuroModeler/main.cpp:56-72
QApplication a(argc, argv);
UStyleManager* styleManager = UStyleManager::instance();
// ...
styleManager->applyGlobalStyleSheet(&a);
```

**Решение:**
- Проверить, что плагин стилей загружается до применения QSS
- Добавить проверку наличия плагина перед применением стилей

## 6. Рекомендации

### Немедленные действия

1. **Проверить конфигурацию сборки:**
   - Если собирается Debug версия, убедиться, что debug плагины присутствуют в `Bin/Platform/Win`
   - Если собирается Release версия, удалить debug плагины из `Bin/Platform/Win`

2. **Синхронизировать плагины:**
   - Скопировать все плагины (release и debug) из vcpkg в `Bin/Platform/Win`
   - Или использовать только release плагины для обеих конфигураций

3. **Проверить qt.conf:**
   - Убедиться, что `Bin/Platform/Win/qt.conf` правильно указывает на папку `plugins`
   - Проверить, что Qt находит плагины по указанному пути

4. **Добавить диагностику:**
   - Логировать путь к плагинам перед созданием QApplication
   - Проверить наличие необходимых плагинов перед их использованием

### Долгосрочные решения

1. **Унифицировать источники зависимостей:**
   - Использовать только vcpkg для всех зависимостей
   - Удалить локальные установки Qt из системы или исключить их из PATH

2. **Настроить автоматический деплой:**
   - Обновить скрипт `deploy_from_vcpkg.bat` для копирования debug плагинов (если они есть)
   - Или настроить сборку только в Release конфигурации

3. **Документировать требования:**
   - Указать, какие плагины необходимы для Debug и Release конфигураций
   - Создать чеклист для проверки окружения перед запуском

## 7. Сравнительная таблица плагинов

| Плагин | vcpkg (build) | Bin/Platform/Win | Статус |
|--------|---------------|------------------|--------|
| platforms/qwindows.dll | ✅ | ✅ | OK |
| platforms/qwindowsd.dll | ❌ | ✅ | **РАСХОЖДЕНИЕ** |
| styles/qwindowsvistastyle.dll | ✅ | ✅ | OK |
| styles/qwindowsvistastyled.dll | ❌ | ✅ | **РАСХОЖДЕНИЕ** |
| imageformats/*.dll | ✅ (release) | ✅ (release+debug) | **РАСХОЖДЕНИЕ** |
| iconengines/qsvgicon.dll | ✅ | ✅ | OK |
| iconengines/qsvgicond.dll | ❌ | ✅ | **РАСХОЖДЕНИЕ** |
| bearer/qgenericbearer.dll | ✅ | ✅ | OK |
| bearer/qgenericbearerd.dll | ❌ | ✅ | **РАСХОЖДЕНИЕ** |
| printsupport/windowsprintersupport.dll | ✅ | ✅ | OK |
| printsupport/windowsprintersupportd.dll | ❌ | ✅ | **РАСХОЖДЕНИЕ** |
| sqldrivers/qsqlite.dll | ✅ | ✅ | OK |
| sqldrivers/qsqlited.dll | ❌ | ✅ | **РАСХОЖДЕНИЕ** |

## 8. Выводы

1. **Основная проблема:** Отсутствие debug плагинов Qt в vcpkg при сборке в Debug конфигурации
2. **Вторичная проблема:** Смешанные версии плагинов (5.15.2 debug + 5.15.10 release)
3. **Решение:** Использовать только release плагины или обеспечить наличие debug плагинов из той же версии Qt

## 9. Следующие шаги

1. Проверить, в какой конфигурации собирается приложение (Debug/Release)
2. Если Debug - скопировать debug плагины из vcpkg или использовать release плагины
3. Если Release - удалить debug плагины из `Bin/Platform/Win`
4. Пересобрать и протестировать приложение
