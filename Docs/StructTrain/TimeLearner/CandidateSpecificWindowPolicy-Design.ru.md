# Окно закреплённого импульса для текущего структурного кандидата

Дата: 2026-11-08. Статус: **design для source review, без реализации и numerical acceptance**. Документ написан в отдельной ветке `codex/timelearner-candidate-window-design`. Frozen206/214/229/240, их CPP/physics/fixtures и действующие runtime/cache не меняются. Новый метод не включается в defaults или общие серии.

## 1. Решение и граница задачи

Минимальное изменение — **одно детерминированное окно на одну новую группу N+2 текущего физического кандидата**. Окно вычисляется из первоначальной измеренной вершины и явно объявленной bounded proposal policy, фиксируется до первого full trial и не меняется в full/omit/repeat. Reference windows, CapturedPerInput raw amplitudes, source/C0 family, reference N−1 и существующая scalar residual math остаются неизменными.

Рекомендуемый первый policy ID: `reference-anchored-candidate-window-v1`. Его смысл — воспроизводимое правило выбора области измерения при изменении структуры. Это не модель, утверждающая местоположение или физическое происхождение пика. Измеритель остаётся `declared-window-basin-necessity-v1`: actual fullBefore maximum, local fixed-basin necessity, actual event/frame/source/model/reset checks.

В первый блок **не входят** адаптивные поиски по набору окон, online EMA, новый planner/orchestrator, оптимизация физики, изменение targets/tolerances, замена Train глобальным максимумом либо обещание прохождения научной серии. Одно окно позволяет сохранить нынешние one-group/one-request, Arm/Consume и probe/invalid counters. Если прогноз неудачен, сохраняется честный отказ, а не подстановка предсказанного значения.

## 2. Закреплённая математическая цель

Уточнение пользователя зафиксировано в [PeakAssignmentClarification-2026-11-08.ru.md](PeakAssignmentClarification-2026-11-08.ru.md): отдельная ранняя вершина допустима при остаточном хвосте, немного усиливающем более позднюю. Неразличимая merged вершина остаётся Ambiguous. Train измеряет закреплённый импульс; Test измеряет полную реакцию и реальные spikes.

Отсюда сохраняются следующие правила:

- Полные extrema/valleys выделяются на всей trace до ограничения окном; граница окна не создаёт новый максимум.
- Выбирается высший actual fullBefore кандидат внутри declared window, который uniquely necessary именно для assigned ordinal.
- Более высокий известный UniqueNecessary другого input не блокирует assigned candidate. SharedNecessary без assigned necessity при явно Preserved assigned-control также не становится global veto. Higher Unknown, потенциально относящийся к assigned input, не скрывается меньшим удобным пиком.
- Unrelated late shared вершина вне declared window не запрещает отдельную раннюю.
- Actual amplitude/time/plateau берутся из сохранённых samples, не из full-minus-control, predictor или single-pulse trace.
- N+2 endpoints не доказывают непрерывную физическую lineage между двумя разными моделями. Миграция вершины без наблюдаемого split/merge может изменить причинную интерпретацию. Новый policy не обещает такую теорему и не добавляет требование физической декомпозиции.

Сохраняются ampAbs=1e-5, минимум=1e-6 и исходный настроенный SyncTol. Geometry window, predictor uncertainty, repeatability и timeComparisonTolerance — разные параметры. Размер одного model tick не подменяет SyncTol.

## 3. Факты исходников и evidence

