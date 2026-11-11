# Сборка NeuroModeler и NeuroModelerConsole

Общие пресеты не содержат путей к установкам на конкретном компьютере. Индивидуальные значения задаются переменными окружения или игнорируемым `CMakeUserPresets.json`. Требуется CMake 3.23+, Git, Visual Studio с компонентами C++ и Windows SDK. Для генератора Visual Studio 2026 нужен CMake с поддержкой VS18 (4.2+).

## Быстрый запуск в Windows

В PowerShell задайте `VCPKG_ROOT` — каталог bootstrapped vcpkg. Для установленного Qt задайте `QT_ROOT` — корень комплекта для MSVC x64, содержащий `bin`, `include`, `lib/cmake`. Нужны Core, Gui, Widgets, Network, PrintSupport, Sql, Xml, Concurrent, Test, SerialPort, Charts, Svg; для Qt6 также Core5Compat и SvgWidgets. Неполная установка Qt обнаруживается при конфигурации.

```powershell
# Значения переменных задаются для вашей установки; они не записываются в репозиторий.
./Scripts/Build-Windows.ps1 -Preset win-vs2022-ninja-release-localqt
./Scripts/Build-Windows.ps1 -Preset win-vs2022-ninja-debug-localqt

# Qt собирается средствами vcpkg; QT_ROOT не требуется.
./Scripts/Build-Windows.ps1 -Preset win-vs2022-ninja-release-vcpkgqt
./Scripts/Build-Windows.ps1 -Preset win-vs2022-ninja-debug-vcpkgqt

# v142 может быть установлен дополнительным компонентом внутри VS2022.
./Scripts/Build-Windows.ps1 -Preset win-vs2019-ninja-release-localqt

# Решения Visual Studio / MSBuild:
./Scripts/Build-Windows.ps1 -Preset win-vs2022-msbuild-release-localqt
./Scripts/Build-Windows.ps1 -Preset win-vs2022-msbuild-debug-vcpkgqt
```

Скрипт находит установки через `vswhere`, выбирает соответствующий toolset, вызывает его `vcvarsall`, сохраняет исходный `VCPKG_ROOT` и собирает **оба** приложения. Пути к STL, SDK, `cl.exe` и номеру патча MSVC не синтезируются. Для повторной сборки одного приложения можно передать `-Targets NeuroModelerConsole`; число задач ограничивается `-Jobs` (по умолчанию до 8).

После каждой операции скрипт восстанавливает окружение вызывающей PowerShell-сессии. Его можно повторно вызывать с разными toolsets. При нескольких установках VS зависимости v143 привязаны к автоматически найденной VS2022 через `VCPKG_VISUAL_STUDIO_PATH`.

Для обычного вызова CMake/Ninja из терминала сначала активируйте x64 developer environment нужного toolset:

```powershell
$env:NMSDK_SHOW_QT_ROOT_PRESETS = "1" # явно показать общие QT_ROOT-пресеты
cmake --list-presets
cmake --preset win-vs2022-ninja-release-localqt
cmake --build --preset win-vs2022-ninja-release-localqt --parallel 8
```

MSBuild-пресеты используют штатное обнаружение установки Visual Studio самим CMake. Для `win-vs2019-msbuild-*` требуется именно VS2019. При наличии только VS2022 + v142 используйте `win-vs2019-ninja-*`.

## Матрица пресетов

Имя Windows-пресета: `win-vs{2019|2022|2026}-{ninja|msbuild}-{debug|release}-{localqt|vcpkgqt}`. Для каждого configure-пресета есть одноимённые build- и test-пресеты.

| Компилятор | Зависимости | Qt из vcpkg | Локальный Qt |
|---|---|---|---|
| MSVC 2019 16.11 / v142 | отдельный manifest, baseline `2023.10.19`, triplet `x64-windows-v142` | Qt 6.5.3 | Qt 5.15+ либо Qt6, собранный совместимым MSVC |
| MSVC 2022 / v143 | корневой manifest, фиксированный baseline `5cad485d…` | Qt 6.11.3 | Qt 5.15+ / совместимый Qt6 |
| MSVC 2026 / v145 | корневой manifest, triplet `x64-windows-v145` | Qt из того же baseline | совместимый Qt для этого toolset |

Наличие пресета не равнозначно проверке на соответствующем компиляторе. Фактическая матрица проверок и ограничения приведены в `Build-Audit-2026-11-11.md`. VS2026 не устанавливался в ходе аудита. Смешивать MinGW Qt с MSVC нельзя; MinGW и clang-cl не объявлены проверенными компиляторами проекта.

