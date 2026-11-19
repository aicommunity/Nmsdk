# Windows: серверная проверка физической DATA из terminal8

Статус: компиляция/линковка закончились с returncode0; исходная сборка
сохранена как `descendants_remaining`, build_accepted=false. Вся группа закрыта.
Независимый closed-build audit прошёл:5092 source files,17287 dependency files,
62 runtime files. Native78 завершён:59 PASS,19 FAIL, без пропусков;
все78 объявленных ID присутствуют, kernel Job отсутствует и task instances пусты.
Новый SDK не принят, Python3 не запускался. Это работа этапа5;
научные N4 Train на M40 и Elder продолжают использовать прежние runtime.

В первом native78 новые solo DATA fixtures оставляли включённый Default
EnablePostTrainTuning=true и получали штатный отказ configured-owner Build.
Причина относится к настройке нового тестового owner. Исправление выключает
незаявленные optional phases до Install/Init и немедленно проверяет
NativeModelEditFailure; guard и waveform tolerances сохраняются. Первый
прогон сохранён как отрицательный; исправление ожидает нового полного прогона.
Два дополнительных rollback failures показывают Copy mismatch DebugSysEventsMask:
32-битный atoi в общем XML integral reader Rdk не сохраняет unsigned4294967295
на Windows. Ещё один failed-attachment test исчерпал10s wall до нужного edit.
Общее исправление Rdk cb6fe50da94ca9cbc9d5e4c0811d42b37b44a14a,
три regression cases и бюджет30s инженерной fixture подготовлены;
их серверная проверка ещё нужна. Новый inventory81 сохраняет все исходные78.
Подготовленная A2 только с fixture fix не собрана и не является приёмкой.

## Точная область

- Compiled Root:7047c695dbf33c9a2901e4209f9425ca727085e8.
- PulseLib:0cf335ae08347f2d042d7eb3f5d05ef70a55789c.
- Worker:user@10.245.1.14 через10.245.1.12; только
  `C:/Projects/TimeLearnerWorker`. Пользовательский проект не изменяется.
- Source:`source-terminal-physical-data8-win-a1`;5092 проверенных Git files,
  восемь согласованных репозиториев, без alternates и незакоммиченного кода.
- Controls:d8922a5df0624034e086f54ff2473782508b35aa;
  namespace Git blob24c8c2ecc240c04146d84b52e4e175319d7d8f62;
  build specification blob b18337bd06e1d59dd2703095c41763c3d3309dca.
- Отдельные `build-terminal-physical-data8-win-a1` и
  `runtime-terminal-physical-data8-win-a1`; output
  `jobs/windows-terminal-physical-data8-sdk-build-a1`.

Сборка штатным `workers/windows-vs2026/sdk-build.py`: VS2026/Qt5/Release,
один compiler job,4GiB Job memory,32 processes,7200s wall. Установка зависимостей
отключена; существующие vcpkg dependencies и build tools сравниваются до/после.
Никакой работающий runtime не обновляется.

## Проверки после сборки

1. Сохранить исходный build outcome и проверить отсутствие всего kernel Job.
   Для `descendants_remaining` используется отдельный штатный closed-build audit;
   отрицательный исход сборки не превращается в положительный. При обычном
   `completed` нужен путь, принимающий именно подтверждённую успешную сборку.
2. Запустить полный объявленный native78 того же состава, что Linux A8.
   Все78 IDs присутствуют на Windows; platform exclusions в этой когорте нет.
   В16 существующих configured-completed/actual-restored cases добавлены
   настоящие DATA export/import и source/DATA burst waveform comparisons.
3. Выполнить3 метода `test_terminal_physical_data_native` по всем16 фактическим
   fixtures. `TIMELEARNER_NATIVE_TERMINAL_CONFIGURATION9` указывает на
   `native-gate/native-composite`. Проверить каждый исходный отсчёт,
   destination Idle/epoch0, отсутствие перенесённого certificate и source-only
   frozen DATA без соседней истории. Подтверждения из диагностических флагов
   не заменяют пересчёт записанных данных.
4. Проверить actual frozen Console и неизменность recognition graph/параметров.
   Сравнение waveform полного source и DATA новой версии, последующая Linux
   приёмка нового SDK и реальный N4 eight-pattern Test остаются обязательными
   до научного использования нового пути на соответствующем worker.
5. Опубликовать полный закрытый primary в центральном M40 archive; в корневом
   Git оставить только код, документы и компактные квитанции.

Допуск сравнения source/DATA≤1e−12 относится к переносу. Он не заменяет
амплитудный1e−5 или SyncTolerance0.02 обучения. CapturedPerInput, закрепление
пика, N0/N1 и бюджеты научных опытов этим изменением не меняются.
Standalone solo DATA не передаётся публичному frozen importer: нужны штатный
prepared graph installer либо явное преобразование solo→recognition.

## Подготовка и доказательность

Root/Pulse получены прямым shallow filtered Git clone; шесть неизменных
репозиториев восстановлены из ранее проверенных Git object projections.
Перед чистым source readback получены штатные Git policy objects. Все5092
видимых файла проверены по Git blob, размеру и SHA256; namespace содержит
политики Git и не содержит тяжёлых результатов корневого Reports.

Первоначальный preparer и первый resume завершились ошибкой `Bin git status`.
Последующий независимый readback подтвердил точный HEAD и чистое дерево.
Причина первоначального отказа отдельно не доказана; первоначальные outcomes
сохранены. В controls записаны оба оператора, preparation-failure и проверка
Git policy objects. Это подготовка нового приватного дерева до сборки,
не изменение исходов какого-либо научного опыта.

[Точные dispatch и kernel handles](../../../../../Reports/StructTrain/TimeLearner/TerminalPhysicalData8-20261119/windows-sdk-running.json).
[Закрытие сборки и отдельный artifact audit](../../../../../Reports/StructTrain/TimeLearner/TerminalPhysicalData8-20261119/windows-sdk-closed-audit.json).
[Native78: объявление и живой процесс](../../../../../Reports/StructTrain/TimeLearner/TerminalPhysicalData8-20261119/windows-native78-running.json).
[Native78: закрытый отрицательный исход](../../../../../Reports/StructTrain/TimeLearner/TerminalPhysicalData8-20261119/windows-native78-closed-negative.json).
Полная семантика и незакрытые проверки: [контракт terminal8 DATA](../../TerminalPhysicalData8-20261119.ru.md).
