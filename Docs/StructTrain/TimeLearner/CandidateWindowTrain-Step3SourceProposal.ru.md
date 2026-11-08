# STEP3: настоящий Train5 поверх candidate-window measurement

Дата: 2026-11-08. Статус: конкретное предложение следующего source-подэтапа, не implementation/acceptance. База: Root `80b2571ec396577bfda9efc3c2a836ab89cda050`, Pulse `feb5fa5d4d6ee3c649905e638fc4914d63a5e260`. Подготовлены отдельные private branches `codex/timelearner-candidate-window-train`; frozen STEP2 и активные source/build/runtime не меняются. Механический `d6888c9` A/B, callback248 и функциональный STEP2 gate остаются самостоятельными prerequisites для runtime admission. Код STEP3 разрешено готовить отдельно, их успех заранее не предполагается.

До feature implementation включить отдельным merge --no-ff source-review budget follow-up Root `9f69883a97168d106e518a6543bf953c1c433691` / Pulse `feb3b181224156d4990d7b12fd2c16a8f1df8d7d`: per-attempt и cumulative retained prefix bytes проверяются против cap на каждой границе, а не только current cap. Эти новые pins также source-only; исходные80b/feb5 не переписываются.

## 1. Результат и неизменная математика

Цель — существующие `--timelearner-train` → actual completed/stopped package → export/import → Test для нового explicit protocol5. Нужны typed Bounded/Final consumers, владение native authority в service и строгие новые serializers. Новый orchestrator, другой search algorithm, общий amplitude target или public `eligible=true` не нужны.

Измерение остаётся `declared-window-basin-necessity-v1`: actual FullBefore highest допустимый assigned peak в заранее объявленном окне; отдельная ранняя вершина допустима при хвосте, влияющем на позднюю. Missing/merged/ambiguous/clipped не заменяются предсказанным максимумом. Reference window неизменно для initial family. Candidate frame window вычисляется до первой queue ОДНОЙ группы из оригинального seed и ACTUAL current parameters; следующие независимые группы могут иметь другие заранее вычисленные окна. Post hoc подстройка по waveform/residual запрещена.

Сохраняются без изменения:

- `CapturedPerInput`: цель input i — его actual initial raw potential. Никаких A* из пересечения амплитуд или общего max.
- Anchor — input N−1, повторно измеренный на том же current graph; arrival/plateau каждого input относительно ACTUAL protocol.originStimulusId в ЕГО FullBefore группе. Absolute modelTime и predicted delay не подставляются в scalar.
- Amplitude tolerance `absolute + relative * abs(target)`, default absolute `1e-5`; minimumAmplitude `1e-6`; sync остаётся конфигурируемым с прежним default `.02`. Geometry/window guards — отдельные значения, не train tolerance.
- Existing integer L/Ns, logRs/effective-domain search, candidate order/rank/tie rules, N0 repeats, restore-best и bounded termination. Измерение может честно вернуть InvalidObservation/OutsideTolerance/BudgetExhausted; Exact не обещается.
- Branch coupled edits инвалидируют anchor/accepted final values всех inputs, а не только редактируемого bank. Final sweep заново измеряет ВСЕ N inputs после последнего edit на одной revision/epoch.
- Rdk scheduler считает children один раз. Service/group не вызывают nested Calculate/Reset/Build. Их bool не служит отказом; Build/Calculate/Reset сохраняют true. Physics edits — штатный native editor/storage images, без uniform child writes или per-tick repair.

## 2. Что есть в базе и какие блокировки надо заменить отдельным typed путём

