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

На source `675cc30bd3bbeddb2cda52d7e6b1df9c79f63b80` оба workers выполнили
10/10 addressed tests без skips/errors/failures и 5/5 реальных learned/stopped/
warm checks после CLI extraction. Pack/verify/extract CLI завершились с 0;
pack с budget 1 byte дал ожидаемый status 2 без создания output. Изменение
только metadata при неизменном raw archive также выявляется общим checksum
manifest; объявленный budget применяется и к созданию архива.

Компактные Git-пакеты:
Elder `4f2cace7774bb924b5ef459f36194fb43d7cfa6a` — primary bundle 4305162 bytes,
raw archive 3564176 bytes (920 files / 63724437 uncompressed bytes);
M40 `cea2df871ff34fe9f027e513e8bae065e5691899` — primary bundle 4309587 bytes,
raw archive 3568715 bytes (919 files / 63697162 uncompressed bytes).
Каждый содержит шесть выбранных PNG и все первичные 338 probes / 507 pairs;
разница числа provenance files не означает потерю expected native trials.
Проверены локально все 34 outer и 8 inner stored hashes каждого пакета.

Full-cache regeneration запущена на M40 отдельно, из A1 archive с SHA,
побайтно совпадающим с A3. Ожидаются все 338 probes / 507 pairs и сравнение
3087 PNG с исходным cache. Полные generated files не будут опубликованы снова;
в Git сохраняется только regeneration receipt. Итог этого job пока не принят.

Regeneration завершилась с status 0. Извлечённый archive
`c48d8232ec77f6bd98f26fb152544031a0cdbe3cddc4e8fdff5ebaf533fd2b81`
дал все 338 probes / 507 pairs; все 3087 PNG совпали с исходным M40 report
побайтно. Три full graphical readback tests прошли без skips/errors/failures.
[Малый receipt](../../../Reports/StructTrain/TimeLearner/s10-compact-regeneration-m40-a1/README.md)
`15279ce361225406f8bc9809be7eeb54056e9e38` опубликован отдельно;
большие generated files в него не включены. Это один реальный full regeneration
на M40; отдельный второй full render из Elder archive не заявляется.
Первичные roundtrip и corruption проверки выполнены на обоих workers.

Это приёмка первого native-fixture bundle/cache пути. Полный experiment runner,
остальные historical adapters, migration старых caches и вся physics/mode matrix
не считаются завершёнными. Ранее опубликованные тяжёлые ветки не объединены
в source develop; их история сохраняется без изменения.

Для быстрого просмотра выбранных изображений добавлены небольшие wrapper
`index.html` в обоих компактных report directories: изображения имеют ширину
1920 px, horizontal scroll и прямую PNG ссылку. Wrapper manifest обновлён с
34 до 35 hashes; сам primary bundle и его восемь внутренних hashes не изменены.
