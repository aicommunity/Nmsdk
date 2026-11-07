# Подготовка дополнительного Windows worker

Пользователь разрешил попробовать сборку и, после проверки, эксперименты на
`user@10.245.1.14`. Вход по существующему SSH-ключу проверен напрямую. Это
дополнение к двум обязательным Linux workers, а не замена их приёмки.

## Фактическая машина и исходники

- DESKTOP-RV8IOD6, Windows 10 Pro 10.0.19045, Ryzen 7 5825U, 8 cores/16 threads.
- ОС видит 14578136 KiB RAM; при подготовке свободно около 4.5 GiB.
- Диск C: около 1.83 TB свободного места при первоначальной проверке.
- VS2026 18.11.12328.437, MSVC 14.51.36231; VS2019 также установлен.
- В VS2026 есть CMake 4.3.1-msvc1 и Ninja. Системного Python пока не подтверждено:
  найденный в PATH python.exe — WindowsApps alias, не доказательство интерпретатора.
- `C:/vcpkg`, чистый commit `1577f17ee57f42a0ef6d75bbb82cb37d0b76d7e8`;
  первоначально установленных пакетов нет.

Пользовательская копия `C:/Projects/Nmsdk` чистая, root master
`8a723d07ff22bbcc75351457400e3c9e5c8ed1d1`. Её root/child checkouts не менялись.
Обычный Git SSH к origin отклонил public key; настройка Fork не изменялась.
Код доставлен native Git pack-objects/index-pack в отдельные private Git repos,
без alternates, с sparse checkout. Это не файловая синхронизация исходников.

Проверяемый root `e7ee7d1cad5128a1a22c3cc6e118eaaaea29a543`, каталог
`C:/Projects/TimeLearnerWorker/source-e7ee7d1ca-a1`. Он содержит новый
[dependency profile](../../../Scripts/StructTrain/TimeLearner/workers/windows-vs2026/README.md).
Rdk `10e9d05aa658dd2203c89bc84ba9166595b50014`, PulseLib
`c17ebd2cc75abd3a1562492907c90782232c2ea6`, Bin
`b4f66eb137d3e1c19539890dbdee06faa3e1020b`; остальные child HEAD соответствуют
точным root gitlinks. Root App/Tests/cmake/CMakeLists совпадают с compiled E91
размерной матрицы; Core Pulse c17/217 имеет одинаковый tree
`5f0a5e8e1ae9c76acdae0d211f390410247968bd`. Это source identity, не Windows PASS.
Bin checkout исключает Configs/Platform/Help и пока предназначен для сборки,
а не готового научного runtime. Docs/Reports blobs не материализуются.

## Постановка сборки

Qt5 соответствует текущему Linux контуру. Отдельный vcpkg manifest закрепляет
registry и включает base/charts/svg/serialport, Boost, Curl, Eigen, glog, GTest.
Release-only target x64 DLL triplet. Host triplet в первой попытке остался
native x64-windows: его tool dependencies собираются Debug+Release отдельно,
что видно по OpenSSL/Qt5 logs. Это не Debug DLLs приложения и не общая
Release-only сборка всех host packages. Не включены optional WebEngine/OpenCV/Python/LLM;
это build options, не изменение нейронной физики. CMake конфигурирует настоящий
проект с BUILD_TESTING=ON. Цели: NeuroModelerConsole,
Test_PulseLib_ProbeAlgorithms и Test_PulseLib_StorageComponents.

Новые outputs: build-a3, runtime-a3, bt-a3/pkg-a3 внутри TimeLearnerWorker.
Параллелизм vcpkg/CMake/Ninja ограничен единицей. Preflight: минимум 3 GiB
available RAM и 100 GiB свободного диска. Жёсткая Windows memory quota и
научный scheduler пока не реализованы и не заявляются. Сборка исполняется в
наблюдаемой SSH-сессии, дочерний cmd запускается со скрытым окном.

Попытка `windows-bootstrap-a3`: owner PowerShell PID412, start UTC
2026-11-07T12:00:02.966Z; cmd PID6368, start UTC12:00:05.505Z. Регистрация:
`C:/Projects/TimeLearnerWorker/jobs/windows-bootstrap-a3`. На последней живой
проверке подтверждены owner/cmd/CMake/vcpkg/compiler processes и установка
зависимостей; configure/build verdict ещё отсутствует. Не перезапускать по
обрыву наблюдения: сначала проверить именно этот process tree и outputs.

Первая длинная EncodedCommand не исполнилась из-за Windows command-line limit.
Затем сохранённый A1 script не начал работу из-за execution policy. Для A3
использован process-only параметр PowerShell ExecutionPolicy; постоянные
настройки системы не менялись. A2 остановился до CMake: функция оболочки Git
затенила git.exe и рекурсивно вызвала себя. В A3 она переименована, используется
git.exe, отдельные outputs; A2 terminal/exception сохранены. Это ошибки
подготовки, не дефекты C++ проекта и не неуспешные научные эксперименты.

## До допуска к экспериментам

Нужны реальный configure/build и JUnit, проверка зависимых DLL и native
lifecycle/storage/response, полная модель Train→Test, временные окна и frozen
identity. Действующие process containment, runtime capture (/proc), leases и
publication pipeline ориентированы на Linux. Их нельзя объявлять Windows
совместимыми по одному успешному compile либо отключать проверки ради запуска.
Нужно отдельно подтвердить Windows process ownership/cancellation и provenance.
Сравнение Windows/Linux чисел не получает нового допуска автоматически.

На этом снимке Windows научным worker ещё не принят; новые научные результаты
на нём не получены. Полный исходный план остаётся активным.

Дополнение наблюдения: OpenSSL target/host builds завершены,13:01UTC живы
те же owner412/cmd6368 и их CMake/vcpkg/MSVC descendants. Собирается Qt5.15.19
host Debug; available RAM6182412288B, disk free1826246479872B. Конфигурация
самого Nmsdk ещё не завершена. vcpkg также установил private tool Python3.14.2
в downloads/tools; это не установка Python пакетов scientific pipeline.


## Фактическая компиляция и следующая попытка

Обновление15:37UTC: A3 завершён. Все зависимости установлены, CMake configure
прошёл. Ninja дошёл до450/495 и остановился в DatasetClock fixture: параметр
`near` раскрывается Windows macro, приводя к C2059/C2143. Это реальная
несовместимость исходного теста с MSVC, не численная ошибка модели. Исправление
`4b4f32262e958bd8c8a0462188fadc0de2aa59b6` переименовывает только параметр
в `nearGrid`; значения, тестовые случаи и алгоритмы не меняются. A3 журналы
сохранены. Поле ExitCode его PowerShell producer оказалось null; это не нулевой
код и не успех. Compiler errors/Ninja stop и terminal false сохранены.

A4 использует новый source `C:/Projects/TimeLearnerWorker/source-4b4f32262-a4`,
новые build/runtime/bt/pkg-a4, те же точные gitlinks и vcpkg registry. Код и
дочерние репозитории доставлены Git packs, пользовательская копия не изменена.
Конфигурация прошла за счёт доступного dependency cache. Свежий CIM подтвердил
owner8720/cmd11516/CMake/Ninja/MSVC;15:45UTC журнал достиг14/495. Это ещё не
успех сборки и не JUnit. Прямое подключение .14 дало timeout, но SSH по тому же
ключу через .12 работает; проблема наблюдения не использовалась для повтора A3.

Сборка и научный допуск остаются разными приёмками. Даже после успешной
компиляции нужны native tests, Windows runtime/provenance и ownership/cancel.