| Компонент | База STEP2 | Изменение STEP3 |
|---|---|---|
| `CompositeTrainingMeasurement.{h,cpp}` | Private Prepared/Validated; Require5 допускает только Reference | Новый private candidate-window Require; прежний Require/ArmComposite не превращать в p5 fallback |
| `CandidateWindowTrainingBoundary.h` | Opaque complete refs, frozen proposal, separate replay; raw DATA не mint authority | Read-only proof/group bindings для связи с CapturedReferences; новых public constructors/valid flags нет |
| `NativeCompositeTrainingAttempt.{h,cpp}` | Cold5, allN release, frozen proposal, actual selector/readback, archive2 warm constructor | Private candidate-admission callback/guard, service-owned acceptance journal; существующие graph/Need/lifecycle guards сохраняются |
| `BoundedTraining.{h,cpp}` | Raw и typed4 APIs явно отвергают5; scalar acceptance уже общий | Новая constructor overload с complete RefSet и отдельные Arm/Consume/RejectCandidateWindow |
| `FinalVerification.{h,cpp}` | Raw/typed4 отвергают5; residual math общий | Отдельные constructor/consumers5; metadata cert3 и allN fresh ownership; math Finish прежняя |
| `NativeTrainingService{,Composite}.{h,cpp}` | Dispatch/Validate/actor creation рассчитаны на4 | Явная ветвь5, подготовка semantic attempt ID до authority, release allN refs перед search, один Arm/Consume на группу |
| `ConfiguredNativeTraining.{h,cpp}` | Cold6 → protocol4 | Cold7 → protocol5/contract2, full policy, windows остаются reference-only |
| `NativeCompositeTrainingEvidence.{h,cpp}` | Archive2 producer actor-only; strict decoder знает candidate/ref proofs, finals пока не producer-promoted | Service archive2 writer с actual accepted reference/final IDs и той же strict replay boundary |
| `CompositePortableTrainingProof.cpp` | Явный guard4 до private scalar/cert replay | Остаётся4; отдельный portable proof3 для strict archive2, без borrowed live callbacks |
| `NativeCompositeLearnedState.{h,cpp}`, `NativeLearnedState.cpp` | Package5/summary6/cert2 только4 | Explicit package6/summary7/cert3 branches с actual model import и проверкой source/refs |
| `ProbeEvidenceJson.cpp` | Encode proto5 есть; cert/summary5 ещё не реализованы | Cert3/summary7 exact serializer; old1/2 и summary1–6 byte/decision paths сохраняются |
| `NativeLearnerLifecycle.h`, оба `NNeuronTimeLearner{,Branch}.cpp` | Native hooks и protected owner adapter уже есть | Новые factory hooks5 в прежнем owner executor, без второго controller owner |
| Root `TimeLearnerTrainingJob.cpp`, `TimeLearnerCompositeArtifacts.h`, `TimeLearnerTransportJob.cpp` | Cold6/package5/execution3 routing | Explicit cold7/package6/execution4 routing, все primary/sidecars, реальные stopped/export/import/Test artifacts |

## 3. Минимальный typed core без связи Bounded с Qt/Rdk

Предлагаемые overloads (имена закрепить в следующем source commit):

```cpp
BoundedTrainingSession(CapturedReferences, CandidateWindowReferenceSet,
    BoundedTrainingConfig, std::vector<InputParameters>, bool requireDomains,
    std::optional<TrainingCapacitance>);
void ArmCandidateWindow(std::size_t actionSerial,const PreparedCompositeMeasurement&);
void ConsumeCandidateWindow(const ValidatedCompositeMeasurement&,const std::string& actualRevision);
void RejectCandidateWindow(const std::string& reason);

FinalVerificationSession(CapturedReferences,CandidateWindowReferenceSet,VerificationConfig);
void ArmCandidateWindow(const PreparedCompositeMeasurement&);
void ConsumeCandidateWindow(const ValidatedCompositeMeasurement&,const std::string& actualRevision);
void RejectCandidateWindow(const std::string& reason);
```

Существующие constructors/APIs сохраняют прежние значения и p5 raw/typed4 guards. New Bounded constructor проверяет protocol5 и COMPLETE закрытый RefSet; прежний constructor5 продолжает отказывать. Прежний Final constructor5 может оставаться data-only без нового RefSet: его ArmComposite/raw и новый ArmCandidateWindow без закрытого набора не допускают observation.

Перед feature commit механически выделить только общую **non-protocol** проверку численных Bounded inputs/config из `ValidateBoundedTrainingInputs`; old guard/order сохраняются. Новый factory-specific preflight5 вызывает тот же scalar/config validator после проверки closed refs. Не переписывать p5 как p4 для Train admission и не обходить preflight публичным bool. Existing `AcceptValidatedScalar`, `AcceptValidatedScalar(index,...)` и `CompleteValidatedInput` остаются единственными математическими consumers.

