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
  --compiler /usr/bin/g++ --output NEW_OUTPUT_DIRECTORY
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
flags, очищенную environment и явно разрешённые static gtest libraries. Хранятся
source hashes, compiler/library/header hashes, точные compile/run arguments,
owned PID/start_ticks/boot ID, elapsed wall time, JUnit и строгая проверка полного
уникального test inventory. Timeout завершает только собственную process group.
Ненулевой exit не становится PASS, отсутствие/skip/unfinished test не принимается.
Фактически загруженные mappings быстрого unit executable не захватываются;
resolved libraries не объявляются actual loaded closure.

Сборки/запуски разрешены только на указанных Elder/M40 через jump host.
Локально выполнены AST/declaration/diff проверки; серверный A/B ещё ожидается.
Результат130/130 с обеих сторон подтвердит этот корпус pure decisions. Он не
доказывает полную operation-trace equivalence, Rdk integration, C-trim, качество
распознавания или выполнение всей матрицы исходного плана. Перед приёмкой нужны
также соответствующие native regressions и общая согласованная Git closure.
