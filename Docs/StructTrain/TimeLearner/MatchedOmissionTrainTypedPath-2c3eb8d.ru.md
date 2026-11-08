# Конкретный типизированный путь matched witness в Train

Дата: 2026-11-08. Статус: source-based design; реализация, численные проверки и повышение evidence acceptance этим документом не выполнены. Документ дополняет `MatchedOmissionTrainingIntegration.ru.md` точками изменения production-кода. Политика `matched-omission-assigned-maximum-v1`, физика и критерий full-horizon не меняются.

Источники зафиксированы независимо от текущих рабочих деревьев:

- `R` — корневой репозиторий, `90231e7ebc752ca5aca4a6c4a4e211d1c6e1323a`.
- `P` — `Libraries/Nmsdk-PulseLib`, `2c3eb8dcc128b75da3d3f1e6801ec2a2e0a0090b`, фактический gitlink R. Рабочее дерево отдельного Pulse checkout могло оставаться на FCC; использовался `git show` указанного SHA.
- Запуски C++, обучения, сети и серверов в этой работе не выполнялись. Proposed API ниже — проект изменений после codec gate, а не описание уже реализованной поддержки.

## 0. Независимые prerequisites: codec и применимость измерения

В pinned source v1 является **diagnostic-only** даже после успешного portable decode/Valid assignment. Codec closure доказывает согласованность записанных bytes/context, а не достаточность определения maximum для цели обучения. Уточнённый пользователем математический контракт: **отдельная ранняя вершина валидна, даже если небольшой её хвост влияет на более поздний пик; реально слившиеся пики сохраняют ambiguous**. Full-horizon influence-exclusive v1 может отвергать именно такой допустимый отдельный ранний пик, поэтому для Train этому контракту не соответствует и не eligible. Новая методика/basin-necessity analysis остаётся предметом review, ещё не реализована. Этот документ не исправляет несоответствие изменением tolerances, diagnostic owned-window hint или cert-eligible flag.

Все положительные пути `CaptureMatched`/`ConsumeMatched`/Exact ниже **условны**: сначала должно существовать принятое определение нового training measurement method, удовлетворяющего этому математическому контракту, и его support contract, затем codec/typed integration gates. Для v1 такого разрешения по одному codec success не возникает. Общие типы/serialization должны быть method-параметризованы. Новый basin/window-based метод получает отдельные ID/schema/policy и собственные доказательства; v1 результаты не переклассифицируются.

## 1. Что уже есть и где заканчивается повторное использование

| Точка | Факт исходника | Следствие |
|---|---|---|
| P:`Core/TimeLearner/NativeTrainingService.cpp:50` | Start требует protocol3/probe3 и inputWindows размером N | Новый метод требует самостоятельной проверки конфигурации; нельзя просто передать raw6 в старый путь |
| P:`Core/TimeLearner/NativeTrainingService.cpp:170` | Request выбирает одно окно; его onPrepared вызывает search Arm | Для группы нужен отдельный prototype без этого callback-wrapper |
| P:`Core/TimeLearner/NativeMatchedOmissionGroup.cpp:152` | Группа создаёт настоящие native raw6 requests с subset | Сохраняется raw6; не создавать якобы валидный ProbeObservation3 |
| P:`Core/TimeLearner/NativeMatchedOmissionGroup.cpp:171` | Исходный onPrepared вызывается на каждом из N+2 raw trials | Callback writer сохраняется для каждого trial; Arm обучения выполняется один раз на группу |
| P:`Core/TimeLearner/NativeMatchedOmissionGroup.cpp:204` | Completed означает закрытие группы, assignment может быть отрицательным | Completed не является разрешением Consume/Capture/certificate |
| P:`Core/TimeLearner/FinalVerification.h:46` | ValidatedProbeMeasurement — публичные три double без proof identity | Для matched недостаточен; нельзя передать произвольные scalar values как доказательство |
| P:`Core/TimeLearner/BoundedTraining.cpp:152` | Вход bounded controller жёстко требует protocol3 | Изменить явную диспетчеризацию поддержанных методов, а не убрать проверку схем вообще |
| P:`Core/TimeLearner/BoundedTraining.cpp:822` | После проверки observation используется raw, arrival, plateauEnd | Эти расчёты ranking/residual/N0-repeat можно вынести в общий приватный путь без изменения формул |
| P:`Core/TimeLearner/FinalVerification.cpp:370` | Certificate возникает только после accepted для всех N | Сохранить общий all-input Finish; заменить источник accepted на validated matched measurements |
| P:`Core/TimeLearner/NativeTrainingProof.cpp:25` | Replay принимает только single-probe packets | Нужен composite replay; старый replay не расширять lossy projection в observation3 |
| P:`Core/TimeLearner/NativeLearnedState.cpp:275` | Learned storage уже использует версии 1,2,3,4 | Новую composite package нельзя назвать schema3 |
| P:`Core/TimeLearner/ConfiguredNativeTraining.cpp:245` | Cold configuration уже использует версии 1–5 | Предлагаемая следующая версия — 6, с отдельной matched веткой |