Qt 6.5 официально поддерживает MSVC2019/2022; у более новых Qt минимальная версия MSVC повышена. Поэтому один непрерывно обновляемый набор портов для v142 и v143 не используется. Выбор Qt5/Qt6 не должен менять toolset уже сконфигурированного дерева; используйте новое имя пользовательского пресета и отдельный `binaryDir`.

## Куда попадает результат

Приложения, соответствующие Qt DLL, плагины и сторонние DLL:

```text
build/<preset>/runtime/Debug/
build/<preset>/runtime/Release/
```

Статические библиотеки: `build/<preset>/lib/<configuration>/`. Ни Debug/Release, ни Qt5/Qt6, ни разные пресеты не перезаписывают результаты друг друга.

`NeuroModeler.ini` и `NeuroModelerConsole.ini` создаются при первой сборке. Они указывают на ресурсы данного checkout в `Bin` и не перезаписывают существующий ini. Это **генерируемые** локальные пути; в исходных файлах абсолютных путей конкретной машины нет. После переноса checkout удалите только эти сгенерированные ini или исправьте пути в них. Сборка не является переносимым установочным дистрибутивом: для поставки нужно отдельно упаковать ресурсы.

Для запуска выберите соответствующую runtime-папку рабочим каталогом. На машине сборки должен быть установлен подходящий MSVC Runtime. `windeployqt` берётся из выбранного Qt, очищаются глобальные `QT_PLUGIN_PATH`/`QML2_IMPORT_PATH`. Нельзя направлять эти переменные на другую версию Qt.

## Очистка без повторной компиляции Qt

Используются два независимых уровня сохранения зависимостей:

1. **Установленные пакеты** в `.deps/vcpkg/<toolset>-<qt-provider>/`: Debug и Release, Ninja и MSBuild одного профиля используют одну установку. Удаление `build/<preset>` не удаляет зависимости. Корень можно переопределить `-DNMSDK_DEPS_ROOT=...` в пользовательском пресете. Для разных наборов дополнительных features задавайте собственный `NMSDK_DEPENDENCY_PROFILE`.
2. **Бинарный кэш vcpkg** — штатно `%LOCALAPPDATA%/vcpkg/archives`, либо каталог `VCPKG_DEFAULT_BINARY_CACHE`, либо настроенный `VCPKG_BINARY_SOURCES`. После удаления `.deps` подходящие пакеты восстанавливаются из него, если совпадает ABI. Путь к собственному кэшу должен существовать. Не устанавливайте `VCPKG_BINARY_SOURCES=clear`, если хотите повторно использовать штатный кэш.

```powershell
# Очищаются объекты приложения, зависимости сохраняются:
./Scripts/Build-Windows.ps1 -Preset win-vs2022-ninja-release-vcpkgqt -Action clean
./Scripts/Build-Windows.ps1 -Preset win-vs2022-ninja-release-vcpkgqt -Action rebuild
```

Также допустимо удалить **конкретный** `build/<preset>` и заново вызвать configure. Для обычного rebuild не удаляйте `.deps`, `vcpkg/downloads`, бинарный кэш и не меняйте baseline. Новый компилятор, SDK, triplet, патчи порта или features могут изменить ABI: такая первая пересборка зависимостей ожидаема.

Не используйте общий classic-mode `%VCPKG_ROOT%/installed` как неявный источник пакетов для manifest-сборок. Это теряет контроль состава и версий зависимостей. Manifest mode + постоянный install-root + бинарный кэш решает задачу без этой неоднозначности. Параллельные установки через один checkout vcpkg сериализуются его штатной блокировкой; не удаляйте файл lock. Не конфигурируйте одновременно разные наборы features в один профиль `.deps`.

## WebEngine, тесты и дополнительные возможности

WebEngine выключен по умолчанию. Без него NeuroModeler использует предусмотренный в коде Qt Markdown viewer. Это позволяет не собирать Chromium для обычной сборки. Чтобы включить:

```powershell
./Scripts/Build-Windows.ps1 -Preset win-vs2022-ninja-release-vcpkgqt -WithWebEngine
# Для локального Qt модуль WebEngineWidgets уже должен быть установлен:
./Scripts/Build-Windows.ps1 -Preset win-vs2022-ninja-release-localqt -WithWebEngine
```

Для vcpkg используется штатный порт из закреплённого registry, согласованный с остальными модулями Qt. Старый `vcpkg-overlay-ports/qtwebengine` **не подключается**. Первая сборка Chromium всё равно длительна; требуются свободное место и короткий корень vcpkg/buildtrees. Последующие сборки используют установку/бинарный кэш.

