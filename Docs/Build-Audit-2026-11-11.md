# Аудит сборки arduino: 11 ноября 2026

## Исходное состояние и границы

Рабочая копия: `C:/Work/Nmsdk` на `10.245.1.8`. Начальный корневой commit: `6c88f7ff59a268f1a68cce83887448bdf403d04a`, ветка `arduino`, рабочее дерево чистое. Аудит касается CMake, vcpkg, сборочных скриптов и настроек VSCode для NeuroModeler/NeuroModelerConsole и их общего графа библиотек. Функциональность `develop` не переносится; подготовка будущего слияния с `develop` не входит в задачу.

На машине установлен VS2022 Community с toolset 14.44 (v143) и дополнительным 14.29 (v142), Windows SDK 26100, Ninja; отдельной VS2019 и VS2026 нет. Есть Qt5.15.2/MSVC2019 и неполный Qt6.9.1/MSVC2022 (отсутствуют необходимые SerialPort/Core5Compat). `VCPKG_ROOT` указывает на отдельный checkout vcpkg. WSL/Linux не установлен. Проверка Linux отложена по договорённости с автором задачи до завершения Windows-проверок и коммитов.

## Основные дефекты и изменения

| Приоритет | До аудита | Исправление |
|---|---|---|
| P0 | Общие пресеты содержат абсолютные пути к Community VS2019/2022, конкретным версиям MSVC, SDK, Qt | Пути удалены из общих пресетов; MSBuild обнаруживает VS штатно, PowerShell-скрипт выбирает toolset через vswhere/vcvarsall |
| P0 | QtWebEngine overlay 6.10.0 применяется к QtBase 6.11.3 | Overlay не подключается; registry закреплён; WebEngine выделен в отдельную опцию и feature |
| P0 | DLL Debug и Release копируются в один каталог, включая DLL с одинаковыми именами | DLL выбираются по фактической конфигурации; каждый preset/configuration имеет собственный runtime |
| P0 | Основные Qt DLL пропускаются при deployment; выбор Qt зависит от содержимого PATH и случайно найденных пакетов | Полный Qt выбирается до модулей; windeployqt берётся из выбранного Qt; глобальные plugin paths очищаются |
| P1 | Установленные vcpkg-пакеты лежат внутри disposable build-каталога | Постоянный `.deps/vcpkg/<profile>`, общий для Debug/Release и генераторов одного toolset/provider |
| P1 | Manifest не закрепляет registry; VS2019 использует актуальные порты с несовместимыми требованиями | Основной baseline закреплён; v142 имеет отдельный manifest с Qt6.5.3/Boost1.83 |
| P1 | vcvarsall может заменить VCPKG_ROOT на встроенный VS vcpkg | Скрипт сохраняет явно выбранный корень до активации developer environment |
| P1 | Qt6 SerialPort/Charts/Svg/Core5Compat объявляются «optional», но используются исходниками | Обязательные модули теперь REQUIRED; конфигурация падает до компиляции, если установка Qt неполна |
| P1 | Boost ищется многократно разными способами; ошибки маскируются QUIET и частичными fallback | Единая Nmsdk::Boost с обязательными компонентами, CONFIG-first, совместимый module fallback |
| P1 | CURL не распространяется как зависимость статического Rdk, хотя вызывается его исходниками | CURL::libcurl подключён PUBLIC к rdk.static.qt |
| P1 | glog объявлен optional, но rdk_logging.h содержит безусловный #error при отсутствии RDK_USE_GLOG | glog — обязательная обнаруживаемая зависимость ядра |
| P1 | BUILD_TESTS и BUILD_TESTING расходятся; Rdk читает флаг раньше корня | Один BUILD_TESTING до add_subdirectory, поддерживается входной legacy alias с проверкой конфликта |
| P1 | VSCode выбирает Linux configure preset и фиксированный VS2019 Release build task; запуск ищет старый Bin/Platform | Выбор пресетов пользователем, задачи CMake Tools и фактический launchTargetPath/Directory |
| P2 | GLOB без CONFIGURE_DEPENDS не замечает новые cpp в библиотеках | Добавлено отслеживание изменений в корневых списках исходников модулей |
| P2 | Необязательные LLM/GUI-тесты напрямую требуют Qt5 при сборке с Qt6 | Используется выбранный Qt и общие алиасы |
| P2 | Несколько тестов линкуют bare gtest/gtest_main | Используются imported targets GTest::gtest/GTest::gtest_main с корректной Debug/Release библиотекой |
| P2 | ConfigValidation ищет уже собранный exe на этапе configure, причём Windows-путь написан иначе | Используется $<TARGET_FILE:NeuroModelerConsole> и зависимость target |
| P2 | Старые bat-скрипты закрепляют иной vcpkg, удаляют установленные зависимости, запускают несуществующие пресеты | Общая точка сборки в Scripts/Build-Windows.ps1; старые entrypoints обновлены/переведены на инструкции без очистки зависимостей |