| Источник | Факт | Следствие |
|---|---|---|
| Root `d433acf6ed250e7ed5da781970b3963a51c56a26`, `Tests/Integration/Libraries/Test_PulseLib_CompositeTraining.cpp:756` | `GrowthLeavesInitialDeclaredWindow` задаёт реальный N0 native L2→L3 через `ApplyNativeParameters`, а не синтетическую trace | Использовать эту физику и первичные трассы для regression следующего policy |
| Тот же файл:735, 790–791 | Classic/Branch сохраняют четыре независимые группы `initial-broad`, `initial-tight`, `after-growth-wide`, `after-growth-initial-window`; CSV всех soma, matched-witness, window declaration, source/after snapshots | Нельзя переименовать эти независимые семьи в один завершённый Train или recapture targets |
| Pulse `bd9338cf4decbbe27efaeaedf5e23be0f114a511`, `NativeCompositeTrainingAttempt.cpp:221,313` | Start и Close берут окно из `protocol.compositeMeasurement.inputWindows[input]` | Несмотря на комментарий «до группы», protocol4/contract1 фиксирует числовое окно на весь search |
| `NativeTrainingServiceComposite.cpp:18–33,132–166` | Plan windows равны protocol windows; native actor принимает один logical request и Arm вызывается на first-full preparation | Per-candidate declaration должна появиться перед `StartMeasurement`, сохраняя один Arm и Consume |
| `BoundedTraining.cpp:829–901`, `FinalVerification.cpp:413–455` | Typed admission проверяет protocol/request/revision/epoch/lease и использует общую scalar math | Требуется добавить проверку expected proposal, а не менять residual/ranking formulas |
| `NativeCompositeTrainingEvidence.cpp:57–69,198–213` | Portable replay заново строит method specification из неизменного protocol; semantic proof v1 не имеет отдельной per-group proposal | Недостаточно присвоить новое окно только actor member; declaration должна входить в prepared identity и proof/archive |
| Evidence `9400c0da0a4d2333efea36076c0e235855ca50f2` | Реальные N2 tail controls уже показывают отличие v1 influence-exclusive от пользовательской цели | Старый influence v1 остаётся diagnostic; window policy не возвращает его global veto |

**Не выдумывать результат206.** Первый Elder206 завершился 111 PASS/1 stale-fixture FAIL/94 not-run, evidence `9b9a38f1a5d8842ada5e167d9bdbf33bd24b6381`. На момент этого design нет закрытого actual6/growth receipt после исправления fixture. L3-shift и non-Valid narrow-window assertions в206 — точные source-prepared физические counterexamples, их численные значения ещё должны быть взяты из закрытых actual artifacts. Документ не объявляет их прошедшими. После A2 в design receipt следует добавить фактические first/last frame/time, identity и data SHA, не менять assertions задним числом.

## 4. Неизменная исходная семья и reference seed

Reference acquisition использует только исходные fixed windows, объявленные в cold configuration до первой reference group. Успешная полная reference group для input i сохраняет закрытый `ReferenceWindowSeed`:

```text
source_origin, target_owner_family, protocol_binding
input_id, input_index, stimulus_id, source_ordinal, physical_channel
reference_group_id, reference_semantic_proof_id
reference_base_revision, reference_effective_revision, reference_epoch
selected first_frame, last_frame, raw_potential
actual peak_time, plateau_end, assigned_event_frame/time, origin_event_frame/time
reference declared window, selected basin anchors/topology
initial actual full InputParameters, optional initial C0 parameter witness
frequency_hz, source/profile/storage bindings
```

Seed строится только из уже validated reference fullBefore и её реальных retained frames. Отдельный публичный `valid=true` или manually filled scalar не создаёт seed. Первоначальные raw targets остаются в CapturedReferences; seed добавляет provenance времени/формы, не заменяет амплитуду целью «достичь нового пика».

После полного capture все seeds неизменны. Для candidate proposals первая версия всегда использует **первоначальный** seed, не последнее удачное измерение, не лучший residual и не уже обученную текущую структуру. Это делает proposal независимым от порядка Ns/Rs/L перебора, N0 repeats и warm Reset. Нет скрытой зависимости от legacy `EstDelayPerSeg`/EMA.

Если incomplete reference capture не даёт seed некоторому input, search этого input и final не стартуют. Сохраняются исходные incomplete-capture/reset ограничения; новый policy не обходит их.

## 5. Точный первый policy: целочисленные frame proposals

Рекомендуется явно объявлять candidate window **в индексах сохранённой native grid**, относительно начала fullBefore. Это устраняет ложный one-frame drift из `double(frame.time - absolute_begin)` и позволяет независимо воспроизвести арифметику C++/Python без различий `log`, FMA и округления JSON.