## 2. Минимальные типы и граница доверия

Вынести **без изменения полей/правил** `MatchedOmissionPolicy` из `MatchedOmissionAssignment.h` в новый `MatchedOmissionPolicy.h`. Его могут включать и `FinalVerification.h`, и assignment. Это устраняет цикл: assignment сегодня сам включает FinalVerification. Не делать FinalVerification зависимым от NativeTrainingService или Rdk.

В `FinalVerification.h` добавить общий независимый от Rdk контракт для нового метода:

```cpp
// Существующие protocol1/2/3 остаются прежними.
struct MatchedVerificationMethod {
    std::string methodId;
    MatchedOmissionPolicy policy;   // полная политика, не только произвольная строка ID
    // Native backend сегодня умеет только exact operational v1 ID;
    // это НЕ регистрация v1 как применимого для certificate.
};
// VerificationProtocol schema4: ровно одна matched method; старые wave/window
// поля не должны выбирать альтернативный алгоритм, отсутствуют в новой JSON ветке.

struct MatchedMeasurementIdentity {
    std::string runId, logicalTrialId, groupId, inputId;
    std::string protocolSha256, policySha256;
    std::string baseModelRevision, sourceC0WitnessId, candidateWitnessId;
    std::string ownerScopeId; // group-independent producer scope
    std::size_t modelEpoch, inputIndex, channel;
    ProbeRouting routing;
};
struct PreparedMatchedMeasurement {
    MatchedMeasurementIdentity identity;
    PreparedVerificationProbe fullBefore; // настоящая preparation первого full
    std::string resetBinding, groupInstanceBinding;
};
class ValidatedTrainingMeasurement {
public:
    const MatchedMeasurementIdentity& Identity() const;
    double RawPotential() const;
    double Arrival() const;    // относительно ФАКТИЧЕСКОГО origin event
    double PlateauEnd() const; // относительно того же события
    const std::string& EvidenceSha256() const;
private:
    friend class NativeMatchedTrainingValidator;
    ValidatedTrainingMeasurement() = delete;
    ValidatedTrainingMeasurement(MatchedMeasurementIdentity, double raw,
        double arrival, double plateauEnd, std::string evidenceSha256);
    // Нет публичного default/aggregate/JSON constructor.
    // Сохраняются actual assigned/origin event times, максимум/plateau sample
    // indices, fullBefore effective revision и digest полного group envelope.
};
```

Точная упаковка identity не обязана совпасть с этим эскизом; обязательны отдельные sourceC0/candidate bindings, явный метод и неоткрытый конструктор доказанного значения. Существующий `ValidatedProbeMeasurement` и старые публичные Consume не удалять: вызывающий код legacy-пути остаётся совместимым, но не может получить matched proof через публичные double.

Новый `NativeMatchedTrainingMeasurement.h/.cpp` включает native group, codec и TrainingCapacitance. Он содержит native/replay validator с одинаковым набором инвариантов и различными источниками boundary evidence. Нижний `ValidatedMatchedWitness` — закрытый operational proof, **не** `ValidatedTrainingMeasurement`:

```cpp
using MatchedWitnessValidation =
    std::variant<ValidatedMatchedWitness, RejectedMatchedMeasurement>;

static MatchedWitnessValidation NativeMatchedTrainingValidator::Validate(
    const VerificationProtocol&, std::size_t inputIndex,
    const PreparedMatchedMeasurement& expected,
    const NativeMatchedOmissionResult& completeGroup,
    const MatchedTrainingBoundaryEvidence& boundary,
    const MatchedOmissionPrimary& primary);

static std::optional<ValidatedTrainingMeasurement>
NativeMatchedTrainingValidator::QualifyForTraining(
    const ValidatedMatchedWitness&, const ResolvedTrainingMethodContract&);
```

