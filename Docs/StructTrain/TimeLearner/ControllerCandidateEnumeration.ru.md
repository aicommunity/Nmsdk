# Проверка механического выделения candidate enumeration

Кандидат PulseLib03b004aa36121766b8eac3040a282e272b392eb5 группирует состояние
перебора L/Ns/Rs в CandidateCursor. Родитель21435c8d5a11d2670cdc1609757d3a9973877314
является исходным вариантом. Типы/defaults перенесены без изменения. После
нормализации CRLF/LF обратная подстановка cursor.field → field восстанавливает
полный прежний BoundedTraining.cpp. Это не реализация C-search On.

Проверка выполняется отдельной командой корневого пакета:

```text
python3 -m Scripts.StructTrain.TimeLearner controller-ab job.json \
  --root-repository ROOT_GIT --pulselib-repository PULSE_GIT \
  --compiler /usr/bin/g++ --gtest-source GOOGLETEST_SOURCE --output NEW_OUTPUT_DIRECTORY
```

Шаблон: Scripts/StructTrain/TimeLearner/specs/candidate-cursor-ab-v1.json.
В job указывается полный candidate_root SHA; baseline_root зафиксирован.
Оба gitlinks PulseLib читаются из соответствующих root commits. Рабочие деревья
не переключаются; исходники читаются как обычные Git blobs. Компилируются целиком
17 production headers/sources и семь существующих test files,130 cases. Тела
функций не извлекаются и не подменяются тестовыми копиями. Корпус tests должен
иметь одинаковые hashes у baseline и candidate. Native scheduler/model tests
в этот isolated decision gate не входят и не считаются подтверждёнными.

Baseline/candidate имеют отдельные каталоги исходников, executable и journals.
Output запрещён внутри репозиториев. Обе сборки используют одинаковые compiler,
flags, очищенную environment и одну копию оригинального GoogleTest. Его source
берётся из заданного FetchContent checkout: полные include/src файлы сверяются
с точным Git commit и копируются в job. Оба executable собирают эти оригинальные
.cc files; библиотеки активного Nmsdk build не используются. Хранятся
source hashes, compiler/library/header hashes, точные compile/run arguments,
owned PID/start_ticks/boot ID, elapsed wall time, JUnit и строгая проверка полного
уникального test inventory. Timeout завершает только собственную process group.
Ненулевой exit не становится PASS, отсутствие/skip/unfinished test не принимается.
Фактически загруженные mappings быстрого unit executable не захватываются;
resolved libraries не объявляются actual loaded closure.

Сборки/запуски разрешены только на указанных Elder/M40 через jump host.
Локально выполнены AST/declaration/diff проверки. Серверный A4 A/B прошёл:
130/130 tests на каждой стороне; строгие результаты и hashes проверены независимо.
Результат130/130 с обеих сторон подтвердит этот корпус pure decisions. Он не
доказывает полную operation-trace equivalence, Rdk integration, C-trim, качество
распознавания или выполнение всей матрицы исходного плана. Перед приёмкой нужны
также соответствующие native regressions и общая согласованная Git closure.


Первый a1 worker не запускал CLI: historical proof checkout оказался sparse без
PulseLib. A2 использовал private bare object store, но остановился до компиляции
из-за отсутствия системного libgtest_main.a. Это ошибка предположения runner,
не отказ алгоритма. Evidence849cb6e8b446982c288ac7f437598a6638949ecf сохраняет
not_accepted и обе причины; эти попытки не объявляются numerical runs. Кандидат
runner исправлен на explicit Git-verified GoogleTest source, runtime ещё ожидается.


A3 обе стороны остановились на одинаковых двух relative include errors:
FinalVerification/ProbeObservation tests ожидают штатный root/Libraries/PulseLib
layout. Evidence da3612b95ec70d34f638b626fa41d9102bce74de сохраняет обе compiler
диагностики. Исправление runner размещает целые исходные файлы в реальной структуре
корень/сабмодуль, не меняя include directives или test bodies. Успех130/130 пока
не заявляется; повторный A/B должен проверить исправленную production CLI.


## Подтверждённый A4 срез и следующая native проверка

Root c04850a81bb7f1918519d72bc4c18214438d9ed0, baseline root2194eeadcb3f29e1b2047ae1bcf3e6e7e48e4747.
PulseLib baseline21435c8d5a11d2670cdc1609757d3a9973877314 → candidate03b004aa36121766b8eac3040a282e272b392eb5.
Evidence bcdae6c4985310850f89356a072ca80b3cbe7ca3:36 members,45377 compressed bytes.
Независимо сверены346 Git source hashes, оба JUnit inventories130/130 без failures,
errors/skips и одинаковые семь test files. Обратная подстановка cursor.field в
production .cpp точно воспроизводит baseline после CRLF/LF normalization.
Принят только этот pure-decision corpus. Native/Rdk integration и полная
operation-trace equivalence пока не подтверждены; C-search не включён.

Для native H10 зафиксирован root f5845fb78d906f9e7d95a55a8b0c217a73fa281c.
Elder supervisor546230/start_ticks326149080 и publisher546231/326149080 проверены
живыми; readbacks s07-candidate-cursor-native-normal-h10 и
s07-candidate-cursor-native-publication-normal-h10. Очередь ждёт успешный baseline
H9b209/87 и освобождение его source/build, затем выполняет209 native tests и104
reader checks. Включены ранее исправленные17 диагностических/certificate controls.
Отдельно требуется точное совпадение наборов и SHA256 детерминированных primary CSV
Classic/Branch N0/N1 automatic service и capacitance bridge с H9b baseline.
Receipt сохраняет все имена/hashes и любое различие запрещает приёмку. Текущий
H10 ещё не запускал сборку; дополнительные неучтённые сбои baseline останавливают
переход. До native/ASan приёмки изменения не объединяются в develop.