Это не допуск сдвига waveforms. Общий N+2 validator по-прежнему требует одинаковые frame count/order, retained event frame/ordinal, source shape и timeComparisonTolerance<0.5/f. На всех traces используются одинаковые объявленные индексы; интерполяции и добавления samples нет.

Поля policy (все counts finite integral JSON numbers/nonbool, exact range ≤2^53−1; signed intermediate arithmetic проверяется до сложения):

```text
schema_version=1
policy_id="reference-anchored-candidate-window-v1"
seed_rule="immutable_reference_full_before"
coordinate_mode="relative_native_frame_interval"
proposals_per_logical_request=1
per_input[i]:
  delay_frames_per_segment                // явный bounded prior; 0 допустим
  base_left_guard_frames, base_right_guard_frames
  length_guard_frames, synapse_count_guard_frames
  resistance_change_guard_frames, capacitance_change_guard_frames
  hard_first_frame, hard_last_frame
  maximum_window_frames
maximum_feature_terms                     // предотвращает unbounded dimension work
```

Здесь `delay_frames_per_segment` — коэффициент предложения, а не measured delay. Uncertainty guards не входят в train tolerances. Все поля хешируются как алгоритмический policy, входят в scientific condition и не объявляются diagnostic-only.

Для полного actual current parameter vector P и исходного readback P0:

```text
nL = sum_j abs(P[j].L - P0[j].L)
nNs = sum_j abs(P[j].Ns - P0[j].Ns)
nRs = count_j(P[j].Rs != P0[j].Rs)           // exact binary64 equality; no logarithm
nC = 0/1: current C correction differs from initial correction
      using existing EquivalentTrainingCapacitance semantics (new unit paths allowed)

shift = (P[i].L - P0[i].L) * delay_frames_per_segment[i]
uncertainty = length_guard_frames[i]*nL
            + synapse_count_guard_frames[i]*nNs
            + resistance_change_guard_frames[i]*nRs
            + capacitance_change_guard_frames[i]*nC
first = seed[i].first_frame + shift - base_left_guard_frames[i] - uncertainty
last  = seed[i].last_frame  + shift + base_right_guard_frames[i] + uncertainty
```

Все умножения/суммы проверяются на overflow и declared budgets. Full vector используется намеренно: Branch edit одного input может влиять на остальные responses. Classic тоже не получает недоказанного предположения независимости feedback. Rs/Ns/C здесь увеличивают заявленную неопределённость; отсутствие отдельной predictive модели для них не означает неподдерживаемую физику.

`Ctrim Off` с отсутствующим C0 даёт nC=0 и не требует C property. Если C0 существует при Off, прежняя actual origin/correction проверка сохраняется. Unsupported C physics отклоняется только при запросе неподдерживаемого C edit по прежним native capability правилам.

Proposal доступен только если first≥hard_first, last≤hard_last, first<last, width≤maximum_window_frames и last<declared maximumSamples. Нельзя молча обрезать интервал hard bounds, подогнать его по waveform или изменить selected input. Недостаточная длительность/число фактически retained frames возвращает `window_frames_not_captured`, без padding/one-tick сдвига.

После строгого native closure actual временные границы для pure geometry берутся **только** как `fullBefore.samples[first].time` и `fullBefore.samples[last].time`. Эти frames объявлены заранее; использование их реальных timestamps не является post-hoc выбором удобной области. Raw selected peak timestamp сохраняется без пересчёта. Потребуется явный frame-window specification2; diagnostic seconds-window specification1 не переосмысляется.

Policy не гарантирует истинную границу физического latency. Неудачный prior может привести к Missing/constraint stop. Даже guard, успешно покрывший L2→L3, не является доказательством покрытия L8, всех Rs или C. После capture следует проверить worst-case arithmetic/window feasibility на объявленных search bounds; это проверка конфигурации, не доказательство существования измеримого пика.

## 6. Recipe, instance и фактические feature bindings

Разделяются два ID:

- `window_recipe_id` хеширует policy+immutable seed proof+actual parameter feature witness+base candidate revision/epoch+input/channel+полученный frame interval. N0 repeats той же geometry имеют тот же recipe.
- `window_proposal_id` дополнительно хеширует current_attempt_id, run/trial/group/purpose, final sweep ID и live generation binding. Каждый новый measurement имеет отдельный ID; replay старого proof не разрешён.