`MatchedTrainingBoundaryEvidence` несёт source capture C₀ witness, candidate witness, actual before/after revision и C readbacks, raw-trial→candidate-witness mapping, исходную producer owner scope/lifecycle binding и accounting. Live factory получает их от владельца service, replay factory — из полного подписанного/хешированного source package и primary, с повторной проверкой графа/storage closure. Декодер portable group сам по себе этого контекста не имеет и не выдаёт `ValidatedTrainingMeasurement`. `ResolvedTrainingMethodContract` выдаётся только явной production support registration после applicability gate, не является публичным aggregate/bool `certificateEligible`. Для текущего diagnostic-only v1 qualification отсутствует; refs/certificate не строятся. Export/import проверяют точный method contract/revision, не произвольное утверждение пакета о своей eligibility.

Порядок factory:

1. Проверить method/protocol/policy digests и input→stimulus/channel mapping; источники ISI/profile/длительности совпадают с protocol/config, N>=2, recordSpikes=false, canonical pulse IDs; raw full-horizon capture не зависит от legacy PeakWindow. N=1 новый путь **явно отклоняет**: native group сейчас требует multi-input, P:`Core/TimeLearner/NativeMatchedOmissionGroup.cpp:27`.
2. Проверить raw+primary closed schema существующим production codec и повторить `SelectMatchedOmissionMaximum` без изменения v1. Ни закешированный assignment, ни флаг Completed не достаточны. Все N+2, маски, события, actual ISI, restoring, sample grids, reset/instance/model bindings проверяются.
3. Сверить точные ожидаемые run/logicalTrial/group/input/revision/epoch и first-full preparation. Модель и C readback неизменны между raw trials; все raw trial IDs уникальны и принадлежат ровно этой группе.
4. Проверить sourceC0WitnessId — исходный `captureWitnessId` этой target family. Он не заменяется текущим trimmed C. candidateWitnessId относится к текущей revision, сохраняет C₀ и полный active/dormant inventory. References берутся при capture revision/epoch; search/final могут иметь другие candidate witnesses, но тот же source C₀ family.
5. Только `assignment.validity==Valid` с измеренным **fullBefore** maximum создаёт operational proof. Training proof дополнительно требует `QualifyForTraining` по принятому method contract; для текущего v1 этого разрешения нет. Прочие complete negative сохраняются как rejected measurement, без raw scalar, пригодного для обучения. Partial/timeout/restoration failure не становятся complete portable evidence.
6. Найти actual assigned и origin события в fullBefore по IDs протокола; взять rawPotential и plateau endpoints из выбранных действительных samples. `arrival = maximum.firstTime - actualOrigin.time`, `plateauEnd = maximum.lastTime - actualOrigin.time`. Не вычитать predicted onset/delay и не использовать amplitude вместо rawPotential.

Отдельная тонкость instance identity: P:`Core/TimeLearner/NativeMatchedOmissionGroup.cpp:71` хеширует `groupId` вместе с путями/адресами. Поэтому `modelInstanceBinding` **не равен между разными группами одного графа**. Для Train нужен отдельный group-independent owner scope либо явное recompute ожидаемого group-specific binding из фактического service-owned graph. При import сохраняется исходный producer instance binding, а не подставляется адрес нового восстановленного объекта. Replay не утверждает live-process attestation.

## 3. Request / OnPrepared / AfterTick: один Arm и два уровня FSM

`NativeTrainingService.h/.cpp`:

```cpp
NativeProbeRequest RequestMatchedPrototype(std::size_t input,
    const std::string& run, const std::string& logicalTrial,
    const std::string& revision, std::size_t epoch);
void BeforeTick(const NativeTrainingAdapter&, const NativeProbeBindings&,
                double modelTime, double wallTime); // новая overload
// Старая BeforeTick(a,time,wall) продолжает legacy single-probe путь;
// для matched без actual bindings — явный отказ, не fallback.
```

В `NativeLearnerLifecycle.h` P:`Core/TimeLearner/NativeLearnerLifecycle.h:72` overload вызывается с `owner.NativeProbeModelBindings()` из существующего friend lifecycle. Не открывать protected bindings через новый публичный unrestricted getter и не собирать граф из строк в чистом bounded controller. Существующий `BindNativeTraining` и методы apply/assess/edit-depth можно сохранить.