Bounded/Final не включают NativeTrainingService/Rdk/Qt serializers. Допустим private callback в уже factory-owned `CompositeTrainingDetail::Identity` для candidate admission: он создаётся только actual actor, не сериализуется и не восстанавливается из адресов. Pure core сначала проверяет lease/request/captured refs, затем вызывает factory guard. JSON/model replay остаётся в native/replay source, а не в pure core. Public reference proof/group IDs доступны только как immutable данные; они не дают constructor authority.

## 4. Точные admission guards

### 4.1. Общие при constructor5

1. Protocol ровно5, contract ровно2; известные method/policy/grid/source-phase/reset tags; complete N refs и RefSet.inputCount=N. N≥2 в новом N+2 пути.
2. CapturedReferences protocol/source/family/initial revision/epoch и ordered input/proof/group IDs равны закрытому RefSet. Все targets — original raw values из replayed native refs. Seed P0/C0 — initial, не текущая обученная структура.
3. Новые config bounds/tolerances/budgets проходят прежний scalar preflight; N0/N1 normalization остаются прежними. Domain provider нужен только в прежних случаях N1. C0 требуется только для запроса C edit/owned C-history, не для Off.

### 4.2. ArmCandidateWindow

```text
require supported state + pending Probe + exact action serial + no other armed token
require actual Need + current owner lease/lifecycle + one active owner/executor
require protocol/source/family/expected closed reference IDs
require exact run/trial/input/channel/purpose/revision/epoch
require identity.frozenProposal exists and belongs to THIS private identity
require proposal was created before the first N+2 queue (private constructor only)
require actual requested maximumSamples <= declared protocol budget
replay full candidate binding and policy computation from expected original refs
require frozen recipe/instance/spec2 interval == independently replayed values
require current prepared graph instances + actual effective revision/routing
record seen group; arm ONE logical measurement, charge ONE controller probe
```

Factory guard повторяет STEP2 checks; core не принимает `valid=true`, произвольный proposal, copied identity fields, diagnostic selector result, archived callback или raw ProbeObservation6/3. Prequeue proposal хранится в identity; при first-full onPrepared проверяется тот же private identity. Прежние raw callbacks продолжают сохранять ВСЕ N+2 preparations/samples/results, но не вызывают дополнительных Arm.

Actual prepared model может быть Branch-muted, поэтому в Arm нельзя сравнивать его hash с unmuted base. Проверяются actual effective revision, original frozen base binding и реальный ordinal/bank/receiver selector. При ошибке/Need=false/expired lifecycle — отказ до scalar acceptance, по прежней invalid/stop/budget категории.

### 4.3. ConsumeCandidateWindow

Повторяются Need/lease/owner authority и exact request/protocol/family/proposal guards. Дополнительно:

- Prepared pointer identity совпадает с ранее armed token; новая подмена одинаковыми строками не допускается.
- Group complete; strict common context/native closure + fresh basin selector дали Valid actual FullBefore peak. Actual retained frame endpoints и assigned-event causality проверены; scalar создан private factory.
- Actual CURRENT unmuted model revision, epoch, complete candidate binding/storage/source/C0 и retained graph instances совпадают с frozen candidate. Per-probe neuron/dataset Reset допустим; owner Reset/Default/rebuild/retarget закрывают lease. Supported edits — controlled editor; invisible same-node direct-value ABA без наблюдения не объявляется покрытым.
- Unique semantic proof/group/trial IDs; same-revision anchor witness для Search. Новая live generation после owned edit не заменяет semantic attempt ID.
- Для Final — тот же current final run/sweep/attempt и та же actual candidate revision/epoch/witness для всех accepted inputs. Старые Search/Reference и предыдущий final sweep не принимаются.

Только после этого общий scalar acceptance получает actual raw/arrival/plateau. Reject ничего не подставляет вместо missing maximum. Need=false между close и consume даёт ExternalStop, даже если ранее закрытая группа геометрически валидна. Старый завершённый certificate может оставаться историческим документом; этим не создаётся новый Exact.

## 5. Final allN и certificate3

`FinalVerificationSession::Finish` сохраняет прежние residual equations и N−1 anchor. Добавляются только identity metadata, не другая проверка tolerances. `Accepted` хранит input-specific group/proof/windowRecipe/measurementInstance, semantic attempt и final run; пустой/неполный/mixed набор запрещает cert3.

