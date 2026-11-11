# Реальные composite archives: подготовка Python replay и временных отчётов

Статус на 2026-11-08: **подготовка исходников и контракта, без запуска**.
Машинный план: [CompositeNativeReplayPreparation-20261108.json](CompositeNativeReplayPreparation-20261108.json).
Этот документ не является результатом текущего C++ задания. Наличие и состав
шести реальных экспортов должны быть установлены его единственным collector
после завершения и закрытия всех принадлежащих ему процессов.

## 1. Неизменяемые источники и область

Python reader/CLI изучены на Root `cb7721c80125f1ca3df86cc69d651a0303346c31`.
Все **440 Python Git blobs** пакета `Scripts/StructTrain/TimeLearner` дают
fingerprint `712184e21fc00c01932f6bec5e5646461b5260127d79bc198fff2d9818936b9d`
по алгоритму `validation.package_fingerprint`. Это новый фактический набор,
а не fingerprint прежних wire67 или combined143. JSON фиксирует SHA256,
Git blob, размер и номера строк затронутых production modules.

Планируемый фактический C++ producer:
Root `b6d0f752ca1668b6a908a435438020db58d2018e`,
Pulse `88ea9c7ab3583da601b1f01ec84bf6f122875a34`,
Bin `918ae5e1a2d6085b9ff148f7162eb9e744126592`,
Rdk `d6c9df759a3ee20ad42fa0a83841f19385fba60a`.
`Tests/Integration/Libraries/Test_PulseLib_CompositeTraining.cpp`:
blob `af21670c9b1e15259e522f0b3d6e7b0ae6c2dfc1`, SHA256
`4dfb510ffde3c141cf3416c04be18f8f2f6ddf76295af5fcee730f23bcd189e3`.
Это **планируемая source binding**, пока не actual accepted producer binding.
Завершение нельзя выводить из имён каталогов или из этого документа.

Сами шесть экспортов используют N=2, 2000 Hz, N0/SynapseCount,
CalculateMode=1, StructureBuildMode=1, protocol4,
`declared-window-basin-necessity-v1`. Их fixture вызывает native service
явно; поле owner.ControllerVersion установлено в 1 в конструкторе (:61–120).
Эти шесть архивов сами по себе не доказывают configured Console Train с
ControllerVersion=2, N1, другие частоты/размерности или CalculateMode=0.
Другие проверки полного C++ cohort имеют собственную область и evidence.
Математика критерия, native lifecycle и старые августовские визуальные
результаты этим read-only replay не меняются и не переоцениваются.

## 2. Шесть ролей и реальные файлы

Все роли должны быть записаны одним фактическим leaf `archive-native23`.
Ниже `NativeCompositeArchive/` — точный префикс C++ test ID; строки относятся
к указанному Git blob C++ TU.

| Каталог | Producer test | Строка | Обязательный смысл |
|---|---|---:|---|
| classic-service | ClassicActualServiceStrictReplay | 1021 | Classic complete reference/final, producer ожидает Exact |
| branch-service | BranchActualServiceStrictReplay | 1022 | Branch complete reference/final, producer ожидает Exact |
| classic-partial | ActualPartialStopNeverPromotes | 1040 | остановка после начала raw sampling; unconsumed partial, без доказательства |
| branch-C0 | ActualBoundC0RawWitnessesBindUnmutedBase | 1131 | существующий C0; каждый raw witness привязан к unmuted logical base |
| classic-warm | ActualWarmReferencesAreNotNewAttemptWork | 1132 | Reset/новая попытка сохраняет прежние references и history; отдельный current-attempt budget |
| branch-ambiguous | ActualMergedAmbiguousGroupStaysDiagnostic | 1133 | merged/nonvalid geometry, не Exact, certificate null |

`SaveCompositeArchive` (:939) сохраняет `composite-measurements/index.json`,
все bytes из `archive.primary` и `group-%06d.json` для каждого record.
`SaveCompositeBoundary` (:949) дополнительно пишет `initial-configuration.json`,
`runtime-plan.json`, `after-model.json` и `boundary-math.json`.
Ordinal sidecar — способ сериализации; это не semantic measurement identity.
Список CSV берётся из фактических `raw_trials[].primary_ref`, а не из glob
с предположениями о числе групп. Все полные, частичные и отвергнутые records
сохраняются. Точные количества, размеры и fingerprints пока **неизвестны**.

