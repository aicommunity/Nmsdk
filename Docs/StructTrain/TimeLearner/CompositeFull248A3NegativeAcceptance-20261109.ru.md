# Baseline A3: независимо проверенный отрицательный результат

Evidence `a7dae002295800d520b1fd35975283f0daa2362d`, origin branch
`codex/timelearner-native-acceptance-full248-m40-a3-negative`,
[primary archive](https://github.com/aicommunity/Nmsdk/blob/a7dae002295800d520b1fd35975283f0daa2362d/Reports/StructTrain/TimeLearner/s07-composite-cancellation-m40-asan-a3/primary.tar.xz).
Root повторно выполнил metadata-only verifier и получил ту же
[квитанцию](../../../Reports/StructTrain/TimeLearner/s07-composite-cancellation-m40-asan-a3-root-verification/independent-verification.json)
SHA256 `eb2ae97128d03571c16b72adbfa6368759852ade98a53b1b8f92fe0139655336`.

Результат: **231 actual completed =230 PASS +1 FAIL;17 not run**.
Падение — `NativeCompositeDeclarations/ClassicCold6AndProtocol4StrictRoundtrip`,
`invalid_native_configuration_number`. Все42 новых callback/cancellation,
исходные20 service, archive23 и оба20k capture/search/final прошли; весь248
не принят. Исходный return1 сохранён, cleanup не превращён в execution success.

Проверка подтвердила3972 archive members/1481568 compressed bytes,3719 Git файлов
восьми репозиториев, фактический binary inventory1624 и заявленный subset248.
Внешняя группа и121 recorded leaf закрыты,122 exact kernel bindings связаны
с исходными requests/invocations/PID-start identities; lease released. Нет
guard/heartbeat/final-capture ошибок. Source/cache/runtime и восемь protected
roots сохранились; сопоставлены семь полных cache entries, шесть global/link
entries и generated flags. [Реестр источника и привязок](TypedCompositeTrainingJobs.json).

Все68 primary rules проверены collector самостоятельно, поскольку successful
worker loop после failing leaf не выполнился: **42 fulfilled,26 missing**.
Missing относятся к ещё не запущенным growth/source guards; они не дорисованы.
Шесть native bundles содержат26 records/101 CSV reference с проверенным
embedded/external/base64 byte equality, sidecars и native XML/identity hashes.
Это transport/provenance verification, не повторный локальный численный анализ.
Локально не запускались C++, unittest, поиск пиков, waveform или физика.

Во всех шести cold6 configurations `base_schema_version` — строка `sample0`;
[точная forensics](Cold6ActualEnvelopeForensics-20261109.json). Поэтому config и
semantic archive-reader acceptance остаются false. Правильность raw waveform
не отвергается автоматически; архивы сохраняются как первичные данные с
ошибочной source-configuration sidecar. Исправлять JSON на месте нельзя.

Первый collector остановился до publication stage: sorted JSON object keys
изменили порядок реконструированных selections. Диагностика доказала равенство
файлов/closure/ID set; следующий collector восстановил порядок по authoritative
inventory.ids и получил точное равенство. Обе попытки сохранены. Первая download
попытка также не считалась завершённой; новый bounded streaming transfer передал
тот же Git pack с проверкой hash. Native job/publisher не перезапускались.

Подготовлен минимальный codec baseline A4 Root
`478cc35c0f1a314c34ad93aa0095b61836c658ec` / Pulse
`4a5c2ec9df9a9f704dcd8260714323494bfa4415`: source-only, ещё без runtime-приёмки.
В нём250 selected IDs = прежние248 +2 focused codec cases; два diagnostic-only
исключены. Предлагается failfast4 codec →16 остальных not-run →230 regression,
с новым actual canonical. Исправление source defects не вносит Train5/token
код в baseline. [Дефект и границы исправления](ColdSchemaJsonProxyFailure-20261109.ru.md).

Закрытая и опубликованная A3 попытка разрешает отдельно рассматривать reuse
idle source/build после fresh no-held-overlap review. Старые runtime/readbacks
и данные A3 должны оставаться защищёнными; никакого нового checkout/build/run
эта квитанция сама не выполняет. Полный план и научная матрица не завершены.