Exact certificate3 field set: прежние common cert2 fields (`schema_version`, `method_id`, `exact`, current model revision/epoch, protocol revision, source/family, reference model revision/epoch, ordered reference/final semantic proof IDs, tolerances, residuals, semantic_certificate_id) плюс обязательные `protocol_binding`, `current_attempt_id`, `final_run_id`, `final_window_recipe_ids`, `final_measurement_instance_ids`. Arrays — ровно N в input ordinal order. Full protocol5/window policy находится в package/archive; certificate binding — canonical hash полного protocol5. No paths/live addresses/generation в semantic ID.

`TrainingCertificate::SchemaVersion` получает explicit5→3; legacy1–3→1 и4→2 неизменны. `Matches` для5 обязательно сверяет source/family, current revision/epoch, EXACT protocol/ref/tolerance bindings и полноту IDs. Текущий predicate `protocol!=4 || familyMatches` нельзя оставить для5: он бы пропускал family check. Recognition/converted model не получает OriginalExact автоматически; Matches по-прежнему требует LearnedSolo. Новая финализация после transforms получает собственный current-state proof, а не переносит старую math claim.

Portable certificate replay — отдельный `CandidateWindowPortableTrainingProof`: strict archive2, COMPLETE original refs, latest OBSERVED current-attempt final sweep, все N candidate/proposal/native proofs, current ACTUAL imported model revision/epoch, затем тот же private scalar Finish. Старый `CompositePortableTrainingProof` остаётся4. Portable decode не восстанавливает callbacks/live lease, не доказывает весь search traversal/wall history и не объявляет opaque ID физическим attestation.

## 6. Service: один владелец, один logical request, два уровня accounting

### Cold start

```text
validate exact cold7/protocol5/contract2/common policy2 + native profile/actual graph
compute checked nextSession and semanticAttempt = baseRun/session/nextSession
reserve retained bytes and validate unchanged original source if restarting
WHILE service still Idle: construct actual NativeCompositeTrainingAttempt5(
    protocol, attemptLimits, {semanticAttempt,primaryByteCap}, actual clocks)
only after successful construction commit plan/session/generation/state
capture references sequentially as independent N+2 groups
after allN capture: CaptureComposite + CompleteCandidateWindowReferences
only then construct typed BoundedTrainingSession5
```

В текущем4 service добавляет `/session/K` после construction; для5 declaration ID нужен ДО construction, поэтому новый порядок реализуется отдельной явной ветвью, не мутацией старого4. Construction до state Capturing предотвращает противоречие owner/service guard. `NativeTrainingAdapter` получает owner-specific create5/restart5 hooks через существующий `NativeLearnerLifecycle.h`; protected model access остаётся там.

`QueueComposite` для5 выбирает pending request, reserve group/native/sample/primary/model/wall budgets, actor замораживает proposal и запускает прежний N+2. First-full prepared вызывает новый typed Arm один раз. `ClosedComposite` сохраняет raw/record ДО sinks, проверяет callback generation/Need/actual clocks после callbacks и делает ровно один typed Consume/Reject. Успех и certificate публикуются только после безопасной доставки sinks, как в reviewed cancellation path. Callback248 corrections не переписываются вторым FSM.

Service хранит controller selection refs/finals и связывает их с actual actor journal. Нельзя одновременно начислять группы в actor и считать raw bursts как controller probes. Один logical group = один core probe, raw budget = N+2, samples и primary bytes — фактические в отдельном ledger. N0 candidateRepeats создают свежие anchor/input groups; FullAfter повтор внутри ОДНОЙ группы проверяет repeatability и не заменяет N0 repeats.

Private service commit acceptance обновляет journal record только после typed accepted counter delta и последнего fresh Need/lease check; public bool не mint authority. Service archive2 writer экспортирует эти реальные consumed/reference/final selections. Actor-only STEP2 writer по-прежнему не притворяется completed Train. Partial/native rejected groups сохраняются, но не становятся measurements/certificates.

### Edits, reset, retarget и import

