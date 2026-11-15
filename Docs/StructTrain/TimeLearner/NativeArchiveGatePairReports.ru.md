# Временные графики двух native archive telemetry контролей

Общий модуль `Scripts.StructTrain.TimeLearner.archive_transfer_reports`
получил явный формат `--input-format native-gate-pair`. Он читает Linux
schema3 native gate с ровно `NativeArchiveTelemetry/At2000` и `At20000`.
Default `legacy16` по-прежнему требует полный прежний16-case корпус;
новый формат не ослабляет эту проверку и не означает её прохождение.

Проверяются actual native.xml IDs/counts/status и его hash из result.json,
completed0/whole bound cgroup closed/loaded runtime из process/result.json,
оба полных100ms окна, 200/2000 native samples, реальные входные импульсы,
все soma/channel samples, effective model identity и storage physics.
Используется прежний production read_case без копирования его алгоритма.
Потеря пробы, несовпадение JUnit, незакрытый процесс или censored observation
не позволяют построить положительный отчёт.

Пример после закрытия исходного задания:

```text
python3 -B -m Scripts.StructTrain.TimeLearner report \
  /path/to/closed-native-job/archive-waveforms \
  --format native-archive-transfer-pair --output /path/to/new-report-cache
```

Графики показывает штатный renderer: physical soma `$.Soma2` исходной модели
и импортированной в свежий процесс, с наложенными фактическими входными
импульсами и читаемыми крупными видами. Обе частоты представлены отдельно.
Это characterization одним импульсом, не пачка Train и не распознавание
восьми паттернов. Другие сомы этим тестом не измеряются; покрытие отчёта
ограничено реально записанной Soma2, а не всем деревом модели.
Output должен быть новым каталогом вне исходных данных и source checkout.
Отдельный module CLI также сохраняется; его default legacy16 не изменён.

В отчёте сохраняется исходная operational diagnostics, включая needs_review;
она не переименовывается в clear. Полный родительский cohort, legacy16,
training certificate и научная классификация этим отчётом не принимаются.
Полный render хранится как кэш M40; в Git идут первичные данные, manifest,
метрики и выбранные рисунки по принятой compact policy.

Одиннадцать проверок reader используют реальную native пару и повреждают её:
unknown schema, false green execution, незакрытая группа, утрата runtime
proof, чужой hash inventory, duplicate/skipped ID, отсутствующий probe и
неполное окно. Дополнительный end-to-end CLI test действительно строит
графики, проверяет hashes и фактические размеры PNG (не менее1600×800),
сохраняя render cache в owned worker TMPDIR для визуального просмотра.
Первый M40 запуск дал10PASS/1FAIL из-за отсутствия matplotlib в системном
Python; отказ сохранён. Повтор A2 на неизменном source
`27c2454ddc34692192a2f5b55c13845666c7e4b8` и тех же25 fixture hashes
прошёл **11/11** за29.764s, completed0/whole group closed, diagnostics clear.
Использован отдельный copied Python interpreter с ранее установленными
matplotlib3.9.4/Pillow13.0.0; общий plot-venv-a1 не менялся.

## Проверенные рисунки

Оба исходных1920×960 PNG просмотрены: подписи и шкалы читаемы, входной импульс
виден, исходный и импортированный отклики накладываются. В каждой паре
амплитудная шкала общая; между частотами шкалы различаются. Амплитуды на
2000/20000Hz также различаются: этот контроль доказывает перенос внутри
одной частоты, а не сходимость интегратора по timestep.

`N=1` в этих диагностических рисунках означает один предъявленный поток;
это не утверждение о числе дендритов всей модели. Показана реально записанная
Soma2. Окно100ms полностью записано, но хвост на его конце ещё ненулевой:
возврат к rest-state и отсутствие более поздних LT events здесь не проверяются.

![Перенос при2000Hz](../../../Reports/StructTrain/TimeLearner/s05-repair17-oom-and-report11-m40-a1/selected/overview-2000.png)

![Перенос при20000Hz](../../../Reports/StructTrain/TimeLearner/s05-repair17-oom-and-report11-m40-a1/selected/overview-20000.png)

Все44 вида, включая крупные100-tick окна без downsampling, остаются в
воспроизводимом M40 cache. В Git сохранены только эти два выбранных рисунка
и compressed primary, не полный PNG-набор.

## Доказательства и границы

Evidence `219ceb0c439ef91ce410cf564f9a1dc9f2f63364` опубликован и принят через
merge --no-ff. [Primary](../../../Reports/StructTrain/TimeLearner/s05-repair17-oom-and-report11-m40-a1/primary.tar.xz)
содержит414 originals/1796972 bytes; с выбранными рисунками Git-pack2095006 bytes.
Сохранены исходный native12/17+OOM, оба Python attempts, включая отказ A1,
все условия и process/source/runtime records. Оригиналы и весь cache на M40
не удалены. [Независимая сверка](../../../Reports/StructTrain/TimeLearner/s05-repair17-oom-and-report11-root-observation/independent-check.json)
проверила414 hashes,4074 compiled-source files,652 reader и650 runner blobs,
реальные JUnit IDs, оба Python outcomes и hashes/размеры выбранных PNG.
Локально модели и численные тесты не запускались.

Capture выполнен явно для closed OOM случая: production native collector v1
не поддерживает missing-JUnit OOM. Его приёмка не объявляется выполненной;
outer cgroup самого capture отдельно не аттестован (false сохранён).
Это не меняет проверенную closure исходных native/Python groups и released leases.
Полный17-case package gate, legacy16 regression нового reader, Elder reader
и исходная научная матрица остаются открытыми.