Service владеет `unique_ptr<NativeMatchedOmissionGroup>`, expected group context, `bool logicalArmed`, per-group harvest offset и раздельными reference/final/observed group records. NativeProbeExecutor остаётся единственным владельцем transient physical probe; group управляет только очередью подпроб, service — только очередью логических измерений и edits.

```text
BeforeTick(service, actualBindings):
  enforce attempt Need/time/execution; если activeGroup:
      group.BeforeTick(groupAdapter); return
  выбрать reference или search.NextAction
  edit/domain action: существующий atomic путь; activeGroup отсутствует
  measurement action:
      reserve logical group + достаточно N+2 burst/sample budget
      freeze revision/epoch/parameters + sourceC0/candidate witnesses
      создать новый groupId и отдельный prototype (НЕ Request с Arm-wrapper)
      group.Start(plan, actualBindings, modelTime, wallTime)
      group.BeforeTick(groupAdapter)
  затем штатный NativeProbeExecutor.BeforeChildren

onPrepared каждого raw trial:
  native capture делает прежний Arm/actual-ISI readback
  external evidence Prepared вызывается для КАЖДОГО raw trial
  только fullBefore (точный group/native/0) и !logicalArmed:
      построить PreparedMatchedMeasurement из actual preparation
      search.ArmMatched(actionSerial, prepared) // refs без search Arm
      logicalArmed = true
  на omit/fullAfter logical Arm запрещён; raw callbacks продолжаются

AfterTick(service):
  штатный NativeProbeExecutor.AfterChildren уже выполнен
  group.AfterTick(groupAdapter) забирает только raw packet
  harvest новые packets → observed/raw sink, execution/revision/C checks
  если group Running: return (activeAction НЕ сбрасывать)
  сохранить complete либо partial group и accounting
  если terminal failure: reject/finish, scalar proof не создаётся
  если Completed: Validate(...); QualifyForTraining(operationalProof, methodContract)
      qualification unavailable: сохранить diagnostic; не Capture/Consume/Exact
      reference: accumulate validated refs; при N → CaptureMatched
      search/final: ConsumeMatched(proof) либо RejectMatched(failure)
  очистить activeGroup/action только после сохранения и проверки restoring
```

Queue decorator service вызывает существующий `BindTrialCapacitance` **до каждого** raw queue; после каждого результата — `ValidateTrialCapacitance`. Текущие реализации P:`Core/TimeLearner/NativeTrainingService.cpp:146` и P:`Core/TimeLearner/NativeTrainingService.cpp:155` переиспользуются, но добавляется group→capture/candidate binding. Не пытаться привязать только логический trial, пока фактические IDs имеют `/native/k`.

Raw sink не должен вызываться лишь в конце группы: `EvidenceWriter::Prepared` открывает новый CSV на каждом raw preparation и требует закрыть предыдущий в Observation (R:`App/NeuroModelerConsole/TimeLearnerProbeEvidenceWriter.h:27`). Каждый завершённый raw packet закрывает собственный sink ровно один раз. Adapter.takeResult decorator сначала сохраняет полученный packet, не теряет его при исключении sink/проверки; дальнейшая harvest не должна дублировать sink. Нужен явный seen/raw-harvest ledger, не вывод из размера одного vector после fail.

Все error/Need falling/time limit/Reset/Default/build invalidation пути используют общий `CancelActiveMeasurement(adapter, reason)` **до** Finish/сброса group, сохраняют partial raw packets и исход restore. Нынешний `RecordCancelled` забирает только один packet, P:`Core/TimeLearner/NativeTrainingService.cpp:359`, а Reset/Default сбрасывают controller/executor отдельно, P:`Core/TimeLearner/NativeLearnerLifecycle.h:109` и P:`Core/TimeLearner/NativeLearnerLifecycle.h:120`. Не оставлять group после Reset и не продолжать legacy между подпробами. Internal probe Reset ребёнка не должен рекурсивно сбрасывать внешний learner/session; действующие lifecycle-depth scopes сохраняются. Ни group, ни service не вызывает Calculate/Build/Default/Reset вручную в обход executor/Rdk hooks; возвращаемые bool общих hooks не превращаются в новый gate.

## 4. CapturedReferences, BoundedTraining, all-input FinalVerification

Добавить рядом со старыми входами:

```cpp
CapturedReferences CapturedReferences::CaptureMatched(VerificationProtocol,
    const std::vector<ValidatedTrainingMeasurement>&);
void BoundedTrainingSession::ArmMatched(std::size_t serial,
    const PreparedMatchedMeasurement&);
void BoundedTrainingSession::ConsumeMatched(const ValidatedTrainingMeasurement&,
    const std::string& actualModelRevision);
void BoundedTrainingSession::RejectMatched(const RejectedMatchedMeasurement&,
    const std::string& actualModelRevision);
void FinalVerificationSession::ArmMatched(const PreparedMatchedMeasurement&);
void FinalVerificationSession::ConsumeMatched(const ValidatedTrainingMeasurement&,
    const std::string& actualModelRevision);
```

`RejectMatched` final имеет ту же семантику invalid/retry budget; тип failure не может попасть в accepted. Группа негативного v1 не переходит автоматически в существующий `AdvanceUnassignedBurst`, который анализирует observation.burstAssignments, P:`Core/TimeLearner/BoundedTraining.cpp:783`. Для первоначальной matched реализации это отдельный explicit unsupported recovery policy; иное решение потребует собственного typed negative-candidate contract/test, не ослабления v1.

`CaptureMatched` требует ровно N различных inputs/groups, общего capture revision/epoch/sourceC0/protocol, правильного stimulus/channel, immutable proof IDs. В `CapturedInputReference` для нового метода сохранить measurement evidence ID, group ID, sourceC0 и method binding (old fields/old bytes без нового значения остаются прежними). Scalar target = выбранный фактический raw максимум исходной группы, не unit C, predicted gain или diagnostic owned-window maximum.

`BoundedTraining` извлекает общий приватный `ConsumeValidatedScalar` из P:`Core/TimeLearner/BoundedTraining.cpp:822`. Оба входа сначала выполняют свои самостоятельные валидаторы/anti-replay/Arm проверки, затем используют тот же residual/ranking/candidate-repeat код. Anchor хранит proof ID и revision/epoch, current/anchor group IDs не взаимозаменяемы. N0 repeat означает новое полное N+2 измерение anchor/input на каждом повторе, а не несколько samples одной группы.

`FinalVerification` извлекает приватный `AcceptValidatedMeasurement` из P:`Core/TimeLearner/FinalVerification.cpp:361`; сохраняет existing `Finish` math. `accepted` содержит доказательства для всех N, включая последний anchor; не использовать успешные search groups или capture groups как финальные. Любой edit/C edit/restore-best, revision/epoch drift или invalidation очищает accepted/final groups и certificate. Finalization запускается на замороженном конечном candidate graph, без edits между N группами. Только fresh all-input final gate даёт certificate Exact/OutsideTolerance с прежними tolerances; OutsideTolerance не переименовывается в успех обучения.

## 5. Бюджеты с явными единицами

В новой конфигурации/summary не переопределять молча значение старого `maximum_probes`. Новый метод задаёт explicit units:

Конкретные новые names: `maximum_reference_measurement_groups`, `maximum_invalid_reference_groups`, `maximum_search_and_final_measurement_groups`, `maximum_invalid_search_and_final_groups`, `maximum_attempt_native_bursts`, `maximum_attempt_sample_frames`. Per-group `policy.maximumNativeProbes/maximumTotalSamples/maximumSamples` уже имеют отдельные единицы native bursts/group frames/burst frames. Их не переименовывать в число групп. Внутри shared controller разрешено явно сопоставить `maximum_search_and_final_measurement_groups → BoundedTrainingConfig::maximumProbes` и remaining final groups → `VerificationConfig::maximumProbes`; новый JSON/summary печатает unit и оба actual counters. Такое сопоставление делается ровно в method-aware plan maker, не через рассеянные умножения N+2 в скриптах.

| Счётчик | Единица / списание |
|---|---|
| reference/search/final measurement groups | Один логический input measurement; резервируется один раз до group Start; invalid/retry тоже расходует |
| native bursts | Фактически queued raw trials; полная группа N+2; partial расходует фактическое число; N0 repeats не бесплатны |
| samples per burst / per group / per attempt | Реальные frames, отдельно от N physical channel values; spec.maximumSamples — frames; checked multiplication/сложения |
| edits/domain assessments/candidates | Существующие отдельные finite budgets, без изменения единиц |
| model_seconds/wall_seconds | Отдельно whole-attempt и group enforcement, monotonic native clocks |