`after-model.json` содержит реальные neuron/dataset snapshots, actual inputs,
model revision/epoch и optional C0 state. `boundary-math.json` содержит actual
reference IDs/proof/raw potential, outcome/reason и certificate2 либо null.
Эти файлы нужно сохранить независимо от того, проверяет ли их текущий reader.
Producer b6 **не пишет** learned/stopped package5 и отдельный `models/native.xml`.
Native XML находится внутри snapshot.native_xml; его нельзя подменять XML
JUnit `native.xml` leaf. Возможный будущий файл `models/native.xml` требует
собственного producer mapping и hash binding. Нельзя создавать package5,
summary6 или XML-файл из отдельных полей ради прохождения другого auditor.

## 3. Приёмка входов до Python gate

1. Sole collector закрытого C++ задания публикует immutable evidence с actual
   Root/Pulse/Bin/Rdk, executable/runtime/loaded-files, CMake/source capture,
   JUnit, owned request/binding, всеми leaf/outer closure и lease release.
   Проверить exact STARTED log через maintained provenance helper. Записать
   actual evidence commit и SHA полного файлового manifest. Не выдать export
   existence за kernel closure или завершённый полный cohort.
2. Все первичные JSON/CSV и модели, используемые опубликованным результатом,
   обязаны храниться с исходными bytes в сжатом Git evidence, с полным manifest
   размеров/SHA и проверяемой привязкой к публикации. В новом owned analysis
   каталоге восстановить шесть role directories из этих сохранённых bytes.
   Same-host byte-preserved cache допустим как staging для анализа и полный render
   cache после сверки каждого файла с Git manifest; он не является единственным
   авторитетным источником. Одной hash-ссылки на отсутствующий в Git primary
   недостаточно. Первичные данные не ресериализовать и не собирать fake package;
   missing Git-backed bytes — отказ, а не fallback на cache.
3. Сделать frozen read capture: regular files, canonical relative path, отсутствие
   symlink/escape/duplicate destinations, размер и SHA256 каждого файла, стабильность
   до/после чтения. Полный observed set должен совпасть с JSON+CSV union, либо
   новый тип файла должен быть явно включён в reviewed fixture contract.
4. Материализовать production `timelearner_python_validation_suite` schema1
   только после фактического inventory. Две fixture bindings указывают на один
   и тот же root: `TIMELEARNER_COMPOSITE_NATIVE_ARCHIVES` с `**/*.json` и
   `TL_COMPOSITE_NATIVE_CSV_ROOT` с `**/*.csv`. Вторая переменная нужна для
   самостоятельного fingerprint CSV; тесты читают первую. Вычислить **реальные**
   положительные counts/fingerprints. `**/*` не подходит: validation отвергает
   попавшие в выборку каталоги. Никаких нулевых/fake placeholders или SkipTest.
5. Отдельно зафиксировать полный source projection. Все materialized Scripts
   bytes должны совпасть с pinned Git до/после; metadata об отсутствующих SDK
   gitlinks не является full SDK source verification. Каждый импорт — Python `-B`.

До выполнения этих условий JSON остаётся preparation, а не запускаемым suite.
Текущий live C++ cache/runtime/source не читаются и не обновляются этой подготовкой.

## 4. Ровно семь существующих production проверок

Модуль `Scripts.StructTrain.TimeLearner.tests.test_composite_native_archive`,
класс `CompositeNativeArchiveTest`. Полные literal IDs и строки сохранены в JSON.

| Метод `test_…` | Что проверяется по реальным входам |
|---|---|
| actual_six_service_exports_replay_all_retained_primary_and_counters | все шесть: retained CSV/packets, N+2 context, geometry, records, archive/current-attempt counters |
| actual_partial_and_ambiguous_exports_do_not_promote_invalid_measurements | partial и ambiguous остаются unmeasured; никакого certificate/scientific promotion |
| actual_sidecars_match_each_retained_record_without_filename_identity_claim | каждый sidecar равен соответствующему record, без identity по имени файла |
| actual_existing_C0_and_warm_accounting_are_retained | actual C0 witnesses; исторические warm attempts не начисляются новой попытке |
| supplied_external_mirror_cannot_fall_back_to_good_embedded_primary | in-memory missing/corrupt mirror обязан отказать при хорошем embedded primary |
| csv_relocation_preserves_actual_measurement_proofs_but_changes_document_identity | byte-identical rename сохраняет semantic proof и меняет artifact document ID |
| resigned_incomplete_native_group_or_counter_changes_fail | re-signing не исправляет удалённый raw trial или изменённый sampled_frames |

