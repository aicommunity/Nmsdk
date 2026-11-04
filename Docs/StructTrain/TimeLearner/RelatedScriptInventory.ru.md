# Дополнение к инвентаризации скриптов

Обнаружен пробел прежнего path-based inventory: расширение.mjs не входило в SCRIPT_SUFFIXES, хотя в Bin есть generate_timelearner_chart_workbook.mjs. Скрипты с нейтральными именами, включая Scripts/audit-probes/generate_probes.py, могут содержать прямые ссылки на TimeLearner и не попадать в поиск по пути. Снимок188 Bin/0 выбранных root остаётся историческим результатом прежнего селектора, не доказательством отсутствия остальных инструментов.

Candidate расширяет поддерживаемые suffixes JavaScript modules/PowerShell modules/Perl/Ruby. Default inventory остаётся schema2 и выбирает по пути. Новый явный --include-related возвращает schema3: выбор по пути либо наличию TimeLearner/StructTrain/NormSync в committed bytes. Для каждой строки сохраняются path_tokens/content_tokens, exact commit/blob/bytes/SHA256. Root production package исключается из исторических migration candidates; его копия в child repository не исключается.

```
python3 -m Scripts.StructTrain.TimeLearner inventory --root ROOT --revision FULL_ROOT_SHA --include-related --output NEW-inventory.json
```

Читаются Git objects корня и записанных gitlinks, а не рабочие файлы или текущие произвольные child HEADs. Ни импорт, ни запуск обнаруженных скриптов не выполняются. Symlinks сохраняются как blob ссылки, без чтения её цели. Comments/string literals могут давать ложноположительные находки. Dynamic imports, computed paths, nonexecutable unknown suffixes, непрямые import chains и внешние callers ещё требуют отдельного анализа. Этот selector — нижняя граница review, а не complete manifest, признак актуальности либо основание для удаления.

Подготовлены15 адресных Git/CLI tests:10 прежних snapshot/integrity cases и5 дополнительных групп с реальными Git trees, JavaScript/PowerShell formats, чтением committed content при изменённом working tree, исключением production package, symlink/unknown-suffix executable handling, schema2/3 CLI и строгим boolean API. Целые исходники Pulse берутся из настоящего pinned repository. Локально проверен только AST; runtime PASS до серверных результатов не заявляется. Ни алгоритмы обучения, ни параметры моделей не изменены.
