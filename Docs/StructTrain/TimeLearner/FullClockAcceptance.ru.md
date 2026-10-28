# Приёмка native regression после исправления absolute-clock sampling

## Проверенный объём

На Elder-1 (Qt5/GCC11) и M40 (Qt6/GCC13) завершены normal full runs
`s07-clock-full-normal-a3`. Native source:

| Репозиторий | SHA |
|---|---|
| Root | `aeff4a9d73c02b7672352ecb1b7a4b1cd8de9224` |
| PulseLib | `967665382687abe82dbfd30ce54b712881ebf04c` |
| Rdk | `1812624ff75c60f03ad57c10b379d3e3848590bc` |

Четыре выбранные maintained группы CTest прошли на каждом worker: три Rdk
группы и PulseLib, 442 cases, 432 pass / 10 helper skips / 0 failures.
Десять skips являются отдельными child roles; реальные parent controls
запускали свежие процессы, их XML сохранены отдельно. Полный parent XML с 442
cases не подменяется XML одного child. Test-only clock seed в full run выключен.

Независимый Python source `75e020f60781b36992174c16dfaf7265b75a1bf1`:
58/58 tests без skips на каждом worker. Проверены completed, stopped, clock,
physical-domain и native-service/assigned-wave evidence. В primary audit:

- 16 completed-state packages / 208 исходных trials;
- 20 stopped-state packages / 66 исходных trials;
- восемь shifted-clock primary probes;
- 81 запись эффективных физических областей, включая unavailable diagnostics.

Unavailable не становится подтверждённой физической областью. SearchUnresolved
и отрицательные сертификаты не превращаются в Exact или scientific PASS.

## Обнаруженная ошибка тестового запуска анализа

Первый Python проход выполнил 40 tests, но setup native-service tests требовал
ровно четыре сводки. Full run содержит ещё восемь cold/configured-service сводок.
Кроме того, assigned-window tests не получили собственную переменную каталога
данных. Исходный failure log сохранён. Исправленный harness требует наличие
каждого из четырёх baseline controls, анализирует все переданные сводки и явно
задаёт assigned-window data directory. Проверки полноты и содержимого данных
не ослаблены. Повторного native расчёта или исправления исходных данных нет.

## Публикация и границы доказательств

[Elder-1 artifacts](../../../Reports/StructTrain/TimeLearner/s07-clock-full-elder1/README.md)
и [M40 artifacts](../../../Reports/StructTrain/TimeLearner/s07-clock-full-m40/README.md)
содержат primary JSON/CSV, модели и storage closure, parent/child XML,
build/runtime manifests и исходный/исправленный Python logs. SHA256SUMS
проверяется и для gzip-файлов, и для распакованного содержимого.

После завершения сверены hashes executable, app ini, compiler и resolved
dependencies. Этот full run не сохранял все actual loaded plugin mappings
живого процесса: resolved dependencies не объявляются полным перечнем runtime
plugins. Адресные ASan проверки и предыдущие runtime-mapping captures сохраняют
свой отдельный source/run scope.

Принимаемый объём включает stopped-state transport, native N1 dynamic domains,
domain schema 2 и абсолютные endpoint comparisons для sampling/coverage.
PulseLib develop merge `32cb44bba481ca5ddb7d54e0288d5fa04695a9bb` опубликован.
Его отличие от tested 96766538 ограничено документацией; native source
деревья Core совпадают. Корневой приёмочный commit фиксирует этот точный gitlink.
Новая recognition conversion API проверялась отдельными адресными runs и не
входила в native root aeff4a9d этого full gate.

Приёмка не закрывает полностью этапы 4–8 или весь план. Открыты полная
physics/mode matrix, N0 repeatability/quantization, остальные search/recovery
проверки, C-trim, PostTune, реальная калибровка, independent scientific Test,
production runner/migration и историческая/контрольная научная матрица.
Связь выявленной sampling ошибки с августовскими результатами не установлена;
визуальные 4/8–6/8 исходного протокола сохраняются как наблюдения.

Корневой develop merge `b62127538694a3442771598420fd78fa7e405c8b` опубликован.
[Свежий recursive checkout M40](../../../Reports/StructTrain/TimeLearner/s07-accepted-closure-m40/README.md),
commit `7f4211bda15740e2886bc94771af7ff3f5478381`, подтвердил все семь точных
gitlinks и чистое дерево. Локально проверены 6 stored / 4 raw hashes. Это
проверка опубликованной source closure, не новая численная сборка.
