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
python3 -B -m Scripts.StructTrain.TimeLearner.archive_transfer_reports \
  --input-format native-gate-pair \
  --input /path/to/closed-native-job/archive-waveforms \
  --output /path/to/new-report-cache --plots
```

Графики показывает штатный renderer: physical soma `$.Soma2` исходной модели
и импортированной в свежий процесс, с наложенными фактическими входными
импульсами и читаемыми крупными видами. Обе частоты представлены отдельно.
Это characterization одним импульсом, не пачка Train и не распознавание
восьми паттернов. Другие сомы этим тестом не измеряются; покрытие отчёта
ограничено реально записанной Soma2, а не всем деревом модели.

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
Новые тесты и CLI требуют серверной приёмки; на момент
подготовки кода она ещё не выполнена.