Первый ID не разрешает reuse measurement. Второй не является portable live authority. CSV paths отсутствуют в обоих semantic IDs; artifact document hash сохраняет paths.

**Не считать нынешний neuron-only hash полным ordinal mapping owner.** Для вычисления policy недостаточно произвольного JSON `actual_parameters`. Новый candidate feature witness должен сохранить actual readback и logical→physical input map: input ID/index, attachment L, Exc bank paths/Ns/Rs, channel path, base model identity и optional C0. Native owner читает и проверяет его до queue; сравнивает mapping на preparation/closure/consume. Дешёвая проверка актуальности ordinal map может работать вместе с существующим typed revision observer; новых model writes/repair нет.

Portable validator проверяет features по retained model parameters/links, supported native builder topology и declared mapping. Для Branch нужен также actual fullBefore effective identity/selector overlay: его SHA должен равняться prepared effective revision, physical selected banks должны соответствовать assigned map row; остальные изменения base→effective запрещены. Равенство base/effective hash при no-op routing допустимо. Если нынешний primary этого не содержит, record1 не «повышается» догадкой — record2 сохраняет недостающий boundary readback. Сам факт native execution по импортированному JSON не утверждается.

Reuse `ReadNativeInputParameters`, `InspectNativeLearnerModel` и существующие graph/metadata checks. Новый слой не должен второй раз независимо реализовывать physics либо вычислять C/R/L из parent defaults.

## 7. Request и FSM: минимальное изменение

```text
Capture:
  use immutable reference window
  execute one complete native N+2
  validate common context + existing basin method
  retain raw target and closed reference seed

Queue Search/Final request:
  require actual Need, owner lifetime, source/C0/storage/current revision/epoch
  read verified actual candidate parameter/map witness
  proposal = Propose(policy, immutable seed, actual witness, exact request)
  if arithmetic/envelope unavailable:
      stop SearchUnresolved with explicit window_policy_constraint
      retain declaration/reason; do not invent group/raw work
  freeze proposal and reserve existing group/raw/sample/model/wall/primary budgets
  StartMeasurement(request, frozen proposal)
  first full preparation: one typed Arm, proposal identity immutable
  omit/repeat: raw callbacks only, no second Arm

Close:
  common N+2 context/native/restore/repeat replay unchanged
  verify actual retained frame interval exists and proposal is unchanged
  select via same basin criterion on full waveform
  verify selected peak >= ACTUAL assigned onset/frame
  arrival = actual_peak_time - ACTUAL origin_event_time of THIS fullBefore
  mint one private validated measurement with recipe/proposal/proof binding
  one core Consume; same scalar residual/ranking/final math
```

Первый policy не добавляет retry-orchestrator. После Missing/Unknown нельзя по этой же trace подобрать другое окно. Существующий retry_same_candidate, если разрешён budget, получает новый logical trial/group, но **то же числовое deterministic recipe** при неизменных P/policy/seed. Каждый повтор полностью свежий N+2, все counters/invalid charges прежние. Изменение recipe возможно только вследствие нового actual physical candidate либо нового explicit policy family.

Adaptive widening/несколько заранее заданных окон — возможный следующий policy с отдельным accounting. Он не требуется для первого исправления fixed-window, не добавляется скрыто, и не может выдавать best residual среди удобных окон как один observation.

## 8. Missing, merge, order, plateau и clipping

| Ситуация | Обязательный результат |
|---|---|
| Предсказанный центр есть, actual full maximum отсутствует | Missing/non-promotable; не materialize predicted value |
| Higher possibly-assigned Unknown, local merge, split, crossing basin boundary | Ambiguous/Unknown; не выбрать меньшую вершину и не сместить окно после просмотра |
| Plateau пересекает объявленную границу либо basin касается record edge | Сохраняется existing Clipped/Unknown; нет «срезанного максимума» |
| Нет достаточных captured frames для declared interval | Incomplete/window_frames_not_captured, ни scalar, ни certificate |
| Full repeat topology/values не воспроизводятся | Existing NonRepeatable; predictor uncertainty не ослабляет repeatability |
| Известный более высокий other-input maximum | Не global veto; assigned necessity определяет admissibility |
| Поздний unrelated shared максимум вне окна | Не veto раннего допустимого peak |
| Одна merged вершина сохраняется в обоих single-source omissions | Нет uniquely necessary input: Ambiguous |
| Источник/ordinal/window/model/epoch изменён между full и omit/repeat | Context rejection, все group data остаются primary, consumption запрещён |

