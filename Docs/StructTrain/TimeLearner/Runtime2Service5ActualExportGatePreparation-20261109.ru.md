# Реальный Service5 export → независимый archive2/Python/CLI gate

Статус: только source preparation. Текущий private native source — обычный
merge-коммит `c265fe7e2afe398701df2d21c203a1d7aa466ec9` с родителями
`99699404aeeb679a82006ad6e68635c0a81b877a` и
`f015db2d4f6ac8c239e07c050ff596524604060c`. Первый merge354 включал worker fix
`a208663decacaecbbe079499e442b6b9dbf1fb32` в исходный runtime2 Root
`9d798eb7715c4bcb052d7ba338ef026deb1d9d3b`; второй сохраняет этот fix и
добавил закреплённый Pulse dependency. Третий mergec265 включает два исправления
владения JSON и исправленный chronology regression. Сборки, CMake, серверные команды,
тесты, source projections и графики не выполнялись. Main/develop и frozen
33/53/73/A2 sources не менялись.

## Конкретная source closure

Все шаги выполнены через `merge --no-ff`. В mergec265 единственный конфликт —
Pulse gitlink; он разрешён на отдельный Pulse mergea43, включающий оба родителя.
Root C++ delta относительно предыдущего code6d358 — только исправление owning
copies/точной причины отказа в `RetainedGroupsCannotReverseIssuedOrder`.
App, CMake/cmake, Rdk и Bin тождественны7fd28. Worker/test bytes
тождественныa208. Полные Git-byte hashes и tree equality записаны в
`.source-closure.json`.

Новый Pulse `eff3a20ab7264811c3217eee24fc140bb46e8b07` обычным merge включает
fix `de26c3b475a406e02fc9a908953879984681590b`: сравнение `QJsonObject` с
`QJsonValueRef` заменено типосохраняющим `QJsonValue(Encode...) ==
candidate.value(...)`. Предшествующий compile failure с нулём выполненных
tests сохраняется отдельно; исходные Root9d798/Pulse0432 и merge354 не
переписаны. Этот source dependency не меняет declared math/schema и ещё не
проверен fresh compile/gate14.

Текущий Pulse `a43dbc727d32d626cd082cda8ab27bbe320d9f37` — обычный mergeeff3a20
с `f7a0e3e63ec29d4647790a695606d1ca32164ef3`. Delta — ровно две замены
получения значения на owning `.value(...)` в `CandidateWindowPortableReferences`
и `CandidateWindowProposalReplay`. В Root chronology test теперь сохраняет
owning first/second, доказывает перестановку двух разных group IDs и проверяет
именно `candidate_window_archive_group_order`. Wire/schema/math не меняются;
исправления ещё не имеют runtime acceptance.

Root+семь gitlinks составляют будущую восьмирепозиторную SDK closure:

| Путь | Commit |
|---|---|
| Root code | c265fe7e2afe398701df2d21c203a1d7aa466ec9 |
| Libraries/Nmsdk-PulseLib | a43dbc727d32d626cd082cda8ab27bbe320d9f37 |
| Rdk | d6c9df759a3ee20ad42fa0a83841f19385fba60a |
| Bin | 918ae5e1a2d6085b9ff148f7162eb9e744126592 |
| Libraries/Nmsdk-MotionControlLib | 85e4494e8596b0998feebff7da2f8d421a6df66f |
| Libraries/Rdk-BasicLib | 2927cad5a7456b301217b7abb228f12c9a359ea9 |
| Libraries/Rdk-CvBasicLib | c471297811367abd348c6258bdaeaf8e1a40c7bd |
| Libraries/Rdk-HardwareLib | de40b008e990105856726e01230dde19f42a90a9 |

Это точные declared Git identities, не утверждение о materialized/compiled SDK.
Перед настоящим gate нужны fresh private source/runtime/build, все восемь clean
Git-byte materializations и production source/runtime captures. Активные SDK/
cache/windows33A2 paths не обновлять. Существующие compiler/Qt/GTest и LLM
dependency settings проверяются maintained preparation workflow; не ссылаться
на удалённый старый FetchContent cache и не придумывать CanonicalSpec.