Резерв на полную группу предотвращает заведомо незавершаемый запуск при остатке меньше N+2. Actual counters не подменяются резервом; pre-prepared failure, cancellation, reference recapture и final retries видны в ledger. Service whole-attempt clocks уже существуют, P:`Core/TimeLearner/NativeTrainingService.cpp:327`; group clocks тоже существуют, но в result сегодня остаются только declarations, P:`Core/TimeLearner/NativeMatchedOmissionGroup.h:28`. Новая Train envelope сохраняет enforced live clock snapshots/counters отдельным producer record; portable codec1 не получает ложное elapsed/enforcement attestation. Независимый reader проверяет арифметику/closure, а не утверждает незаписанную реальную wall-time гарантию.

## 6. Хранение, export/import и independent readers

Версии ниже предлагаются как **следующие свободные в pinned source**, резерв проверить заново при реализации:

| Контракт | Existing | Proposed matched |
|---|---|---|
| VerificationProtocol | 1–3 | 4: method + полная immutable policy; общий mapping/profile/origin; не Observation/ProbeSpec4 |
| ProbeSpec raw | 1–6 | raw6 сохраняется, schema3 prototype текущей group остаётся только declaration |
| matched portable evidence | 1 | 1 без изменения `diagnostic_only=true` / `training_certificate_eligible=false` |
| cold configuration | 1–5 | 6: отдельная method ветка, policy/group budgets; без обязательных legacy windows/peak selection |
| learned/stopped package | 1–4 | 5: composite Train envelope + sourceC0 history + group/primary closure |
| TrainingCertificate | 1 | 2 для нового метода: exact method/policy/protocol/sourceC0 + reference/final proof IDs |
| training summary | 1–5 | 6 для нового метода: explicit units/group ledgers; старые shapes неизменны |

Не использовать холодный schema3 decode как промежуточную конфигурацию с фиктивными окнами. В `MakeConfiguredNativeTrainingPlan` P:`Core/TimeLearner/ConfiguredNativeTraining.cpp:143` новая ветка строит protocol4 и real group prototype. Legacy ветка byte/meaning compatible. `ValidateBoundedTrainingInputs` проверяет либо старую schema3, либо новый полный matched contract; unknown schema/method/policy отклоняются.

Matched Train требует `recordCapacitanceHistory=true` даже без C-search: исходный actual C₀ нужен для identity reference family, а не для разрешения trim. Существующий owner binding вызывается как metadata-only bind/validate по штатному пути перед service Start; repeat не recapture. Unbound/неподдержанный C₀ — явный отказ данного method, не придуманный unit witness.

`Encode/DecodeVerificationProtocol` P:`Core/TimeLearner/ProbeEvidenceJson.cpp:133` / P:`Core/TimeLearner/ProbeEvidenceDecode.cpp:117` требуют самостоятельной schema4 ветки. Старый Decode намеренно использует временный data-only ProbeSpec primitive parser; **новую protocol4 нельзя передать через него**, потому что ProbeSpec4 уже означает characterization. Выделить общие strict primitives/profile/mapping decoder helpers, без создания fake observation. Certificate `SchemaVersion()` сегодня всегда1, P:`Core/TimeLearner/FinalVerification.h:108`; для нового пути это хранимый/вычисляемый по методу version и method-aware Matches, а не безусловное переименование всех старых certificates.

`ReplayNativeMatchedReferencePrefix` / `ReplayNativeMatchedTrainingProof` — новые overload/types рядом с существующим `NativeTrainingProof`. Принимают group envelopes + primary map + C₀ history, вызывают тот же validator, затем `CaptureMatched`, `FinalVerificationSession::ArmMatched/ConsumeMatched`. Нельзя replay только cached residuals, только assignment или плоские raw packets без group inventory. Completed proof требует N source capture groups и N свежих final groups (плюс явно сохранённые rejected retries), order/run IDs и отсутствие overlap; stopped proof допускает partial group только в diagnostic section, не references/certificate. Dynamic checkpoint / mid-probe resume по-прежнему отсутствует.