Тесты по умолчанию выключены во всех обычных пресетах. Для их конфигурации и сборки:

```powershell
./Scripts/Build-Windows.ps1 -Preset win-vs2022-ninja-debug-localqt -WithTests -Targets Test_ArduinoPinMap
ctest --preset win-vs2022-ninja-debug-localqt -R PinMap
```

При следующем configure опции `-WithTests` и `-WithWebEngine` нужно передавать снова; обычный пресет задаёт базовую конфигурацию. Для Linux с локальным Qt WebEngine включается параметром `-DNMSDK_USE_WEBENGINE=ON`.

Интерактивные GUI-тесты имеют отдельный opt-in. По умолчанию LLM включён, embedded llama.cpp выключен; embedded-провайдер включается отдельно через `RDK_LLM_BUILD_EMBEDDED`. OpenCV, Python, CUDA, TensorFlow и прочие необязательные интеграции требуют отдельной установки SDK и согласованных features. Они не входят в стандартную проверенную сборку. Не включайте CMake-опцию без добавления её зависимостей в manifest features / окружение.

## VSCode

Установите рекомендованные CMake Tools и C/C++. Задайте пользовательские `VCPKG_ROOT` и при необходимости `QT_ROOT`, затем перезапустите VSCode, чтобы он унаследовал переменные. Выполните **CMake: Select Configure Preset**, затем **CMake: Select Build Preset** и выберите одноимённую конфигурацию. При первом запуске выберите **CMake: Set Launch/Debug Target** → NeuroModeler или NeuroModelerConsole.

Задачи `nmsdk: build NeuroModeler` и `nmsdk: build NeuroModelerConsole` работают с текущим активным CMake-пресетом; жёстко выбранной Linux-конфигурации или VS2019 Release больше нет. Debugger запускает выбранный CMake target из его фактического каталога. CMake Tools выполняет build-before-run один раз; дополнительного preLaunchTask нет. Для Ninja используется developer environment соответствующего toolset; если VSCode выбрал другой MSVC, ранняя проверка компилятора останавливает configure с понятной диагностикой. При сложном наборе установок используйте PowerShell-скрипт или запустите VSCode из developer shell нужного toolset.

## Linux

Пресеты: `linux-{gcc|clang}-{debug|release}-{local|vcpkg}`. `local` использует пакеты дистрибутива (либо Qt по `QT_ROOT`), не подключает Windows toolchain и не требует `VCPKG_ROOT`.

Для Debian/Ubuntu с Qt5 нужны, в частности: `build-essential ninja-build cmake git libboost-program-options-dev libboost-thread-dev libboost-filesystem-dev libboost-chrono-dev libboost-atomic-dev libcurl4-openssl-dev libgoogle-glog-dev nlohmann-json3-dev qtbase5-dev libqt5charts5-dev libqt5svg5-dev libqt5serialport5-dev`. Для тестов добавьте `libgtest-dev`, для Clang — `clang`. Для Qt6 потребуются соответствующие модули Qt6, включая Core5Compat и SvgWidgets.

```sh
cmake --preset linux-gcc-release-local
cmake --build --preset linux-gcc-release-local --parallel 8
```

Linux/vcpkg требует системных X11/XCB/OpenGL-пакетов, перечисленных в диагностике порта Qt. GCC и Clang имеют отдельные dependency profiles; пресеты сами задают соответствующие `CC`/`CXX`. Выбран shared-triplet `x64-linux-dynamic`, одинаковый для host и target: Qt собирается динамически без отдельной ручной регистрации статических platform plugins.

## Источники

