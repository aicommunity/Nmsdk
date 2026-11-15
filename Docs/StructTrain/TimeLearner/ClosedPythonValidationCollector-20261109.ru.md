# Штатный сбор закрытых Python validation gates

Статус: SOURCE ONLY. Код, metadata fixtures и план gate подготовлены; новая
когорта ещё не исполнялась. Фиксированные producer для65 и ранее53 сохраняются
как исторические control/source artifacts. Новый сбор40/73 должен использовать
этот maintained module после отдельного review и Linux metadata gate.

База feature: `a5e028517452ed421bbabe795b741ef7e7e1b379`, содержащая принятые
Source2caf APIs и результат65 с проверенным применением трёх общих API.
SDK, Pulse/Rdk/Bin, модели, source/build/runtime caches не изменяются.

## API и границы

`Scripts.StructTrain.TimeLearner.closed_python_validation` поддерживает только
завершённую полную когорту существующего `owned_python_job/python-validation`
schema1, с исходным signed binding, request, suite, результатом и журналом.
Отсутствующий binding, preflight0, неполная когорта, native C++, render, builds,
AR cleanup, динамическая unittest-инвентаризация сюда не допускаются.

- `validate_manifest(value)` проверяет закрытую schema1 и все declarations до
  чтения их членов. Field `expected` содержит точные IDs, failure/error IDs,
  skips с причинами, diagnostic fragments для каждого fail/error и исходные
  controller/worker outcomes.
- `prepare_closed_collection(path, expected_sha256)` делает SQL-readonly
  preflight: общие file/Git-role APIs, буквальная module/class inventory,
  исходный supervisor и fresh закрытие ТОЧНОЙ исходной группы, runtime identity,
  worker lease, полные materialized Scripts и fixture before/after.
  Исходные тесты и модели не запускаются; исходные leases не освобождаются.
- `collect_prepared(prepared, output_root)` повторно валидирует публичный
  prepared value, затем через штатный reservation owner создаёт только новое
  output. Bundle writer получает возвращённые общими API staged frozen copies.
- `stage_collection_artifacts(output_root, repository)` требует durable final
  receipt и последний artifact inventory, проверяет actual released collection
  lease через read-only owner, затем вызывает существующий
  `publisher.stage_artifact_set`. Commit/push/Git closure остаются у существующих
  Git/publisher primitives; новый collector их не дублирует.

`collection_status=completed` не означает, что исходная когорта прошла. Для73
сохраняются `original_gate_outcome=failed`, исходный `process_error/1`,
`worker.operation_passed=false`, 72 passed/1 failed и точный failed ID:
`Scripts.StructTrain.TimeLearner.tests.test_candidate_window_runtime2.CandidateWindowRuntime2DeclarationTest.test_C_region_and_context_count_limits_are_checked`.
Исходная причина/traceback не перезаписывается; ожидаемый fragment задаётся
manifest, а не новым прогоном теста.

## Schema1

Manifest имеет ровно поля: `kind`, `schema_version`, `collection_id`,
`worker_host`, `execution_root`, `collector_tool`, `job`, `expected`, `files`,
`git`, `projections`, `fixture_reference_roles`, `extra_metadata_note`, `limits`.
Полные обязательные вложенные keys проверяет `validate_manifest`.

`job` задаёт original tool, validation source и plan как отдельные
`{path,commit}`. Collection tool — фактический namespace импортированного
module; original tool не импортируется и не подменяется. Planned/actual SDK и
compiled runtime не изобретаются: для этого scope они `None`/not started.

`files` — `RequiredFileRole` + `archive_path` + purpose (`code_or_plan`,
`observer_metadata`, `opaque_extra`). `git` — полные `GitInputRole` с canonical
repository, HEAD/commit40/path/blob40, точным bytes/SHA256 и верхним cap.
No lazy fetch, basename lookup, fallback ODB или hash-only source authority.
`projections` хранит ожидаемые sparse patterns ЯВНЫМИ массивами; порядок
сравнивается буквально, никогда не выводится из порядка map keys.

Fixture snapshots сравниваются с исходными saved before/after и result.fixtures.
Сами primary CSV/models не включаются как file-role payload: сохраняются
исходные Git reference capabilities и metadata fingerprints. Fixture-specific
семантический join и научный replay остаются у owning reader, не у collector.

