# Компактные первичные артефакты и воспроизводимый кэш графиков

Пользовательская политика от 30.10.2026 заменяет хранение всех PNG/SVG/PDF
каждого gate в исходном Git. Читаемость, полнота первичных данных и полный
графический отчёт сохраняются. История уже опубликованных пакетов не очищается.

Первый адаптер обслуживает native test run с явным 51-case/26-phase контрактом.
Это не полный production runner экспериментов и не универсальный trained-state
codec: он архивирует существующие model packages побайтно.

```text
python3 -m Scripts.StructTrain.TimeLearner bundle pack-native-tests CONTRACT.json --artifacts IMMUTABLE_READBACK --selected-report COMPLETE_CACHED_REPORT --output NEW_COMPACT_BUNDLE
python3 -m Scripts.StructTrain.TimeLearner bundle verify COMPACT_BUNDLE
python3 -m Scripts.StructTrain.TimeLearner bundle extract COMPACT_BUNDLE --output NEW_EXTRACTED
```

Bundle содержит детерминированный `primary.tar.gz`, manifest по каждому
uncompressed file, source/runtime provenance, проверенный expected contract
и выбранные PNG. Перед pack проверяется весь native inventory. Все файлы
`native/` сохраняются, включая модели, конфигурации, references/certificates,
warm/stopped records и CSV. Root terminal/runtime/source records сохраняются
как provenance. Каталоги с производными figures в архив не включаются.

Выбранные previews читаются из явного cached-report QA manifest. Проверяются
hash PNG и source PDF, полное совпадение native inventory, exact group/probe
origin, исходный JSON (включая `/probe`) и CSV hash. Равенство trial IDs не
позволяет подменить источник. PDF и все остальные zoom images остаются в cache.

Распаковка сначала проверяет checksum архива, expected members, размеры и
SHA256 каждого payload; запрещены traversal, абсолютные пути, дубли и links.
Проверяется extraction budget (default 8 GiB; явно настраивается), checksum
выбранных рисунков и отсутствие прежнего output. Payload записывается вручную
с mode 0644 без вызова `extractall` или исполнения provenance scripts.

Для полной регенерации на M40 используется версия renderer из
`manifest.render_recipe.renderer_root`, записанные Python/matplotlib/backend
и следующая команда из чистого source checkout этой версии:

```text
python3 -m Scripts.StructTrain.TimeLearner report NEW_EXTRACTED/contract.json --format native-test-run --artifacts NEW_EXTRACTED --output NEW_FULL_CACHE
```

Рекомендуемый cache root: `/media/user/Data/TimeLearnerRefactor/report-cache`.
Конкретный путь не является scientific identity и не заменяет данные в Git.
Primary bundle receipt, numeric validity, training outcome, cache completeness,
scoped visual review и scientific verdict остаются разными осями. Для новых
полных cached reports проверяется coverage всех ожидаемых trial/soma пар;
выбранные Git figures являются только контрольной выборкой.

Реализация и адресные tests пока находятся в рабочей ветке. До серверных
roundtrip/corruption checks и реальной регенерации эта спецификация не является
объявлением завершённого перехода всей инфраструктуры на компактную политику.