In-memory отрицательные варианты строятся из фактического экспорта внутри теста;
исходные файлы неизменяемы. Это не новые физические наблюдения.

Production API:
`validation.run_suite(specification, fixtures, output)`.
Production CLI (на сервере, после фиксации concrete suite и fresh request):

```text
python3 -B -m Scripts.StructTrain.TimeLearner.validation <suite.json>
  --fixture TIMELEARNER_COMPOSITE_NATIVE_ARCHIVES=<frozen-six-root>
  --fixture TL_COMPOSITE_NATIVE_CSV_ROOT=<same-frozen-six-root>
  --output <fresh-output>
```

Для owned запуска используется существующий `owned_python_job run <request.json>`
с operation=`python-validation`, без нового orchestrator, TEMP worker или расширения
его action set. Источники и fixtures резервируются read-only; output новый.
Fresh preflight должен включить actual fixture/source размеры, доступную память
и disk bounds. Предложение для review — 1 GiB/tasks64/1800s; оно не запускает
задание и требует проверки по фактическим размерам, а не по предполагаемой
степени сжатия. Не повторять job из-за таймаута наблюдающего транспорта.

Успех — exact seven IDs, 7 executed, failures/errors/skips=0, точное source/fixture
before/after, закрытый owned kernel group и released lease. Сохранить suite/result,
полный unittest log и stdout/stderr, explicit log roles, frozen producer/observer
bytes, source capture и closure в компактный Git evidence; отдельно повторить
metadata/hash verification локально без выполнения численных алгоритмов.

Основной reader —
`composite_measurement_evidence.audit_composite_measurement_archive` (:201),
с actual initial configuration, runtime plan и
`composite_primary.filesystem_primary_resolver(case_root)` (:102).
Embedded blobs обязательны; внешний mirror — дополнительное точное сравнение,
не fallback. Он пересчитывает sample/event/packet/context/geometry closure,
raw amplitudes/timing, semantic proofs и counters. Для partial он проверяет
синтаксис/границы доступных данных; причину отказа или отсутствующую геометрию
не вычисляет заново и доказательство не создаёт.

## 5. Какие следующие проверки остаются отдельными

Семь тестов не читают `after-model.json` и `boundary-math.json` и не вызывают
полный `composite_runtime_plan.audit_runtime_plan`. Archive reader сверяет
current run/budget bindings, но это не полный поиск/bounds/capacitance policy.
`current_runtime_budget_binding_checked=true` нельзя переименовывать в полную
проверку runtime plan. Его production API (:18) можно вызвать отдельно по actual
config/protocol/plan с фактическим C0, после source review теста/adapter.

**Boundary/certificate2.** Сначала добавить отдельно reviewed maintained adapter
для двух фактических boundary schema1, не masquerading package5. Проверить
snapshot hashes и semantic identity (`audit_snapshot`, :53), model_revision
против neuron identity, epoch, current actual_inputs против native graph, dataset
semantic identity против initial source после mask restore, C0 state/witness и
reference inventory/proofs против audited archive. XML digest и semantic hash
подтверждают только согласованность сохранённых описаний. Без реального native
import и отдельной проверки фактического native graph/response boundary audit
не доказывает native_xml↔semantic graph equivalence, восстановление модели,
её response или корректность Rdk lifecycle.

Существующий `audit_composite_certificate(package, archive_audit)` (:29) требует
полный package context. До actual package5 запрещено вызывать его с выдуманным
package. Возможный минимальный следующий refactor — выделить из него reviewed
context API с явными `certificate, archive, archive_audit, protocol, runtime_plan,
model_revision, model_epoch, capture_revision, capture_epoch, training_outcome`.
Каждое значение должно иметь exact source JSON pointer: boundary certificate/outcome,
after-model revision/epoch, archive protocol/source.initial_model/initial_epoch,
actual runtime-plan. Этот API **пока не реализован**. Positive complete cases
потребуют all-input references/finals; partial/ambiguous — null certificate и
явного nonpromotion. Проверять raw residual `measured-target`, tolerance
`abs + rel*abs(target)`, timing interval относительно последнего final input:
`[arrival_i-plateau_end_anchor, plateau_end_i-arrival_anchor]`; никакой нормировки
амплитуд или подмены assigned peak глобальным максимумом.