## Диагностика исходного QtWebEngine

Из исходного `build/win-vs2022-release-vcpkgqt/vcpkg-manifest-install.log`: QtBase/QtDeclarative установлены версии 6.11.3, overlay QtWebEngine имеет версию 6.10.0. Ошибка возникает во время configure, до компиляции Chromium:

```text
QtPublicSbomHelpers.cmake: The current active SBOM project name was not found.
src/core/api/CMakeLists.txt: qt_internal_add_module
```

Уменьшение числа потоков или очередное удаление кэша этот конфликт модулей не устраняет. В исходной попытке перед WebEngine уже успешно собраны 202 пакета. Их бинарный кэш сохранён и используется. Старый overlay оставлен в истории/дереве как неактивный материал, а не как источник сборки.

## Сравнение с актуальным origin/develop

Ссылки `origin/develop` обновлены через HTTPS (SSH-аутентификация GitHub на удалённом компьютере не настроена). Рабочие ветки и привязки сабмодулей при этом не переключались.

| Репозиторий | develop на момент аудита | Вывод по сборке |
|---|---|---|
| Nmsdk | `1d1c8e5dc3e50bca51c174d9552feab4a5ccf5d9` | Полезны отдельный runtime, единый test switch, конфигурационное копирование DLL. Эти идеи учтены, deployment доработан для Qt и multi-config |
| Rdk | `10e9d05aa658dd2203c89bc84ba9166595b50014` | PUBLIC CURL для статического ядра — полезное исправление. Дополнительно есть изменение startup/working directory в C++; оно не переносится как несвязанная функциональная миграция |
| Nmsdk-PulseLib | `0ec9193e6620ae2439329eece5ecd6d6f167c70a` | CONFIGURE_DEPENDS полезен. Подкаталог TimeLearner и его cpp относятся к другой функциональности; в arduino не добавляются |
| Rdk-HardwareLib | `ac53a6011bfedf97d459b47bcd4d525fb6c9b811` | develop не содержит новых Arduino/ESP32 частей. Сокращённый список исходников переносить нельзя |
| Nmsdk-MotionControlLib | `85e4494e8596b0998feebff7da2f8d421a6df66f` | Изменений CMake относительно используемого commit нет |
| Rdk-BasicLib | `2927cad5a7456b301217b7abb228f12c9a359ea9` | Изменений CMake относительно используемого commit нет |
| Rdk-CvBasicLib | `c471297811367abd348c6258bdaeaf8e1a40c7bd` | Изменений CMake относительно используемого commit нет |
| Nmsdk-Bin | `b4f66eb137d3e1c19539890dbdee06faa3e1020b` | Сборочных CMake-изменений нет; данные и функциональная миграция не переносятся |

Корневой develop также добавляет GUI LinkRouter/ExternalSource/ExternalSink и Console TimeLearner job cpp. Это не универсальные исправления CMake: они требуют соответствующего содержимого Rdk/PulseLib. В arduino их нет, поэтому механическое копирование CMakeLists.txt сломало бы configure. Новые перечисления тестов в develop также связаны с его миграциями и не перенесены целиком.

## Проверки

Для каждой строки ниже собраны **оба** приложения. Все семь основных конфигураций прошли сборку. После исправления сохранения окружения две последние проверки повторены успешно; первоначальный журнал ошибок сохранён отдельно.

| Компилятор / генератор | Qt | Конфигурация | Результат |
|---|---|---|---|
| v142 / Ninja (toolset внутри VS2022) | локальный 5.15.2 | Debug, Release | build прошёл; оба exe `--help` вернули 0 |
| v143 / Ninja | локальный 5.15.2 | Debug, Release | build прошёл; оба exe `--help` вернули 0 |
| v143 / Ninja | vcpkg 6.11.3 | Debug, Release | build прошёл; оба exe `--help` вернули 0; проверен split-layout debug deployment |
| v143 / MSBuild | локальный 5.15.2 | Release | build прошёл; оба exe `--help` вернули 0 |
| v143 / Ninja, дополнительный opt-in | локальный 5.15.2 + WebEngine | Release | build и запуск прошли; проверены QtWebEngineProcess.exe, ICU, Chromium pak и locale |