Source ordinal/actual event order неизменны: retained omitted controls используют тот же исходный pulse index и actual frame, не перенумеровывают его по близости к predictor. Assigned peak не может предшествовать actual assigned event.

Не вводить дополнительный запрет `peak < next_stimulus_onset`: длинный кабель может дать законный поздний ответ. Не требовать глобального temporal order максимумов между разными Classic soma или разными Branch solo groups. Где observed split/merge делает локальное назначение неоднозначным, результат остаётся ambiguous. Смена относительного порядка предсказанных окон сама по себе не доказывает physical crossing. Continuous physical vertex identity между разными L/Rs не заявляется.

## 9. Инвалидация, repeat и fresh final

- Source/reference windows и seeds привязаны к исходным reference proofs, source origin и initial model/epoch. Candidate window не является retarget и не меняет raw target.
- Любой actual L/Ns/Rs/C edit отменяет inflight proposal/live lease и старые accepted current-model measurements. Для Branch инвалидируются все inputs/anchor/finals по прежним правилам.
- Новый proposal вычисляется только после verified native edit/readback. Atomic rollback получает actual returned graph/epoch; старый proof не возвращается по совпадению semantic hash.
- N0 repeats одной geometry используют один recipe; не уточняют его по первым repeats. Уникальные group/trial IDs и actual clocks сохраняются.
- Перед final фиксируется recipe set всех N inputs для одной actual candidate revision/epoch. Каждый input получает свежую N+2; reference N−1 повторно измеряется на текущем графе. Same current_attempt + same final run/sweep + latest observed run guards сохраняются. Смешивание sweep/epochs/policies/proposals запрещено.
- Certificate связывает method, window policy hash, seeds/reference proofs и final proposal IDs; математика amplitude/timing residual остаётся прежней. Более широкое окно не увеличивает SyncTol.
- Warm Reset сохраняет initial seeds/family/C0, но истекает live generation. Импорт не восстанавливает callbacks; новый actual owner Start проверяет current physical model/source/map и создаёт новую lease. Seeds не пересчитываются из обученной структуры.
- Default/Pool/retarget удаляют family. Изменение policy/reference windows требует explicit новой семьи с исходным baseline и свежими reference observations; нельзя тихо пересоздать targets на текущем trained graph.
- PostTune/conversion/calibration не наследуют новый Exact для recognition; Test и inference verification остаются отдельными.

## 10. Rdk/storage/lifecycle

Policy — чистая арифметика над закрытым readback. Она не вызывает Calculate/Build/Reset/Default, не задаёт child properties и не использует их возвращаемые bool как отказ. Единственный scheduler/NativeProbeControl и штатный порядок CalculateMode0/1 остаются прежними.

Предложения используют actual native model после штатного editor; uniform physics остаётся в storage images. `CreateClassSamples`/prototype registration не получают нового overlay. Если меняются images/source/C0 origin, existing family guards отклоняют это; не чинить граф перед каждым tick.

Build/Init/reconstruction используют штатные роли Rdk: owner lifetime/graph-instance observation инвалидирует старый inflight proof. Сохранение immutable target после допустимого native Reset не означает сохранение живой lease. После pool return/take прежняя family не переносится по адресу объекта.

## 11. Совместимость и предлагаемые версии

Нельзя переименовать protocol4 inputWindows в «только initial windows», а cold6/package5 выдавать с другим смыслом. Для source review предлагаются новые точные ветви:

| Документ/тип | Frozen | Следующая opt-in ветвь |
|---|---|---|
| Cold configuration | 6, composite policy1 | 7, flat base1..4 + composite policy2/window proposal policy; top windows явно reference-only |
| VerificationProtocol / CompositeMeasurementContract | 4 / 1 | 5 / 2: reference windows + complete policy; старые codecs строго отвергают новые поля |
| Native declared basin method specification | 1 seconds offsets | 2 tagged reference-time/candidate-frame coordinate; geometry method ID сохраняется |
| Composite candidate binding | v1 | v2 actual parameters/ordinal map/effective-selector readback |
| Measurement record / archive | 1 / 1 | 2 / 2 с полным window proposal, recipe/instance IDs, feature witnesses |
| Learned package / summary | 5 / 6 | 6 / 7 с новым строго decoded archive; actual model import unchanged |
| Training certificate | 2 | 3 с window policy + proposal bindings; numerical residual math unchanged |
| Console execution | 3 over base1/2 | 4 over base1/2 с точной новой archive/version closure |
| Native raw ProbeRecorder / native packet / matched portable | 1–6 / 2 / 1 | **Без изменений** |

Это резервирование design, не уже реализованные schemas. Перед implementation перепроверить latest source и заморозить exact keys с C++/Python владельцами. Минимальный selector/common context не переписывается. Общий composite dispatch должен распознавать только конкретные protocol4/5, а не произвольное `schema>=4`, пересекающееся с другими diagnostic типами.

Source binding2 остаётся immutable physical initial source; его не нужно менять ради policy. Target/method binding различает policy через reference protocol/family. Condition hashing сохраняет новую policy целиком; исключать можно только ранее явно diagnostic context radius/influence fields после полной validation. Смена CSV путей меняет artifact hashes, не semantic recipe/measurement/certificate IDs.

## 12. Конкретные файлы и минимальные этапы реализации после review

1. **Pure proposal + tests.** `Core/TimeLearner/CandidateWindowPolicy.h/.cpp` и `Tests/Integration/Libraries/Test_PulseLib_CandidateWindowPolicy.cpp`. Закрытый reference seed/factory, checked integer arithmetic, один deterministic frame interval. Никакой зависимости от Rdk или physics equations. Fast target компилирует production .cpp, не test body copy.
2. **Typed identity/native bridge.** `CompositeTrainingMeasurement.{h,cpp}`, `NativeCompositeTrainingAttempt.{h,cpp}`, `NativeDeclaredWindowBasinAssignment.{h,cpp}`: explicit expected proposal, feature/map witness, frame-coordinate projection только через actual retained timestamps. Общий `MatchedOmissionValidation` переиспользуется без whitelist/дублирования.
3. **Service/core admission.** `NativeTrainingService{,Composite}.{h,cpp}`, `NativeTrainingBindings.h`, `BoundedTraining.cpp`, `FinalVerification.{h,cpp}`: source seeds после capture; proposal перед Queue; один Arm/Consume; exact proposal equality; actual current graph/C0 checks; fresh final proposal set. Общая scalar math/order/targets/tolerances не меняется. Native lifecycle files меняются только если требуется добавить проверку feature-map актуальности.
4. **Strict portability.** `CompositeTrainingDeclarations`, `ProbeEvidenceJson`, `NativeCompositeTrainingRecord`, `NativeCompositeTrainingEvidence`, `CompositePortableTrainingProof`, `NativeCompositeLearnedState`, `ConfiguredNativeTraining`: новые dispatch branches/IDs, полный replay recipe из primary/reference/current-model feature witnesses. Old fixed-window byte/decision regression — отдельный gate.
5. **Root adapters/CLI.** `App/NeuroModelerConsole/TimeLearner{CompositeArtifacts,TrainingJob,ProbeEvidenceWriter}`, `Scripts/StructTrain/TimeLearner/composite_*` readers/managed pipeline/condition projection и maintained tests: actual complete group/spec/policy/source transport, никаких inferred proposal defaults. Обновить versioned docs/entry points и gate inventories, hash source только по binary Git blob.

Source preparation изолированного pure STEP1 разрешена после source review design и не должна ждать всех240. Она не разрешает обновить active source/cache. Native integration/runtime admission отдельно требует соответствующих принятых prerequisites206/механический97/214/229/240. Каждый последующий шаг — отдельная ветка/commit, после review и server acceptance merge --no-ff по принятому плану.

## 13. Адресные acceptance controls