**Package/import/pipeline.** Только actual ModelLearnedExport package5 допустим
для `composite_package_evidence.audit_composite_package` (:68), production
`analyze <actual *_learned_state.json> --format learned-solo` либо stopped-solo.
Summary6 standalone optional, но actual execution3 требует produced summary и
полной рекурсивной artifact closure (`native_pipeline_worker.audit_execution` /
`audit_run_manifest`, `composite_execution_evidence.audit_composite_execution`).
Native model import/storage/lifecycle acceptance остаётся отдельным C++ gate.
Текущий legacy `native_execution_gate` требует process schema1/
launched_executable_only (:65–75); он не подходит для новых bound_cgroup/schema2
receipts. Использовать текущий `native_gate.audit_junit` (:66) и реальные
collector/contained closure без casts и снятия guards.

**Final sweeps.** Три теста `test_composite_final_sweep_archive` требуют седьмой
реальный `classic-two-final-sweeps`, которого producer b6 не пишет. Нельзя
добавить их к этим семи с отсутствующим input, изготовить sweep из старых
records либо объявить epoch equality достаточным доказательством свежести.

Во всех указанных Python results сохраняются native_execution_verified=false,
native_import_verified=false, live_authority_restored=false и null scientific/
evaluation verdict. Численная согласованность сертификата не восстанавливает
lease и не превращается в приёмку native исполнения или разделимости обучения.

## 6. Временные отчёты после принятого replay

Нынешний `declared_window_basin_report.py` version2 (:26 read_group/:52 render)
читает старый diagnostic14 wire format, требует N=2 и собственные witness/receipt
поля. Это **не готовый composite renderer**. Не подделывать этот dialect. Нужен
отдельный reviewed maintained adapter от accepted composite archive, сохранив
готовую идею компоновки и независимую проверку его metadata.

Контракт renderer:

- Все шесть cases, все сохранённые groups и все soma channels. Classic:
  assigned channel=input_index при отображении всех N; Branch: один soma,
  assigned channel=0, logical input identity остаётся самостоятельной.
- На каждой soma potential overview и zoom — actual CSV curves full-before,
  omission каждого input и full-repeat. На **каждом potential panel** наложить
  actual full-before `stimulus` тонкой оранжевой step curve на явно подписанной
  независимой raw-input right axis. Нижняя panel сохраняет actual stimulus всех
  controls. Только записанные CSV values/time, без восстановленных pulse templates.
- События — только actual observed ID/frame/time. CSV stimulus агрегирован;
  отдельные физические per-input waveforms из него не придумываются.
- Отображать selected peak/window/basin лишь для selection_checked принятого
  replay; ambiguous/partial видимо помечать. У incomplete group не появляется
  придуманная геометрия или сертификат. Не заменять nonfinite samples нулями.
- Явная временная трансформация для каждого probe:
  `tau_probe_ms=1000*(t_absolute-actual_specification.begin)`. Сохранить абсолютные
  CSV времена и begin в manifest. Arrival/plateau_end сертификата отсчитываются
  от **observed protocol origin_stimulus**, это другая origin. Оба начала и единицы
  записать; окна переводить из actual declared offsets, не выравнивать вручную.
- Overview + zoom с локальным Y диапазоном для каждой soma, raw units без
  сглаживания, resampling, normalization. Manifest содержит per-panel x/y/right-y,
  channel/role mapping, input CSV SHA, group/semantic proof ID, selection status.
- Full cache на M40 содержит все groups. В Git только selected 4–8 PNG, HTML/index,
  versioned transform/provenance manifest и hashes. Отбор явно включает valid,
  ambiguous, partial, C0 и warm, обе топологии; нет дублирующих SVG/PDF без причины.

Будущие расчёты и render выполняются только на разрешённых Linux серверах через
существующий maintained contained launcher и отдельный reviewed source pin.
Эта подготовка не выполняла ни replay, ни unit tests, ни C++ build, ни render,
не обращалась к серверам и не меняла live SDK cache/runtime или primaries.