Всего успешно выполнено 14 запусков приложений в семи конфигурациях. GUI-проверка включает создание QApplication, загрузку Windows platform plugin и темы оформления. Console также прошла инициализацию и штатно вернула код 1 с отчётом валидации для заведомо несуществующего проекта.

Дополнительные проверки:

- `BUILD_TESTING=ON`: полный тестовый CMake-граф сконфигурирован, собран `Test_ArduinoPinMap`; 4/4 программных теста прошли. Аппаратные live-тесты и прошивка плат не выполнялись. Полный набор C++ test targets не собирался и не запускался.
- Новый пустой `build/cache-reuse-probe` использовал существующий `.deps/vcpkg/v143-localqt`. Ни один пакет не компилировался заново; vcpkg завершил проверку установок за 3.63 мс, весь configure занял 32 с. Это проверяет сохранение зависимостей при удалении application build tree.
- До этого 66 пакетов восстановлены из штатного бинарного кэша за 8.2 с. Кэш и downloads сохранены.
- Отдельная регрессионная проверка deployment под CMake 3.23: разные Debug/Release `glog.dll` с одинаковым именем; Release DLL с окончанием `d` (`zstd.dll`); отсутствие подмешивания Qt DLL в общее копирование. Все проверки прошли.
- Повторные configure в одной PowerShell-сессии: v142 → v143 → v143. PATH и INCLUDE после каждого вызова равны исходным. Исправлена утечка окружения, вызывавшая ошибку длины строки при многократном vcvarsall.
- Неполный локальный Qt6.9.1 отклонён на configure с диагностикой отсутствующего Qt6SerialPort. Другая версия Qt не была незаметно подмешана. Окружение восстановлено и после этого неуспешного configure.
- Вариант WebEngine OFF → ON выявил пустой сохранённый moc для UMarkdownWebEnginePage. Его cpp и Q_OBJECT header теперь явно включаются в target только при активном WebEngine; повторная сборка прошла.
- JSON всех конфигурационных файлов и перечисление configure/build/test пресетов проверены. В общем файле 32 пользовательских configure-пресета и одноимённые build/test-пресеты.
- Для v142 + vcpkg Qt6 выполнен **dry run разрешения зависимостей**: все Qt-модули 6.5.3. Полная компиляция этого дополнительного набора не выполнялась.
- Для v143 + vcpkg WebEngine выполнен **dry run разрешения зависимостей**: QtBase/QtTools/QtWebEngine и остальные модули 6.11.3. Компиляция Chromium из исходников в этой проверке не выполнялась.

Логи и JSON результатов находятся в игнорируемом `.build-audit/` удалённого checkout. Использованный временный worker Планировщика запускался независимо от SSH: обрыв прямого соединения не потерял очередь. Последующий контроль выполнялся через jump-сервер 10.245.1.12.

## Практические ограничения

- Настроенные пресеты и выполненные сборки — разные уровни подтверждения. VS2019 как отдельная IDE, VS2026/v145, Linux и полная компиляция v142/vcpkg Qt6 не проверялись. MSBuild проверен полной Release-сборкой с локальным Qt; прочие MSBuild-комбинации подготовлены, но не прошли полный build в этом аудите.
- Первая сборка нового ABI или дополнительного Qt/WebEngine feature всё ещё требует компиляции; бинарный кэш не заменяет отсутствующий пакет.
- Локальный Qt6.9.1 на проверяемой машине неполон: нельзя подмешивать недостающие модули из Qt другой версии или другого provider. Нужно дополнить комплект либо использовать vcpkg Qt.
- Базовый граф приложений включает HardwareLib GUI и QtWidgets даже у Console. Превращение Console в полностью headless core-only продукт — отдельное изменение архитектуры, не задача этого аудита.
- OpenCV/Python/CUDA/TensorFlow/ODE/embedded llama.cpp не включены в обычные пресеты. Их дополнительные конфигурации должны проверяться отдельно после установки соответствующих SDK.
- В исходном C++ остаются предупреждения преобразований числовых типов. Существующая GUI-диагностика ищет имена Qt5 Release-плагинов и может печатать ложные «missing» для Debug/Qt6; фактическая загрузка QApplication и завершение с кодом 0 проверены. C++ диагностический код не изменялся.
- Коммиты сабмодулей должны быть доступны в соответствующих remotes до публикации корневого commit. Аудит не публикует изменения в origin автоматически.

Порядок использования и все команды: [Build-Windows.md](Build-Windows.md).


## Граф модулей и объём проверки