Реальные export/import точки: `NativeLearnedState.cpp::ExportNativeLearnedStateImpl/PrepareNativeLearnedState`, P:`Core/TimeLearner/NativeLearnedState.cpp:210` и P:`Core/TimeLearner/NativeLearnedState.cpp:317`, методы обоих owners `ExportNativeLearnedState`. Символа `ModelLearnedExport` в pinned Pulse source нет; этим термином нельзя подменить конкретный сериализатор. `RawReferences`, `Plan`, `Configuration`, `BoundaryHistory`, RestoreBoundary/RestoreStoppedBoundary тоже получают method-aware ветки, а не только top-level encoder. ControllerVersion2 сегодня требует canonical protocol equality — сохранить требование, расширив canonical maker новым методом.

Новая package5 хранит immutable source capture witness, per-candidate witnesses, group→witness и rawTrial→witness mappings, full portable group objects и доступные canonical primary bytes/hash inventory. Для самодостаточного model archive import существующая `PrepareNativeLearnedState(package,storage,environment,implementation)` не принимает внешний primary resolver: либо package5 встраивает canonical primary blobs с closed encoding/inventory/size budget, либо вводится **явный новый overload с resolver**, а old overload отказывает package5 без bytes. Для минимального самодостаточного ModelLearnedExport предлагается embedding с total byte limit; arbitrary file access из archive запрещён. Текущий portable codec не менять: package envelope переиспользует его результат как нижний evidence layer и отдельно добавляет Train bindings.

В root writer `TimeLearnerProbeEvidenceWriter.h` R:`App/NeuroModelerConsole/TimeLearnerProbeEvidenceWriter.h:43` Finalize переименовывает файлы в зависимости от stopped/completed outcome. Для нового wrapper разделить два ID (в existing codec этого механизма нет):

- `semanticMeasurementProofId` — хеш **закрытого canonical projection** spec/policy/source/native packets/raw CSV hashes+byte sizes/roles+omitted ordinals и Train sourceC₀/candidate/epoch/model/method bindings, без `relative_path`. Именно этот ID связан с immutable measured condition и, условно после applicability gate, reference/certificate.
- `artifactDocumentId` — хеш полного portable JSON/envelope с actual relative paths и artifact inventory. При штатном rename меняется только artifact mapping/document ID; semantic ID прежний только при идентичных bytes/roles/bindings. Projection version фиксирован; произвольные неизвестные поля не игнорируются.

После Finalize можно ребиндить пути и пересоздать artifact document, не переписывая измеренные условия. Обязательны rename regression (одинаковые bytes дают прежний semantic ID) и tamper regression (другие bytes/role/context при прежнем semantic ID отвергаются). Не принимать пересчитанный злоумышленником новый semantic ID как тот, который связан старым reference/certificate. Альтернатива — stable immutable group filenames с самого начала; старый writer output сохранить для старых jobs. Group sink связывает groupId/role/omitted ordinal с raw trial ID и primary; scalar summary не заменяет raw evidence.

Обновить actual root входы R:`App/NeuroModelerConsole/TimeLearnerTrainingJob.cpp:209` (raw/group sink wiring) и R:`App/NeuroModelerConsole/TimeLearnerTrainingJob.cpp:227` (learned export), также `ExecuteLive` source-solo capture до recognition import. Python отдельная ветка: `learned_evidence.py::audit_learned_state`, `stopped_evidence.py::audit_stopped_state`, `native_evidence.py::audit_training_summary`, `capacitance_boundary_evidence.py`, `native_pipeline_worker.py::audit_execution`, readers finalization boundary. Нижний parser `matched_omission_portable.py::audit_portable_matched_evidence` переиспользуется; старый `audit_probe` жёстко schema3 и не должен быть «починен» lossy raw6→3 projection.

## 7. Минимальные gates реализации — подготовить, запускать только на серверах