- Между probes/группами параметры меняет только existing owner native editor. После Applied — actual readback/revision, model epoch, invalidation all Branch anchors/finals, новая live guard generation; original source/family/seed/P0 неизменны. Semantic attempt остаётся прежним.
- Warm Reset после complete refs сохраняет исходную family/targets; inflight lease истекает. Следующий Start создаёт НОВЫЙ semantic attempt и actual owner lease из validated original archive2 refs/actual current graph. Допустимо reuse уже подготовленного private complete data proof, но не callbacks прежнего процесса/owner. Не вызывать cold InitializeShared на trained graph как target capture.
- При incomplete refs нет usable set. Reset закрывает/архивирует partial и уничтожает staged live tokens. Recapture всех N допускается только при исходных original revision/epoch/source constraints; при их потере — explicit cold/original-state restore, не новая цель из trained graph.
- Default/PoolReturn/retarget очищают live authority и автоматически сохраняемую target family. Explicit import valid package6 — отдельная операция восстановления исходного source/proofs и ACTUAL model; она не является неявным возобновлением после Default.
- Source ISI/profile/frequency, class images, input identity/order или candidate-window policy changes требуют explicit new condition/family; существующий immutable protocol binding не переписывается. Разное candidate frame window от той же policy/current parameters не считается retarget.
- Package6 import сначала проверяет данные/primary/proofs, реально импортирует `neuron`/dataset/storage images, сверяет actual full identity/parameters/C0/restored full source. Template из initial config не заменяет trained model. Только последующий Start создаёт live authority.

## 7. Explicit wire/Console branches

Версии ниже свободны в актуальном Root Python adapter source; новые readers подготавливаются отдельным chunk после согласования schema. Нет `>=4`/`>=5` dispatch и нет расширения старых wire aliases.

| Wire | Новый путь | Old invariant |
|---|---|---|
| Cold configuration7 | Exact прежний cold6 wrapper key set, schema7/base1–4; composite_measurement policy2 = прежний policy1 key set + ОБЯЗАТЕЛЬНЫЙ candidate_window_policy1; outer windows — initial reference windows | Cold6/protocol4 decoder не принимает новое поле; old configs1–6 остаются прежними |
| Protocol5/contract2/spec2 | Уже STEP2; полный immutable reference windows + candidate policy, actual frame projection | Protocol4/fixed seconds windows не меняются |
| Measurement record2/archive2 | Уже STEP2 exact keys; service writer теперь может выбирать consumed Final IDs по настоящему typed acceptance | No extra unbound policy overlay; semantic proof2 binds native spec and byte cap; old record1/archive1 не получают новые поля |
| Certificate3 | Exact fields из раздела5, recomputed boundary math | Cert1/2 serializer/meaning прежние |
| Learned/stopped package6 | Exact key set package5 с schema6, cold7/protocol5/runtime plan2/archive2/cert3; actual neuron/dataset/C0 | Package5 остаётся4/cert2, wrong mixed versions отклоняются |
| Runtime plan2 | Exact прежний runtime plan1 key set; p5/full policy5 и native training policy2 | Initial configuration неизменна, runtime run/tolerances/budgets — actual current attempt |
| State summary7 | Exact summary6 key set с schema7, protocol5/runtime plan2/archive2/cert3; IDs/candidates/residuals берутся из реальных group records | scalar trial packets не синтезируются |
| Console execution4 | Exact execution3 wrapper key set с schema4/base1-or2 и new package6/archive2, source+attempt/archive/execution counters | Preflight known zero; failed pre-Start unknown source/archive/attempt — null, не fake empty family |

Минимальное C++ configuration расширение: optional `CandidateWindowPolicy` рядом с `ConfiguredNativeTraining::composite`, допустимый только с policy.schema2/cold7; один explicit encoder/decoder пары policy2+window policy. В `NativeTrainingPlan` window policy не дублируется: authoritative экземпляр уже в protocol5.candidateWindowMeasurement. Validate сравнивает plan common limits/context/geometry с ним; missing/mixed optional запрещены. API details можно упростить при implementation, exact wire/content bindings менять молча нельзя.

Console не требует новой универсальной команды. `TimeLearnerTrainingJob.cpp` читает новый nested cold7 существующего signed training job и сохраняет input job неизменным. `TimeLearnerCompositeArtifacts.h` явно принимает package5 или6 с их ожидаемым archive/protocol, пишет каждый record sidecar и ВСЕ actual primary по embedded refs. Execution4 связывает полный artifact closure, actual source/family/model hash и counts. `TimeLearnerTransportJob.cpp` export/import/evaluate использует package6 factory; после recognition/calibration сохраняются отдельные source/current models и finalization status, без автоматического признания OriginalExact.