**Pure proposal:** immutable reference seed + actual P0/P; L2→L3 меняет окно до измерения; Ns/Rs/C changes учитывают guards, CtrimOff без C работает; same candidate/order/repeat/warm даёт одинаковый recipe; разные purpose/trial/epoch дают разные instance IDs; negative/overflow/count-bool/nonfinite/budget/hard-envelope failures; frame bounds после rollover; никакого доступа к measurement amplitude/residual в API proposal.

**Pure/bridge geometry:** moving assigned peak был вне reference window, попадает в заранее declared candidate interval; выбран actual highest assigned full peak; поздний higher shared вне окна не veto; higher known-other не veto; higher potentially-assigned Unknown внутри окна не скрывается; merged/ties/plateau/basin boundary/record clipping/subfloor/split/nonrepeatability остаются отрицательными. Попытка изменить first/last после fullBefore или вычислить их по его peak должна быть rejected binding.

**Native growth:** переиспользовать физику и after-state source206 Classic/Branch L2→L3 controls. После закрытия206 взять фактические traces как отдельное историческое обоснование proposal parameters, затем **зафиксировать** policy до новых independent groups. Не выбирать коэффициент из того же будущего measurement. В новой реальной Train-семье исходные references/targets остаются прежними; L3 group меняет только candidate window, final всё ещё использует fresh actual allN. Сохранить old narrow negative, new predeclared-window result, all full/omit/repeat CSV, actual input, source/after snapshots, raw target and residuals. Не требовать Exact, если физика не достигает исходных tolerances; требуется честная measured/negative классификация без false success.

**N4/N6:** отдельные Branch positive-routing fixtures с distinct attachments `[N,N−1,...,1]`, actual selected banks для каждого input и full source ordinal/frame checks. Текущий `[2,2,...,1]` source206 dimension fixture содержит shared banks и остаётся самостоятельным negative/plumbing control; protocol counts сами не доказывают правильную физическую маршрутизацию. Classic N4/N6 проверяет реальные channel paths. ≥4 cases не должны искусственно ослаблять amplitude/sync tolerances или обещать Exact.

**Live/portable adversarial:** wrong seed/input/pulse/map/revision/epoch/attempt/final-sweep; same hash после rollback, stale prepared after Reset/Default/pool; Need=false setter/direct/connected между close и consume; tampered frame interval/feature witness/policy hash/primary; insufficient samples/partial/stop; full declared-source profile/actual ISI/frequency mismatch; all old schemas reject new fields. C++ and independent Python replay сравнивают actual recipe/selection/target/final residual/cert fields и rename-invariant semantic IDs.

**Clock:** fullBefore groups с разными ABS begin, actual source quantization и frame clocks; proposal frame interval остаётся заранее тем же, actual arrival всегда относительно origin события текущей группы. Не применять guessed cumulative ISI как actual timestamp и не расширять tolerances на один tick.

**Runtime evidence:** compiler+normal+ASan scoped gates, exact case inventory из actual gtest list, source Git blob SHAs, active loaded runtime provenance, retained primary + independent replay + temporal renderer. Нельзя считать source-written cases или job JSON результатом numerical запуска.

## 14. Что именно будет закрыто и что останется

После review/implementation/gates будет устранена механическая зависимость всех search/final measurements от неизменного initial numeric window: текущая actual geometry получит новое заранее declared окно, не меняя targets. Появится воспроизводимая per-candidate policy и portable proof её исполнения.

Это не доказательство полного покрытия всякой физики и непрерывной vertex lineage. Bounded hard horizon, плохо выбранный prior, multiple-peak semantics и невозможная синхронизация могут оставить Missing/Ambiguous/SearchUnresolved. Их надо показывать как ограничения/результаты, не как ошибки анализа и не как обещанный PASS. Single-input N=1 multi-peak contract остаётся отдельно tracked; N1 normalization (TipResistance) при multi-input поддерживается и не смешивается с количеством inputs.

Исходные августовские визуальные4/8–6/8 относятся к первоначальному protocol без permutation/увеличенного gap и сохраняют свой доказательный scope. Новая политика и её adversarial tests не отменяют их задним числом.
