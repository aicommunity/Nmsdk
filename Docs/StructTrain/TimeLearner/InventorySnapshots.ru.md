# Инвентаризация точного Git-снимка

Статус: кандидат, серверная проверка ожидается. Это source/metadata audit,
не численная проверка learner и не завершение всей semantic/property matrix.

Прежний inventory schema1 смешивал `HEAD` в provenance, `git ls-files` текущего
индекса и working-copy headers/sources. Незакоммиченный либо просто иной child
HEAD мог дать смешанный каталог. Старые source_inventory/property/evidence
JSON сохраняются как исторические snapshots; новая версия их не перезаписывает.

Schema2 читает root commit и **его записанные gitlinks** Bin/PulseLib. Все
пути и content hashes берутся из `ls-tree`/Git blobs. HEAD и tracked status
рабочей копии выводятся отдельно, вместе с checkout_matches_snapshot. Отсутствующий
точный commit либо worktree alias запрещает каталог. Silent fallback к доступному
child HEAD не выполняется. `--revision` принимает полный root SHA; без него
используется текущий root HEAD.

Properties извлекаются тем же balanced source parser, что property_drift:
четыре immutable header/source blobs, actual registration names, setter body
hashes и ограниченные телом ADefault mentions. Новый inventory не объявляет
все прежде рассмотренные свойства снова семантически непроверенными: поле
semantic_review=not_inferred_by_inventory. Нормативны PropertyReview и адресные
контракты/receipts. Значения defaults не объявляются эффективной child physics.

Каталог включает именованные suffix tools, `.bash`, executable shebang files
без расширения и symlink candidates с явной пометкой. Выбор по пути всё ещё
является нижней границей: imports/callers и файлы вне известных тематических
путей требуют отдельного review. Untracked/ignored files и inherited Rdk
properties не входят в этот committed catalog. Исторический код не исполняется.

Команда:

```text
python3 -m Scripts.StructTrain.TimeLearner inventory --root ROOT \
  --revision FULL_ROOT_SHA --output NEW_INVENTORY.json
```

Проверки используют настоящие Git repositories и целые четыре Pulse source
files точного donor commit, а не извлечённые тела функций или замену модели:
staged/dirty scripts, иной child HEAD, испорченный working header, старый root
revision, repository alias, отсутствующий child commit, Unicode/shebang и
production CLI. Сходимость, lifecycle и весь этап1/9 этим не принимаются.