## Минимальный C++ набор: 11 + 1 + 2 = 14

Target — `Test_PulseLib_StorageComponents`, настоящий SDK integration executable.
`Tests/Integration/Libraries/CMakeLists.txt` включает оба maintained test source
в этот target. Нового harness, test body copies или standalone SDK substitute
нет. После fresh build compiled `--gtest_list_tests` обязан подтвердить exact
14 literal IDs до выполнения; source regex inventory сам по себе не доказывает
наличие compiled tests.

Сначала все одиннадцать literal `CandidateWindowRuntime2.*` из
`Test_PulseLib_CandidateWindowDeclarations.cpp` (точные IDs/строки/hash в
`.selection.json`), затем исправленный chronology control:

```text
NativeCandidateWindowBudgetReplay.RetainedGroupsCannotReverseIssuedOrder
```

Он использует настоящий production archive encoder/decoder и построенный
native reference archive. Проверка не относится к одиннадцати synthetic runtime
declarations. Отдельный frozen gate37 также готовит этот case; его будущий receipt
не считается уже полученным. Повторное покрытие можно исключить только после
явного сопоставления accepted receipt и точных test/production dependencies,
без подмены фактического inventory. Затем два Service5 cases:

```text
NativeCandidateWindowService.ClassicN0CalculateMode0FreshAllNFinal
NativeCandidateWindowService.BranchN0CalculateMode0FreshAllNFinal
```

Оба вызывают production `WindowServiceExact` через настоящий Environment/storage/
scheduler/native before/after hooks, а не manual actor или synthetic packet.
Исходник EXPECT/ASSERT требует references, final allN, certificate3 Exact,
actual callback/raw/sample accounting и runtime2 roundtrip. Это **ожидаемая
проверка**, не заранее установленный результат: до actual run наличие refs/
finals/успешный Train не утверждается. Если test/producer откажет, сохраняется
настоящий negative и неполный output; ожидаемые файлы не дорисовываются.

Scope двух cases: N2, 2000 Hz, N0, CalculateMode0, two candidate repeats,
engineering SyncTol=.2, ampAbs=1e-5, minimumAmplitude=1e-6. Это plumbing/control
с заданной .2, не научная сходимость исходной .02 серии. Default .02, CalculateMode1,
N1, все модели/режимы и N4/N6 distinct attachments остаются отдельными
обязательными пунктами исходного плана, не исключёнными этим gate.

## Producer paths и защита от коллизий

Использовать maintained native acceptance worker **из своей actual SDK source**:
его module `__file__.parents[3]` должен совпадать с этой SDK. Native output route:

```text
owned native leaf → native_gate → contained_runner
kernel request.environment.TIMELEARNER_COMPOSITE_OUTPUT = OWNED_LEAF/native-composite
```

Worker проверяет этот exact route. Его нельзя подменять monkeypatch, чужим Tool
worker или дополнительным shell launcher. Родительский output leaf новый и
отделён от source/runtime. C++ writers применяют `QIODevice::NewOnly`.

Два positive case создают разные root suffixes:

```text
native-composite/classic-native-window-service5/N0-mode0/
native-composite/branch-native-window-service5/N0-mode0/
```

Chronology control дополнительно пишет native manual-DATA suffix
`native-composite/classic-window-budget-refs-A-empty-B/` через
`ActualRetainedWindowBudgetArchive(false)`. Он distinct от обоих Service5
outputs. Этот helper не владеет service5 runtime plan: его файлы нельзя выдавать
за полноценный cold7/runtime2 CLI case или достраивать недостающий plan.
Его original archive/CSV/boundary сохраняются как отдельный typed replay control.

Одиннадцать declaration-only tests не вызывают этих export writers. Два cases
имеют разные topology prefixes; совпадающие run/trial/local group names внутри
разных cases не дают права смешивать их records. Один case/test запускается
один раз в fresh output; повторное выполнение в том же output запрещено.

Реальные дополнительные producers поддерживаются исходником и предлагаются
как **отдельное расширение после минимального14**, не как неявно выбранные tests:

| Exact test suffix (`NativeCandidateWindowService.`) | Реальные output suffixes |
|---|---|
| ClassicPartialWarmDiscardsExpiredSeedsAndRecapturesAllN | classic-native-window-service5/partial-before-warm; /partial-warm-fresh-allN |
| BranchMergedVertexRemainsDiagnostic | branch-native-window-service5/merged-diagnostic |
| BranchBoundC0WitnessesStayOnBaseRevision | branch-native-window-service5/bound-C0 |
| ClassicWarmAfterOwnedGrowthKeepsOriginalTargetsAndHistory | classic-native-window-service5/grown-before-warm; /warm-after-owned-growth |

Имена distinct от N0-mode0 и друг от друга. Partial producer имеет actual
stopped prefix без complete refs; после warm сохраняет старый unconsumed record
и пишет fresh allN. Merged producer ожидает InvalidObservation, отсутствие
references/certificate и unconsumed geometry !=Valid. C0 producer записывает
реальные per-raw base-revision witnesses. Warm-after-growth producer сохраняет
исходные P0/targets/history, current runtime start revision может быть уже
изменённым. Их фактические outcomes/groups всё равно берутся из actual output.

Не включать несколько однотипных callback-fault tests в общий leaf: helper
`SaveWindowService(f,"callback-fault")` использует один suffix на topology.
Для их будущей проверки нужны отдельные owned leaves. Это output limitation,
а не исключение работающих режимов/проверок из общего плана.

## Обязательный self-contained case и raw inventory

После successful started service `SaveWindowService` вызывает:

1. `EncodeNativeCandidateWindowServiceArchive(service)` и production runtime2
   Encode→Decode→Encode с actual `service.Plan()`, проверяя current run ID.
2. `SaveCompositeArchive`: `composite-measurements/index.json`, **каждый** CSV из
   archive.primary по своему relative path, sidecar `group-%06d.json` для каждого
   retained record. Не предполагать число groups/native/sample по имени теста.
3. `SaveCompositeBoundary`: original owned `initial-configuration.json` (cold7),
   actual `runtime-plan.json` (runtime2), `after-model.json` с реальными neuron/
   dataset snapshots/actual inputs/revision/epoch/C0 и `boundary-math.json`.
4. `service5-boundary.json`: actual outcome/reason/session/model epoch,
   original references/proofs/targets, current limits, certificate/last core
   certificate, actual candidate residual evidence and resistance domains.

Для двух Service5 cases точные version checks: cold7, runtime2,
protocol5/contract2, archive2/record2,
method specification2, Recorder6. Минимально обязательно наличие всех шести
named JSON + всех CSV и record sidecars. Full manifest/SHA/file count формируется
**после** actual producer completion, из реальных файлов; не генерируется по
предполагаемым группам/пикам. Original input stimulus и все retained soma samples
остаются в CSV. Old SourceSnapshot/runtime1/manual33 не заменяют эти документы.

В literal `service5-boundary.scope` ещё есть историческая фраза «before separate
runtime2…». Она не является codec/version authority: admission проверяет
actual runtime-plan.json schema2/full protocol binding. Label отмечен как
documentation debt; из него нельзя делать вывод об отсутствии runtime2 или
восстанавливать недостающие typed fields.

## C++ ↔ Python join

Python analysis берёт отдельный reviewed source
`d8f3ebf26c882b4ebb54a40a3ab6e9857077d942`, Python452 fingerprint
`db126c94bb8df9e61dbef60a71446e5c74bb506986323cd3c044f57dc35e1e0c`.
Сначала должны быть сохранены original negative73 и пройден conditional73A2/
common collector metadata gates. C++ source/build identity и Python analysis
tool identity фиксируются раздельно; совпадения root commits не выдумываются.

После полного closure native job и own lease release original output
фиксируется через Git-only evidence/fixture projection с actual allowlist и SHA.
Не менять producer outputs, не перепаковывать источники из текущей working copy,
не передавать scientific data через SSH/SCP. Объём и пределы analysis output
объявляются по actual retained data, не через guessed CanonicalSpec.