- [vcpkg binary caching](https://learn.microsoft.com/en-us/vcpkg/users/binarycaching)
- [vcpkg manifest mode](https://learn.microsoft.com/en-us/vcpkg/consume/manifest-mode)
- [CMake Presets](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html)
- [Qt 6.5 supported platforms](https://doc.qt.io/qt-6.5/supported-platforms.html)
- [Qt 6.8 Windows support](https://doc.qt.io/qt-6.8/windows.html)



## VSCode: смена ветки и выбор vcpkg

Не переключайте ветку во время configure/build: CMake повторно читает toolchain
после установки зависимостей, и при переходе на ветку без него конфигурация упадёт.
После смены ветки дождитесь перечитывания пресетов; если остался старый кэш,
выполните **CMake: Delete Cache and Reconfigure** на нужной ветке. Каталог `.deps`
удалять не требуется.

CMake Tools может заменить `VCPKG_ROOT` при загрузке окружения Visual Studio.
Если выбран встроенный `VC/vcpkg`, toolchain восстанавливает явно заданный
Windows user/machine `VCPKG_ROOT` (пользовательский имеет приоритет).
Обычный внешний `VCPKG_ROOT` из shell остаётся без изменений.
Для намеренного выбора другого checkout, включая встроенный в VS, задайте
cache variable `NMSDK_VCPKG_ROOT` в своём `CMakeUserPresets.json` или передайте
`-DNMSDK_VCPKG_ROOT=...`. Этот явный параметр имеет наивысший приоритет.
Абсолютный путь в локальном пользовательском пресете не коммитится.
`cmake.environment` не используется как способ переопределения preset environment.

## Диагностика и выбор локального Qt в VSCode

`Scripts/Diagnose-Qt.ps1` не меняет конфигурацию. Он опрашивает `qmake -query`,
проверяет версию и MSVC metadata, архитектуру DLL, обязательные CMake-модули,
импортные библиотеки и DLL для Debug/Release, Windows platform plugins и windeployqt.
Это предварительная проверка целостности kit; окончательная проверка — сборка проекта.

```powershell
./Scripts/Diagnose-Qt.ps1
./Scripts/Diagnose-Qt.ps1 -SearchRoot <каталог-с-версиями-Qt>
./Scripts/Diagnose-Qt.ps1 -Root <конкретный-kit> -CompilerVersion 19.44
./Scripts/Diagnose-Qt.ps1 -Root <конкретный-kit> -WithWebEngine
```

Без `-Root` кандидаты берутся из process/user/machine `QT_ROOT`, `CMAKE_PREFIX_PATH`,
PATH, CMake package registry и настроек Qt Creator. `-SearchRoot` дополнительно
просматривает только два уровня каталогов (версия/kit), без сканирования диска.
Явный `-Root` ограничивает проверку указанными kit, без подстановки Qt из окружения.
При обнаружении нескольких подходящих kit автоматического выбора нет.

Чтобы выбирать версию Qt в интерфейсе VSCode, один раз выполните:

```powershell
./Scripts/Register-LocalQtPresets.ps1 -SearchRoot <каталог-с-версиями-Qt>
```

Команда находит установленные MSVC toolsets через vswhere и добавляет Debug/Release
для доступных Ninja/MSBuild в игнорируемый Git `CMakeUserPresets.json`.
Проверяется фактическая версия установленного компилятора относительно версии,
которой собран Qt. v142 внутри VS2022 доступен и для Ninja, и для MSBuild через
генератор VS2022; в названии такого варианта указано `(VS 2022)`.
Отсутствующие компиляторы не регистрируются. Например: `Qt 5.15.2 (msvc2019_64) | MSVC 2022 ninja release`.
Затем выполните **CMake: Select Configure Preset** и выберите нужную строку;
при необходимости выберите одноимённый **Build Preset**. Кнопка **Configure**
использует уже выбранный вариант и не показывает отдельный диалог Qt.
Если список не обновился, выполните **Developer: Reload Window**.

Чтобы ограничить набор, передайте `-BasePreset` с именами нужных общих
`*-localqt` пресетов. Указанный компилятор и система сборки должны быть установлены. Для WebEngine используйте `-WithWebEngine`.
Неполные kit исключаются. Для каждого kit создаётся отдельный каталог сборки;
зависимости продолжают использовать общую установку соответствующего профиля `.deps`.
Повторный запуск обновляет сгенерированные записи, сохраняя остальные пользовательские
пресеты. Предыдущий файл сохраняется в `.build-audit/CMakeUserPresets.before-qt.json`.
Локальные абсолютные пути в общий `CMakePresets.json` не попадают.

## Общие localqt-пресеты и список VSCode

В обычном списке отображаются варианты с конкретным проверенным Qt kit и установленным
компилятором, созданные `Register-LocalQtPresets.ps1`. Это устраняет дублирующие варианты,
которые зависели от QT_ROOT в старом окружении VSCode. После установки/удаления Qt или
компиляторов выполните регистрацию повторно. Если список VSCode не обновился, используйте
**Developer: Reload Window** и выберите новые Configure/Build Preset.

Общие `win-vs...-localqt` остаются переносимыми профилями. Для прямого вызова CMake
они включаются явно через `NMSDK_SHOW_QT_ROOT_PRESETS=1` вместе с `QT_ROOT` и нужным
developer environment. `Scripts/Build-Windows.ps1` включает этот режим сам и поддерживает
как общие имена, так и имена зарегистрированных Qt-пресетов. Linux-пресеты не менялись.
Общий профиль `win-vs2019-msbuild-...` использует генератор VS2019; зарегистрированный
профиль может использовать установленный VS2022 с v142, что видно по его названию.