1. Protocol4/config6 strict roundtrip, unknown/duplicate/malformed fields rejection; старые fixtures protocol1–3/config1–5/package1–4/certificate1 дают прежние bytes и outcomes. Protocol4 never parsed as characterization ProbeSpec4.
2. Typed proof нельзя aggregate/default-конструировать; portable decode/diagnostic owned-window result и operational v1 Valid не convertible в training-qualified measurement. При отсутствии принятого applicability contract v1 не попадает в references/Exact. Positive scalar-only test helper и public eligibility bool не доступны production API.
3. Classic/Branch × N0/N1: реальная N+2 группа, callback count N+2, raw CSV закрываются N+2 раз, logical Arm ровно1, Consume ровно1; pending action не сбрасывается на omit.
4. Mutate по одному binding: run/group/logicalTrial/input/assigned/channel/profile/policy/protocol/revision/epoch/reset/instance/ISI → отказ до capture/consume. Cross-group instance bindings корректно различаются; одинаковый groupId на другом graph не replayable.
5. C₀ missing/unbound/mutated, candidate readback drift, dormant history lost, rawTrial→чужой witness, witness от другого capture family → отказ. Trim candidate не становится новым исходным C₀. Read-only witness не recapture C₀.
6. Negative complete Missing/Ambiguous/Clipped/NonRepeatable корректно сохраняется, тратит один invalid group, не создаёт measured candidate/certificate и не включает legacy AdvanceUnassignedBurst.
7. Сохранить v1 контрпример: ранний exclusive peak и более высокий shared/unknown позже дают отказ full-horizon; owned-window diagnostic не меняет исторический v1 вердикт и не попадает в refs/accepted. Отдельные обязательные acceptance cases для **нового**, пока не реализованного method: clearly separated early vertex + небольшой tail на later peak должны приниматься; truly merged peaks остаются ambiguous. Новый метод не должен сводиться к повышению influence tolerance, скрывающему реальное слияние.
8. Actual origin/assigned time drift, plateau из нескольких samples, separated tie, boundary clipping; residual берётся из raw fullBefore и actual origin, не из difference trace или amplitude. Tolerances и anchor N−1 прежние.
9. Budget boundaries N+1/N+2 bursts, reference+retry+N0 repeat+final суммируются; frame vs channel-sample distinction; checked arithmetic overflow; group/attempt clocks отдельно; partial accounts actual queued count.
10. Need falling / cancel / sink exception / timeout на каждом k=0..N+1: raw packet не потерян/не продублирован, presentation restored, service terminal без certificate, partial не выдаётся codec1 complete.
11. Explicit learner Reset/Default/build invalidation и внутренний probe reset: group не остаётся active, C₀ не recapture, child Calculate ровно один раз на штатном tick, NativeTrainingOwned не отпускает legacy между subtrials. Bool Build/Reset/Calculate не используются как новый acceptance gate.
12. Изменение любой физики/C после последнего search success требует fresh final всех N; старые N−1 успехов, повтор одного input или чужой epoch не заменяют all-input certificate. OutsideTolerance сохраняет прежнее значение.
13. Fresh-process package5 export/import: primary hash mismatch/missing/extra, changed assignment/policy/group role/C₀/native packet → отказ; certificate2 полностью воспроизводится только для принятого method contract; input/source packet IDs не overlap. Штатный rename идентичных primary меняет artifactDocumentId, но сохраняет semantic proof ID; different-bytes tamper при старом semantic ID не проходит.
14. Stopped/partial import boundary диагностический, mid-probe resume отсутствует; self-contained import не ищет arbitrary external files. Export byte limit явный и проверен.
15. Root job writer + independent Python readers воспроизводят те же scalar/residual/proof IDs из primary; deliberate corruption расходится с claimed result. Live finalization сохраняет source Solo package5 до conversion, recognition не наследует иной метод молча.

Основные тестовые файлы root: `Tests/Integration/Libraries/Test_PulseLib_MatchedOmissionEvidence.cpp`, `Test_PulseLib_FinalVerification.cpp`, `Test_PulseLib_BoundedTraining.cpp`, `Test_PulseLib_NativeExecution.cpp`, `Test_PulseLib_NativeProbe.cpp`, `Test_PulseLib_TrainingCapacitance.cpp`, `Test_PulseLib_FinalizationBoundary.cpp`; новый scoped `Test_PulseLib_MatchedTrainingIntegration.cpp` допустим для composition вместо разрастания прежних single-probe fixtures. Python — отдельные matched Train cases рядом с `test_learned_evidence.py`, `test_matched_omission_portable.py`, stopped/pipeline/finalization tests. Утверждение физической работоспособности/разделимости требует собственных серверных опытов; structural metadata checks этого не доказывают.

До codec gate реализация этих numerical APIs не начинается; codec success сам по себе не снимает mathematical/applicability gate раздела 0. При выполнении использовать отдельные ветки с merge-коммитами, без rebase/squash/cherry-pick, и согласованный серверный build/experiment контур. Настоящий документ — review-ready постановка, не изменение ImplementationStatus и не новая сертификация результатов.