Root Python chunk: explicit cold7/record2/package6/summary7/cert3/execution4 dispatch в существующих composite readers/adapters; primary resolver selfcontained+same-bytes external mirror, source-policy/proposal replay, current/latest final sweep, actual-model import/metadata checks, managed pipeline/contained runner и renderer. Не проектировать composite в `trial_packet`/scalar3. Существующие Python cold6/package5 readers остаются отдельной ветвью. Новую extraction/adapter работу координировать с владельцем Root Python branch, не править её параллельно.

Конкретные Root файлы отдельного Python chunk (из существующей reader branch, не её параллельная перезапись): `composite_configuration.py`, `composite_measurement_contract.py`, `composite_source_evidence.py`, `composite_raw_evidence.py`, `composite_measurement_evidence.py`, `composite_primary.py`, `composite_runtime_plan.py`, `composite_certificate_evidence.py`, `composite_package_evidence.py`, `composite_summary_evidence.py`, `composite_execution_evidence.py`; dispatch в `learned_evidence.py`, `stopped_evidence.py`, `native_evidence.py`, `live_training_worker.py`; artifact closure в `native_pipeline_worker.py`, `managed_pipeline.py`, `artifact_bundle.py`. Для новой независимой арифметики/replay нужен небольшой `candidate_window_evidence.py` по versioned specification, а не synthetic scalar projection. Tests обновляют corresponding modules и actual-native-archive/final-sweep fixtures. Old reader schemas не теряют свои negative/duplicate/type guards. Сумма primary bytes — materialized logical refs, не deduplicated blob-store size; historical prefix caps повторяются независимо от C++.

## 8. N0/N1 normalization, C0Off и отдельный N=1

N0/N1 здесь — normalization modes, а N — число inputs. Оба режима normalization поддерживаются новым Train5 при N≥2. N0 меняет реальные Ns по прежнему bounded integer path, сохраняет repeats. N1 использует прежние effective resistance domains/logRs bounds; preview/domain queries и edits не пересекают активную N+2 группу. Rs feature в window policy — actual existing control knob; полный heterobank graph/weights/links остаётся в binding. Uniform physics changes выполняются storage images, не прямым обходом child properties.

C-trim Off — базовый поддерживаемый путь без искусственного C0 и без требования C-property у любой потенциальной модели. Если current owned C0 уже есть, он сохраняется и проверяется; новый C edit разрешается только после существующего capability/baseline validation. On/BoundC0 использует immutable original origin и actual current scales; warm не capture новый baseline из trained graph.

**N=1 не закрывается contract5.** Существующий scalar/native protocol3 training/export/Test путь сохраняется и должен иметь отдельные Classic/Branch × N0/N1 regressions. Cold7/Train5 для N=1 выдаёт явный unsupported multi-input-method reason до queue; автоматического fake N+2 или cert3 нет. Полный рефакторинг сохраняет открытый пункт: математический single-input multi-peak/assigned-impulse contract и его accepted implementation. Для штатной single-impulse модели N=1 работает прежний поддержанный путь; способность выбрать правильную вершину при нескольких волнах от одного input нельзя объявить доказанной legacy scalar pass. Завершение STEP3 multi-input не закрывает этот пункт полного плана.

Legacy scalar3 recovery `advance_unassigned_burst` сохраняется там, где уже поддержан. Новая cold7 base1–4 не переносит автоматически эту raw/burst-specific политику на Missing/Ambiguous N+2: такое combined-mode поведение остаётся явно неподдержанным до отдельного versioned controller rule. Это не исключение прежнего рабочего режима из репозитория и не основание ослаблять новый measurement. Общая invalid-budget/Reject path остаётся bounded и честно учитывает отказные группы.

## 9. Последовательность отдельных source commits и gates

