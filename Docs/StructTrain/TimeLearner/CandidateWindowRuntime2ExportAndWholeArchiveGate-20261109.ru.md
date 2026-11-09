# Runtime2 exporter и полный archive2 → Python → CLI gate

Статус: отдельная source preparation от Root
`7ad96da0e66fe1ef51fc76acb2114174ab6a4e68` / PulseLib
`4b70b0bfb41510691971de86ce5c4993bb382b8b`. Текущий frozen33 и reader7352
не переписаны. Сборки, тесты, численные расчёты и серверные вызовы этим
изменением ещё не выполнялись. Новые исходники требуют отдельного source pin
и gate; runtime acceptance не объявлена.

## Выявленное соединение несовместимых контрактов

В исходном Root7ad `Test_PulseLib_CompositeTraining.cpp:1016–1019` service5
producer сохранял cold7 и `runtime-plan-scope.json` с
`runtime_plan2_exported:false`, а не runtime-plan. Manual `ActualWindowArchive`
на строках 1840–1848 также не владеет service plan. Эти архивы остаются
полезным DATA; отсутствующие документы не восстанавливаются из их claims.

Reader7352/codeef5 `candidate_window_archive_evidence.py:291–295` передавал
runtime-plan в `validate_protocol` как cold configuration. Через
`configuration_view:107–119` это требует schema7 и model/profile/window fields.
Настоящий runtime1 имеет отдельную схему (Pulse
`CompositeTrainingDeclarations.cpp:93–134`); настоящий runtime2 также должен
оставаться runtime declaration. Это production integration defect, который
нельзя закрыть переименованием cold7, mock auditor или одним missing-file test.

## Изменяемые компоненты

PulseLib `CandidateWindowTrainingDeclarations.h` и новый
`CandidateWindowRuntimePlan.cpp` вводят отдельные strict runtime2 encode/decode.
Полная схема и ограничения описаны в
`Libraries/Nmsdk-PulseLib/Docs/TimeLearner/CandidateWindowRuntime2Declaration.ru.md`.
Старые runtime1
и cold7 codecs не меняются; runtime2 — полный old runtime declaration shape с
schema2, protocol_binding и candidate_window_policy в common policy2.

Root `SaveCompositeBoundary` сохраняет original
`service.CompositeInitialConfiguration()` и
`EncodeCandidateWindowRuntimePlan(service.Plan())` для настоящего service5.
`SaveWindowService` проверяет actual-plan roundtrip и session identity до IO.
Динамика service/learner, критерий, lifecycle methods и callbacks не меняются.

Отдельная Python ветка должна заменить ошибочный cold7-call для runtime-plan
специальным strict runtime2 validator. ORIGINAL cold7 по-прежнему проверяется
как cold7. Runtime2 связывается с protocol5/candidate policy, текущим attempt,
archive primary cap и budgets текущих records; historical records проверяются
по своим прежним caps. Реальные clipped group limits допустимы при `<=` plan,
а runtime search/tolerances/caps не обязаны равняться исходному cold7.

## Обязательные реальные входы

Для первого полного gate требуются закрытые service5 exports с:

- producer-pinned original `initial-configuration.json` schema7;
- producer-pinned original `runtime-plan.json` schema2, созданным из фактического
  started service plan, с actual session/run_id;
- `composite-measurements/index.json` schema2/protocol5;
- всеми referenced CSV, побайтно совпадающими с embedded primary;
- сохранёнными producer sidecars и source/JUnit/closure metadata для provenance.

Полные hashes/counts фиксируются по фактическому postclosure Git corpus;
неизвестные сейчас размеры и количества не подставляются из synthetic fixture.
Все JSON/CSV/models, использованные опубликованным результатом, сохраняются
сжато в Git. Server cache — только staging/render cache, не единственная primary.

Первый минимальный positive cohort: реальные
`classic-native-window-service5/N0-mode0` и
`branch-native-window-service5/N0-mode0`. C++ producer должен закончить
all-input references и final sweep. Для последующего расширения уже существуют
`branch-.../bound-C0`, `classic-.../warm-after-owned-growth`,
`classic-.../partial-before-warm`, `branch-.../merged-diagnostic`.
Это точные source paths, не утверждение, что артефакты уже существуют.

## Минимальные meaningful assertions

Unmocked public `audit_composite_measurement_archive` должен получить
`reader_version=2`, все records/groups/CSV, `reference_set_recomputed=true`,
положительное число measured groups и search/final proposals, закрытые
all-input references/finals. Для измеренных rows требуются independently
recomputed closure/geometry, validity `valid`, proposal replay для non-reference,
точные counters/attempt membership/prefix budgets и runtime binding checked.
Нулевой архив/нулевая positive coverage не удовлетворяет gate.

Та же original case directory передаётся публичной команде:

```text
python -B -m Scripts.StructTrain.TimeLearner analyze CASE --format native-composite-measurements --output OWNED_NEW_REPORT.json
```

Результат читается обратно и сохраняется в компактном Git evidence как actual
audit artifact; temporary-only persistence не называется retained report.
Exact-byte bindings трёх JSON и полный audited group/measurement inventory
должны совпасть с direct auditor. Output находится вне immutable case. Ни один
auditor не подменяется mock; archive1 не преобразуется в archive2.

Negative controls копируют только parsed metadata в owned output и сохраняют
actual raw CSV неизменёнными. После пересчёта разрешённых content digests:

1. Чужой reference_proof_id с правильными recipe/instance/measurement/document
   hashes отвергается replay против retained original reference.
2. Physical Rs claim с обновлёнными candidate/proposal/document hashes, но
   неизменным semantic synapse bank, отвергается graph/control-knob check.
3. Для actual warm corpus historical cap, покрывающий отдельный record, но не
   retained prefix, отвергается ledger check даже при сохранённом current cap.
4. Missing/changed external CSV не заменяется хорошим embedded blob.

Patching C++ verdict, перенос live addresses в authority, восстановление
callbacks/native leases, promotion certificate/package и scientific verdict
не входят в этот gate. `native_execution_verified`, `live_authority_restored`
и `training_certificate_verified` остаются false. Actual C++ execution
подтверждается отдельным native producer gate, не Python file audit.

## Порядок принятия

1. Source review обоих codecs и совместной schema2, literal test inventory.
2. SERVER ONLY: 11 synthetic runtime2 declaration tests плюс actual service5
   producer, реальные bytes roundtrip, source/CMake/JUnit/owned closure.
3. Git capture immutable original cold7/runtime2/archive2/CSV; без текущих cache
   updates во время чтения и без заднего дополнения старых manual exports.
4. SERVER ONLY: unmocked dispatcher + публичный CLI + cross-layer negatives,
   exact case IDs, positive coverage и retained compact reports.
5. Независимая metadata/hash verification и scoped docs; acceptance не
   распространяется на manual33, package6/Train CLI или полный scientific matrix.