##40 и дополнительные непрозрачные metadata

SQLite, requests, closure observations и сжатые observer records можно явно
добавить в `files`/`git` с purpose `opaque_extra` и обязательным note.
Collector сохраняет bytes, но не открывает дополнительные SQLite для анализа,
не checkpoint-ит их, не превращает наличие файла в kernel proof.
`extra_metadata_semantic_validation=false` и
`nested_kernel_closure_attested=false` остаются явными. Root observer для40
(11 units/9 cases, 7 released/2 intentionally held) — отдельное доказательство;
generic collection не переинтерпретирует эти состояния.

Собственная общая reservation SQLite/WAL/SHM не может быть входным file-role:
reserve/heartbeat/release изменили бы эти bytes. Нужны отдельные закрытые
case snapshots либо независимые records/refs, явно перечисленные оператором.

## SQL-readonly owner

`Reservations.read_snapshot(database, managed_units=False)` читает metadata,
schema, policy и rows в одном `mode=ro`/deferred `BEGIN`/SELECT snapshot.
Не вызывает constructor, `_transaction`, PRAGMA, writer reservation или schema
migration. `open_existing`/`inspect` сохраняют прежние writer semantics.
SQLite reader locks, существующие WAL sidecars и atime не объявляются
неизменяемыми filesystem bytes; обещание относится к SQL access.

Immutable lease identity/resources/state/timestamps/release note сравниваются
полностью. Только `heartbeat_expired`, `owner_status`, `inspection_required`
считаются observation-derived, с явной проверкой типов. Оба original/raw record
сохраняются, а не нормализуются в одинаковый hash.

## Завершение и публикация

В bundle лежит только `capture_prepared` proof. После archive, повторного
preflight, source/fixture/capture checks, budget checks выполняются stop/join
heartbeat и проверка late errors. Затем штатный owner освобождает collection
lease; SQL-readonly snapshot подтверждает release/identity/resources.

Ограниченный controller-finalization tail, аналогичный контроллеру
`owned_python_job`, пишет только два новых JSON control файла после release:
`verification.json` (bundle/proof hashes + original outcome + фактический
released lease) и ПОСЛЕДНИЙ `artifact-inventory.json`. Это не bulk output write
после release. Inode output directory проверяется; 4 MiB tail reserve включён
в budget. Каждый control ограничен 1 MiB, exclusive atomic link и fsync;
неуспешный новый success-name откатывается только при совпадении собственного
inode. Finalization objects и failed partials сохраняются для review.

Нет self-hash цикла: receipt хэширует bundle/capture proof, последний inventory
хэширует receipt и эти artifacts. stdout не является единственной durable
квитанцией. Stage action требует оба final файла, перепроверяет hashes и
released state; capture proof сам по себе не разрешает публикацию.

## CLI и проверки

```text
python3.12 -B -m Scripts.StructTrain.TimeLearner.closed_python_validation collect MANIFEST --manifest-sha256 SHA256 --output NEW_OWNED_OUTPUT
python3.12 -B -m Scripts.StructTrain.TimeLearner.closed_python_validation stage OUTPUT --repository PRIVATE_REPORT_REPOSITORY
```

`-B` обязателен для source projection. Output/input roots не пересекаются;
все reads, включая fixtures и projection ODBs, входят в read reservations.
Новый manifest и output подготавливаются по Git в новых каталогах, без
SourceCache/SDK mutation. Schema3 managed collection dispatch пока не включён
неявно: нужен отдельный review; original metadata API сохраняет explicit mode.

Unit fixtures — СИНТЕТИЧЕСКИЕ METADATA. Они проверяют schema/outcome/log footer
и traceback completeness, joins, public-value/staging guards, late heartbeat,
atomic finalization, last-marker staging и реальную SQL-readonly observation
на отдельной временной ledger. Они не доказывают валидность реального40/73,
native archive2/runtime2 или научных результатов.

Первый metadata gate включает новые tests и релевантные существующие
resource_reservations/resource_budgets/existing_reservations regressions:
factor затронул persisted policy/decode/inspection. Count/IDs фиксируются по
Git AST inventory; не по памяти и не по source macro bodies. Все исполнения
только Linux, через существующий owned validation pipeline после source review.
Реальный40 и negative73 собираются отдельными последующими CLI invocations;
никаких повторов их исходных unit/native/model запусков.