Далее maintained **actual-service5** test/manifest (отдельный от A4 schema1
test fixture) должен выполнить без mocks:

```text
audit_composite_measurement_archive(index, original_cold7,
    runtime_plan=genuine_runtime2,
    external_resolver=filesystem_primary_resolver(case_dir))

python -B -m Scripts.StructTrain.TimeLearner analyze CASE_DIR \
    --format native-composite-measurements --output NEW_OUTSIDE_CASE_REPORT.json
```

Каждый external primary обязателен, даже при хороших embedded blobs. Проверить
full source/storage/model/readback/raw/native reset/grid/events/chronology/repeat,
actual geometry и peak, reference family, frozen proposal arithmetic/IDs,
semantic proof2, current runtime2/full protocol hash и retained history caps.
Не использовать C++ asserted selection как truth.

Для positive case после actual observed status проверить N из protocol inputs,
nonzero measured/proposal coverage, allN immutable refs и fresh allN finals
одного current/latest observed final run/revision/epoch. Сопоставить reference/
final group/proof IDs и raw targets с `service5-boundary`/`boundary-math`, actual
after-model revision/inputs/C0/dataset full restored stimulus. Source initial
graph не заменяется trained graph. Report нужен retained вне case; временный
report из старого unit test не считается сохранённым analysis artifact.

Дополнительная прозрачная сверка residuals использует ровно существующую
математику `FinalVerification.cpp:556–571`, не новый критерий:

```text
R[i] = independently_audited_reference[i].raw_potential
F[i] = independently_audited_fresh_final[i]
A = F[N-1]                                 # same final graph/sweep
amp[i] = F[i].raw_potential - R[i]
amp_tol[i] = runtime.amp_abs + runtime.amp_rel * abs(R[i])
(low,high)[N-1] = (0,0)
(low,high)[i] = (F[i].arrival-A.plateau_end, F[i].plateau_end-A.arrival)
```

arrival/plateau_end уже отсчитаны от **actual origin event каждой группы**;
нельзя сравнивать raw absolute model clocks разных групп. Сверить сохранённые
certificate3 `residuals` поля `target_raw_potential`, `measured_raw_potential`,
`amplitude_residual`, `amplitude_tolerance`, `timing_low/high`, `within_*`,
trial/effective revisions и proof/window/instance IDs. Timing threshold не
заменять dt/процентом/EstDelay. Это planned consistency check, не уже
реализованный независимый cert3 admission.

Adversarial controls на **копиях actual original case**: coherently rehash
foreign ref proof/recipe/instance/measurement/document; physical Rs claim при
неизменном semantic bank; candidate frame/required timestamp; historical cap
за новым warm cap; missing/corrupt CSV; wrong runtime2 protocol/current attempt.
Ожидаются конкретные source/data binding failures, без исправления originals
или превращения invalid/missing/ambiguous в PASS.

## Prerequisites и acceptance scope

До настоящего запуска отдельно review: fresh SDK8/rootc265/Pulsea43 Git-byte
closure, compiler/Qt/LLM dependencies, target build and loaded-runtime capture,
compiled literal inventory14, exact production-created native request, новые
paths/resources/limits и output-route collision map. Из source-only этого
документа runnable CanonicalSpec/request не создаётся. Подготовка/запуск идут
через existing production capabilities, не новый orchestrator.

Приёмка требует actual C++14 JUnit, all process closure/leases, immutable source/
runtime provenance, complete producer byte inventory, independent Python/CLI
full replay/rehashed negatives и сохранённые per-case reports. Native/analysis
failures сохраняются; runtime/model/status не правятся ради зелёного результата.

Даже successful minimum gate — actual **portable DATA/runtime2 join**. Он не
заменяет full248/STEP2/core/service regressions, N4/N6 distinct physical routing,
all modes, N1 pending single-input contract, package6 self-contained imports,
полный cert3 verifier или frozen recognition evaluation. Python flags
native_execution_verified/live_authority_restored/training_certificate_verified
остаются false. Recorded C++ Exact — факт этого engineering fixture при .2,
не автоматический recognition PASS/новая научная матрица.