1. **S3-A0 mechanical preflight/core metadata extraction**: только non-protocol scalar validation и общие accepted metadata helpers; old formulas/order/97 regression и p4 bytes сохраняются. Отдельный pin/A-B; не смешивать с feature PASS.
2. **S3-A typed consumers5 + cert3**: closed refs constructor, private factory candidate guard, Arm/Consume/Reject5, fresh final identity, certificate3 serializer/replay skeleton fail-closed для service. Actual core fixtures с storage/scheduler/primary. Это не Console endstate.
3. **S3-B service composition5**: source/session ID до authority, safe start/one-group ownership, allN release, edit/warm/retarget/Need/lifecycle/callback delivery, journal/ledgers и service archive2 selections. Genuine actor/service Train run, не ручная выдача scalar в search.
4. **S3-C cold7/package6/summary7/runtime2/Console4**: exact codecs, actual-model export/import, stopped boundary, fake-template negative, actual Train→export/import→Test. Только closed checkpoints; callbacks не portable state.
5. **S3-D independent Root audit/pipeline/visual closure**: actual produced complete/ambiguous/partial/C0/warm bundles; все full/omit/repeat presented patterns, all soma channels+actual source, reference/final raw peaks/residuals и before/after graphs. Никаких CSV из ожиданий assertions.

Source preparation следующих commits может идти до завершения предыдущих remote gates в новых ветках. Runtime dispatch/общие experiments/recommendV2/defaults не включаются до source review и требуемого acceptance. Frozen STEP2/callback jobs не переписываются; новые fixes — новые commits и preserved negative evidence. Затем merge --no-ff в develop по принятому этапу, без rebase/cherry-pick/amend.

## 10. Meaningful acceptance inventory (названия групп, не обещанные counts)

| Группа | Обязательные controls и ожидаемый смысл |
|---|---|
| `CandidateWindowTrainingCore` | Closed allN refs → typed search/anchor/final; raw3/raw6/typed4/pure diagnostic/public scalars не допускаются; rehashed false proposal/refs/source/current revision/epoch/instance rejected; mixed anchor candidate rejected |
| `CandidateWindowFinalIdentity` | Все N fresh current sweep; mixed/old whole sweep, Search-as-Final, wrong origin/time offset, renamed primary invariance; identical pattern-relative arrivals при разных absolute begins; Need=false/Reset/Default/rebuild между close и consume — без нового certificate |
| `NativeCandidateWindowService` | Classic/Branch × normalization0/1 × CalculateMode0/1; autostart и explicit start; owned edit growth за initial window с настоящим shifted peak; partial/missing/merged/clipped/Unknown остановки; новый candidate window не выбирается по residual |
| `NativeCandidateWindowWarm` | Cold allN original targets, trained current graph, Reset/import → original P0/C0/proofs без recapture; new attempt counters; incomplete capture constraints; changed source/storage/profile/policy invalidates; Default/retarget не revive |
| `NativeCandidateWindowDimensions` | Actual N4/N6 distinct Branch attachments `[N..1]` и реальные ordinal/bank/IsConnected witnesses; отдельно legacy shared-bank negative. Routing closure не заменяет allN valid targets или научную convergence |
| `NativeCandidateWindowPackage` | Production package6/summary7/cert3 writer → strict independent replay → actual graph import; trained template fake заменённый исходной config-моделью должен отказать; source restored full mask; rename primary меняет document ID, не semantic proofs |
| `CandidateWindowConsole` | Реальная cold7 job → preflight → Train → stopped/completed export → import → Test, точный artifact closure/counters/source/actual model; pre-Start failure — null/unknown вместо fabricated archive |
| `LegacyWindowAB` | Scalar97 + protocol4 composite/service/package/callback inventories и old config/serializer fixtures по точным IDs; p4 untouched common math/bytes. Counts берутся из compiled inventory и macro expansion, не общей regex TEST |
| `SingleInputPreservation` | N=1 single-impulse old path Classic/Branch N0/N1 и COff; отдельный multi-peak pending label, отказ cold7 до queue; никакого общего “N1 passed” вместо раскрытия scope |

Native cases сохраняют actual raw samples/profiles/graphs и используют реальные clocks/раздельные group+attempt model/wall caps. 20k Branch N+2 может быть дорогим: fixture budgets объявляются честно, эффективность не доказывается zeroClock или обрезанными traces. Default sync `.02` имеет реальный OutsideTolerance/non-Exact контроль; `.2` инженерные plumbing cases могут быть отдельными явно помеченными cases, но не доказательством исходной научной сходимости. Legacy август4/8–6/8 визуально рабочие результаты исходного протокола остаются действительными историческими наблюдениями; новые permuted/gapped protocols оцениваются отдельно и их провал не переписывает историю.

Локально в этом предложении выполняются только Git/text/diff metadata checks. Численные tests, C++ compile/syntax-only, remote jobs и изменения active caches не выполняются.
