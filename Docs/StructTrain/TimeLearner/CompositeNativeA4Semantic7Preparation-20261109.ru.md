# Actual A4: адресный semantic reader gate7

Статус: только локальные metadata descriptors, подготовленные для review. Тесты, semantic replay, графики, model imports, серверная discovery/запись и fixture materialization не выполнялись. Это отдельный узкий шаг portable reader; не полная приёмка stage3/5, package/CLI или научная приёмка.

## Источник и actual primary

Tool и проверяемый Python source: `cec33f2fcceb8c8f815e3494173bf48dcd39ed6c`. В CEC ровно441 Python files пакета TimeLearner; fingerprint по Git bytes: `629bd6fe86318b5e38251ab4f822a07d01debf4c8a9ab3d88a8896c0636de20d`. Существующий серверный source path из неизменённого accepted27 request — `/media/user/Data/TimeLearnerRefactor/source-channel-lt-overview-tool-m40-a2`; его актуальная чистота, Git bytes, canonical path и interpreter должны быть проверены заново read-only. Прежние27 проверок не повторяются по привычке и не подменяют новый semantic gate7.

Actual A4: Root `478cc35c0f1a314c34ad93aa0095b61836c658ec`, Pulse `4a5c2ec9df9a9f704dcd8260714323494bfa4415`; опубликованный primary commit `b4feb38aeed9940c4292b532b3de0e3ab853685e`. Archive `Reports/StructTrain/TimeLearner/s07-composite-cold6-m40-asan-a4/primary.tar.xz`: 1,836,352 bytes, SHA256 `15b990e1825f7aaac51dfd7a252215253a429df871c02c418ccb25cc8dc25008`,4551 members. Native250 PASS не является результатом этих новых Python проверок.

Выбран ровно prefix `s07-composite-cold6-m40-asan-a4/worker/cold6-regression-archive-native23/native-composite/`. Все157 выбранных members — regular files; размеры и SHA256 каждого совпали с опубликованным bundle. Здесь считались только hashes/размеры/структура архива: CSV значения не разбирались и алгоритмы reader не вызывались.

| Actual case | Files | JSON / CSV | Bytes |
| --- | ---: | ---: | ---: |
| classic-service |35|11 /24|5,717,959|
| branch-service |35|11 /24|4,389,112|
| classic-partial |7|6 /1|1,858,574|
| branch-C0 |35|11 /24|55,535,231|
| classic-warm |35|11 /24|5,751,050|
| branch-ambiguous |10|6 /4|1,717,652|

Сумма74,969,578 bytes. Все context/index/group/source/model sidecars и CSV сохраняются исходными. Fixture fingerprint: `78f286701300c7d365e16d25bb64fca430a06b23e08b638396249a87b89056db`. Нового seventh/final-sweep bundle, сконструированных traces или восстановленных из ожидаемых assertions записей нет.

## Семь существующих проверок

Существующий модуль `Scripts.StructTrain.TimeLearner.tests.test_composite_native_archive`, класс `CompositeNativeArchiveTest`. ID получены через AST без импорта или выполнения tests:

- `test_actual_six_service_exports_replay_all_retained_primary_and_counters`;
- `test_actual_partial_and_ambiguous_exports_do_not_promote_invalid_measurements`;
- `test_actual_sidecars_match_each_retained_record_without_filename_identity_claim`;
- `test_actual_existing_C0_and_warm_accounting_are_retained`;
- `test_supplied_external_mirror_cannot_fall_back_to_good_embedded_primary`;
- `test_csv_relocation_preserves_actual_measurement_proofs_but_changes_document_identity`;
- `test_resigned_incomplete_native_group_or_counter_changes_fail`.

Полные exact ID находятся в `.suite.json` и основном `.json`. Проверки независимо потребляют actual index/config/runtime-plan и внешний CSV mirror; воспроизводят portable closure/geometry/counters и сохраняют nonpromotion partial/ambiguous. Их отрицательные mutations выполняются самим неизменённым maintained test в памяти. Они не доказывают повторное native execution: source tests требуют `native_execution_verified=false`, `scientific_verdict=null`.

## Связанные descriptors и будущая preparation

Все файлы этой постановки фиксируются одним normal metadata commit. На сервер suite/request/allowlist/checksums должны поступить из точных Git blobs этого commit, без newline normalization и без scientific data через SSH copy.

- `.fixture-manifest.json`: все157 original member→relative path, size/SHA, case fingerprints, source archive/bundle bindings.
- `.members.txt`: точный allowlist157 для GNUtar.
- `.SHA256SUMS`: exact bytes каждого projected file.
- `.suite.json`: production validation suite schema1; fixture pattern `**/*.*`,157files и полный fingerprint. Fixture root содержит только шесть case directories; manifests остаются снаружи, поэтому pattern покрывает все157 data files и не попадает на directories.
- `.request.json`: production `timelearner_owned_python_job` schema1, операция `python-validation`.
- основной `.json`: source/package hashes, limits, статусы, prerequsites, unexecuted argv и expected closure.

Предложенные новые пути:

```text
/media/user/Data/TimeLearnerRefactor/plan-composite-native-a4-semantic7-m40-a1
/media/user/Data/TimeLearnerRefactor/fixtures-composite-native-a4-git-b4feb-a1
/media/user/Data/TimeLearnerRefactor/readbacks/s10-composite-native-a4-semantic7-m40-a1
```

Перед записью нужны root review и fresh read-only discovery: hostname M40, source/interpreter bytes, наличие b4feb Git archive blob, canonical отсутствующие target paths, память/диск и отсутствие конфликтующих held leases/живых kernel groups. Если нужен новый Git-only evidence donor, он также отдельный fresh path; старые A4 source/runtime/worker остаются неизменными. После review GNUtar выбирает только manifest157 из Gitb4feb archive, `--strip-components=4`, в новый absent root. Проверка SHA256, точного набора names, regular/noalias files и фактического размера обязательна до freeze. Никаких source updates, Build/Calculate или преобразований scientific JSON/CSV.

Preparation ожидает75MB data и ограничена128MiB projection; порог физического free перед ней768MiB. Semantic job: memory2GiB, tasks32, wall900s, output128MiB, minimum free512MiB. Registry capacity/null и actual admission фиксируются заново; глобальная capacity не меняется. Штатный adapter резервирует source/tool/suite parent/fixture read и только собственный свежий readbacks job write. Metadata preparation здесь не заменяет эти действующие проверки.

После допуска единственный запуск — существующий `python3.12 -B -m Scripts.StructTrain.TimeLearner.owned_python_job run <plan>/request.json` из CEC source. Нового launcher, API или исполняемой TEMP-программы нет. Приёмка требует exact7 actual IDs без skip/error/failure, immutable package/suite/request/fixture snapshots до/после, valid owned runtime, закрытие всей своей cgroup и освобождение lease, затем compact Git publication и независимую проверку. Любой отказ сохраняется как отдельный negative; elapsed/result до исполнения не придумываются.