| CMake-проект | Использование и результат аудита |
|---|---|
| Корневой Nmsdk | Пресеты, единые флаги, persistent vcpkg, конфигурационные выходные каталоги, единый test switch |
| Rdk | Qt/core static target; PUBLIC Boost, CURL, glog и Threads; отслеживание добавленных cpp |
| Rdk-BasicLib | Общие компоненты; CONFIGURE_DEPENDS; существующие Unix exclusions сохранены |
| Rdk-CvBasicLib | Native CV/TSNE; единое обнаружение Boost; OpenCV остаётся opt-in |
| Rdk-HardwareLib | Core/GUI Arduino/ESP32, SerialPort/Svg/SvgWidgets; списки arduino сохранены; cpp отслеживаются |
| Nmsdk-MotionControlLib | Core + Qt interface; исходники отслеживаются; существующий NO_MOTION_CONTROL в пресетах сохранён |
| Nmsdk-PulseLib | Core + Qt interface; исходники отслеживаются; ODE opt-in; develop/TimeLearner не подмешан |
| NeuroModeler | Общие link dependencies, AUTOGEN optional header, styles/help, Qt и сторонние DLL |
| NeuroModelerConsole | Общие зависимости ядра и runtime deployment, отдельный ini |
| Rdk/LLM | Core включён в проверенные сборки; CURL/json feature согласованы; embedded llama.cpp выключен |
| Tests и Rdk/Tests | Проверены CMake-включения, test flag, Qt-major, imported GTest targets и пути исполняемых файлов; запуск ограничен указанными программными тестами |

Библиотеки проверены в составе корневого графа Nmsdk, а не как независимые standalone checkouts. Автоматически найденные отслеживаемые CMakeLists.txt исходного состояния:

- `App/NeuroModeler/CMakeLists.txt`
- `App/NeuroModelerConsole/CMakeLists.txt`
- `CMakeLists.txt`
- `Libraries/Nmsdk-MotionControlLib/CMakeLists.txt`
- `Libraries/Nmsdk-PulseLib/CMakeLists.txt`
- `Libraries/Rdk-BasicLib/CMakeLists.txt`
- `Libraries/Rdk-CvBasicLib/CMakeLists.txt`
- `Libraries/Rdk-HardwareLib/CMakeLists.txt`
- `Rdk/CMakeLists.txt`
- `Rdk/LLM/CMakeLists.txt`
- `Rdk/LLM/Embedded/CMakeLists.txt`
- `Rdk/Tests/CMakeLists.txt`
- `Rdk/Tests/Integration/Application/CMakeLists.txt`
- `Rdk/Tests/Integration/CMakeLists.txt`
- `Rdk/Tests/Integration/Core/CMakeLists.txt`
- `Rdk/Tests/Unit/CMakeLists.txt`
- `Rdk/Tests/Unit/Engine/CMakeLists.txt`
- `Rdk/Tests/Unit/Engine/Logging/CMakeLists.txt`
- `Rdk/Tests/Unit/Engine/UComponent/CMakeLists.txt`
- `Rdk/Tests/Unit/Engine/UContainer/CMakeLists.txt`
- `Rdk/Tests/Unit/Engine/UProperty/CMakeLists.txt`
- `Rdk/Tests/Unit/Engine/UStorage/CMakeLists.txt`
- `Rdk/Tests/Unit/Graphics/CMakeLists.txt`
- `Rdk/Tests/Unit/LLM/CMakeLists.txt`
- `Rdk/Tests/Unit/Serialize/CMakeLists.txt`
- `Tests/CMakeLists.txt`
- `Tests/Integration/CMakeLists.txt`
- `Tests/Integration/ComponentSystem/CMakeLists.txt`
- `Tests/Integration/ConfigValidation/CMakeLists.txt`
- `Tests/Integration/GUI/CMakeLists.txt`
- `Tests/Integration/HardwareLib/CMakeLists.txt`
- `Tests/Integration/Libraries/CMakeLists.txt`
- `Tests/Integration/Migration/CMakeLists.txt`
- `Tests/Integration/PropertyConnections/CMakeLists.txt`
- `Tests/Integration/Serialization/CMakeLists.txt`
- `Tests/Unit/CMakeLists.txt`
- `Tests/Unit/Engine/CMakeLists.txt`
- `Tests/Unit/Engine/UEnvironment/CMakeLists.txt`
- `Tests/Unit/HardwareLib/CMakeLists.txt`
- `Tests/Unit/Math/CMakeLists.txt`
- `Tests/Unit/System/CMakeLists.txt`
- `Tests/Unit/System/UGenericMutex/CMakeLists.txt`
