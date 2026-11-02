# Аудит ссылок на проблемную Elder рабочую копию

Продолжение [диагностики Bin alias](SourceWorktreeIdentity.ru.md). У ранее
использованной `source-n1-measured-refinement-normal-a1/Bin` Git проверял другой
checkout, а в запрошенном каталоге отсутствовали tracked files. Исправление
текущего checkout не подтверждает его прежнее содержимое задним числом.

Production tool `source_reference_audit.py` читает immutable Root Git tree в
`Reports/StructTrain/TimeLearner`, обычные metadata/code/log files и metadata
members primary.tar.xz. Для matching lines сохраняются номера и SHA256,
без публикации произвольного содержимого строк. Отдельно помечаются resource
root references, source bindings в коде, пути в логах и ссылки отчётного текста.
Скрипт не делает checkout и не выполняет исторический код. Каталог/commit
проверяются через native Git, включая соответствие requested repository/toplevel.

```text
python3 -m Scripts.StructTrain.TimeLearner.source_reference_audit \
  --root REPOSITORY --revision FULL_ROOT_SHA \
  --needle source-n1-measured-refinement-normal-a1 --output NEW_AUDIT.json
```

Ссылка на каталог не доказывает actual file reads; отсутствие буквальной ссылки
не доказывает отсутствие влияния. Вычисляемые/escaped имена, CSV и изображения,
вложенные archives, слишком большие/нечитаемые metadata не объявляются
проверенными. Лимит64MiB на blob/member отмечается явно как unknown; oversized
Git blobs дренируются без загрузки целиком. Сведения о source SHA и semantic
model identity должны проверяться отдельно. Scientific verdict не создаётся.

Первый снимок для анализа — опубликованный accepted Root422647a2d. Серверные
повторы, проверка результата и классификация затронутых source claims пока
ожидаются. Нельзя автоматически отменять прежние измерения либо объявлять их
полностью подтверждёнными по результату этого текстового inventory.
