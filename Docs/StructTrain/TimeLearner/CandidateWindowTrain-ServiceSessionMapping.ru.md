# STEP3-B: точная карта Service/Session для Train5

Статус: source preparation / reviewable mapping. Это не реализация service5, не runtime acceptance и не разрешение CLI/default dispatch. Исследованы immutable Pulse `376bee62adadb3306afec72634665aab0a612b01` и Root `6579c58386a0b77dd79926c5ff3b1bb93b84a884`; ветки подготовки — `codex/timelearner-candidate-window-service`. Frozen STEP2/core/remote source не изменяются. Исходное предложение — `CandidateWindowTrain-Step3SourceProposal.ru.md`; реализованный отдельный core — `CandidateWindowTrain-A-Core.ru.md`.

## 1. Существующий путь и точечные разрывы

Отдельного общего Session framework здесь нет. Session — `NativeTrainingService::attempt`/`SessionAttempt()`, `plan.search.runId`, owner request intent и текущая native authority. Добавлять новый orchestrator не требуется.

| Файл/метод в Pulse376 | Факт | Минимальная следующая правка |
|---|---|---|
| `NativeTrainingService.cpp:37 Start`, `206 BeforeTick`, `278 AfterTick`, `331 CheckBudget`, `358 ExternalStop` | Dispatch только protocol4;5 уходит в scalar3 validation/cancellation | Явная ветвь5 с contract2/policy2; scalar3 и fixed4 сохраняют свои ветви. Не заменять на `>=4` |
| `NativeTrainingServiceComposite.cpp:18 Validate` | Требует4/contract1/policy1, сравнивает fixed `inputWindows` | Отдельный validator5: protocol5/contract2/policy2, reference windows и полная authoritative policy из protocol; общие source/limits checks сохраняются |
| `StartComposite:61–120` | Actor создаётся до `++attempt` и добавления `/session/N` | Для5 вычислить checked next attempt/run ДО constructor, не публиковать их до успешного prepare. Этот ID передать в `NativeCandidateWindowAttemptDeclaration` |
| `NativeTrainingBindings.h:47 createComposite` | Только старый cold4 и imported fixed4 proof factories | Отдельные typed factory callbacks для cold5 и `DecodedNativeCompositeArchive`2 adoption; никаких public eligibility bool/portable callbacks |
| `StartComposite:79–91` | Warm4 оставляет только reference records; actor5 отдельно хранит `windowRecords/windowPrimaryBytes` | Для5 согласовать один retained ledger с actor до restart. Нельзя оставить service bytes только refs при сохранённых actor bytes всей истории |
| `CompositeBeginSearch:122` | Вызывает старый Bounded constructor, который намеренно отказывает5 | Только после complete allN release вызвать overload с `CandidateWindowReferenceSet` из фактического actor |
| `QueueComposite:129` | Один group/pending, но ArmComposite4 callback | Сохранить один logical request на N+2;5 вызывает только `ArmCandidateWindow`, raw callbacks остаются evidence-only |
| `ClosedComposite:264–347` | Ставит Need-at-consume до ветвления и каждый reference `consumed=true` | Для5 staged refs остаются `!consumed`/null до единого allN release; отдельные typed Consume/Reject5, fresh final IDs по реальному accepted delta |
| `ArchiveComposite:247` | Переписывает record `attemptId` и `policy` из текущего service plan | Для5 не переписывать значения actor, уже включённые в proof2. Проверять соответствие service declaration и сохранять actual clipped group caps |
| `NativeLearnerLifecycle.h:17 InterruptComposite` | Явно только4 | Расширить только явными4/5 ownership ветвями; Reset/Default/Pool/retarget не должны терять cancelled raw packet |
| Classic `NNeuronTimeLearner.cpp:3385`, Branch `...Branch.cpp:4139` | Build interruption/reset guard явно4 | Включить5 в ту же штатную owner interruption границу. Build/Calculate/Reset по-прежнему возвращают true, результат не используется как admission |
| `ResetControl:373`, `InvalidateTarget:385` | Reset отзывает live lease и сохраняет цель; invalidation очищает семью | Добавить новый retained closed reference state и imported archive state к тем же правилам; не recapture trained graph |
| `ConfiguredNativeTraining.cpp:360 CaptureCompositeInitialConfiguration` | Принимает только4 и encoder выдаёт cold6 | Для5 нужен настоящий immutable cold7 declaration либо явная временная непереносимая service boundary. Нельзя выдавать cold6/пустой source за новый portable package |

`ProbeSpec.schemaVersion` — другое пространство версий: N+2 использует raw6, prototype сервиса остаётся3. Нельзя глобально заменять проверки native ProbeSpec4/5 на проверки VerificationProtocol5.

## 2. Минимальное состояние и ownership

Повторно использовать `composite`, `compositeRecords`, `compositeRequest`, raw notification queue, generation guards, C0 maps, `referenceBinding`, `retainedEpoch` и существующие states Idle/CapturingReferences/Searching/Finished. Для5 нужны только retained complete closed reference set и закрытый imported archive2/proof3 boundary. Search/final не получают staged seeds.

Различать четыре значения:

- Original source family: immutable source/P0/C0/storage/profile/reference windows и ordered reference group/proof/raw targets. Не меняется при обычном Reset или controlled edit.
- Semantic attempt ID: заранее вычисленный полный `baseRun/session/N`, новый на warm restart. Стабилен при owned edits, равен namespace record/proposal/logical request; не выводится из адреса actor.
- Live generation/lease: свежий после Reset/adoption; может меняться после controlled edit. Не используется для группировки portable attempt counters.
- Current graph revision/epoch: изменяется после реального редакта. Initial source revision/epoch не заменяется текущим значением.

Cold5 constructor должен работать пока реальный service ещё Idle. Все fallible проверки/создание authority/immutable declarations завершаются до публикации нового состояния. Callback authority из существующего owner adapter проверяет actual Need, lifecycle и physical model; адреса не экспортируются. При отказе Start не публикуются пустые family/archive/certificate.

## 3. Транзакция complete allN references

`consumed` для reference5 означает **включён в завершённый allN reference set**. Сам факт измерения хорошего input0 не делает prefix consumed. `training_requested_at_consume` до release остаётся null; живой Need при промежуточном close проверяется локально, а не записывается как несуществовавшее complete consumption.

```text
close reference group -> archive actual packet/CSV/proposal absence first
require current owner/Need/model/source/C0 + actual clocks/budgets
if missing/ambiguous/partial: keep diagnostic !consumed; bounded reject/stop
stage native validated measurement and its group under original capture binding
if fewer than N: publish no CapturedReferences/closed RefSet/search
if all N:
    prepare CapturedReferences from ALL actual live reference values
    prepare closed native reference set with original P0/C0/plateau indices
    preallocate service reference groups/records/target storage
    recheck current boundary/Need/deadlines
    commit actor complete set + service complete set + ALL selected flags together
    only then construct/publish search5 or stop at a valid complete-reference boundary
```

В Pulse376 `CompleteCandidateWindowReferences` уже выполняет fallible closed-set copy до actor flags. Этого недостаточно для нового cross-owner service commit, если после actor release service ещё делает allocating copy. Следующий source chunk должен использовать private prepare/commit split: закрытый набор полностью подготовлен до публикации, commit выполняет только noexcept pointer/move/swap и bool assignments. Возможная минимальная реализация — factory-owned `shared_ptr<const CandidateWindowReferenceSet>` внутри actor/service, без нового public token/valid flag; до commit он виден только private подготовке. Проверить noexcept свойства реально используемых moves. Альтернативный shape допустим, но partial archive не должен получить consumed prefix при allocation/validation exception.

Raw sinks и `beforeCompositeConsume` выполняются с существующей stable snapshot/lifecycle/generation логикой. Между commit и публикацией search нет внешних callbacks. Если создание search после complete commit отказывает, сохраняется честная complete-reference stopped boundary, а не fabricated partial или Exact.

## 4. Один N+2 request и старые численные consumers

`QueueComposite` сохраняет serial/action, purpose, run/trial/input, base revision/epoch. Actor5 выводит candidate binding и proposal ДО первой queue, фиксирует frameSpec2 на все full/omit/repeat. Native prepared callback вызывает ровно один ArmCandidateWindow; ни один raw `onPrepared`/`onNativeResult` не Arm/Consume в controller.

`ClosedComposite` повторно проверяет Need/lease/current graph/source/C0/frozen proposal, затем вызывает единственный ConsumeCandidateWindow либо RejectCandidateWindow. Успех определяется accepted observation delta, не наличием diagnostic measurement и не возвращаемыми Rdk bool. Partial/no measurement хранится со всеми реально полученными raw packets, без synthetic scalar3.

N0 integer Ns/repeats, N1 effective domains/logRs, ranking, length cursor, CapturedPerInput raw targets, reference N−1 и residual equations остаются core376. Domain/preview/edit actions разрешены только вне активной N+2 группы. Branch edit по-прежнему invalidates все final inputs; после actual edit `RefreshOwnedAfterEdit` выполняется до следующего frozen proposal. `declined` edit с unchanged graph не повышает epoch; partial/failed edit не принимается по шаблонному readback.

Default amplitude abs1e−5/minimum1e−6/sync.02 не меняются. Engineering .2 controls остаются отдельными. Candidate policy использует initial reference indices и actual control knobs; waveform/residual/predicted delay не становятся selected maximum. N=1 single-impulse остаётся legacy scalar3; contract5 N≥2, single-input multi-peak открыт явно.

## 5. Warm/reset/import: одна retained ledger

Complete own warm и package import не должны вызывать cold constructor5 на trained graph. Предпочтительный reuse для complete boundary — strict archive2 encoder/decoder + существующий `NativeCompositeTrainingAttempt(owner, decodedArchive, limits, newDeclaration, ...)`: factory самостоятельно replay original references/proposals/source, проверяет actual current owner/model/storage/C0 и создаёт новый lease. Это boundary work, не новый controller framework; portable validation не утверждает факт native execution.

Если собственный warm оптимизируется private `RestartCandidateWindowOwned`, он обязан сделать эквивалентные checks и явно обновить semantic declaration; простой `RestartOwned` из376 недостаточен. В нём сейчас меняется live generation, но остаётся старый `windowDeclaration.attemptId`.

Для первой5 реализации разумно сохранять ВСЮ retained history (включая невыбранные old finals/failed groups) одновременно в actor и service. Это убирает расхождение current service4 prune и actor5 ledger. Current cap платит все retained primary bytes; historical caps/prefix checks из feb3 не переписываются. Current group/native/sample counters начинаются с нуля; retained historical raw groups не считаются новыми пробами. Если позднее требуется pruning, это отдельная явно объявленная retained-ledger операция с согласованными records/bytes/references и lower-bound scope; не молчаливое ослабление accounting.

Incomplete capture Reset: expired staged native tokens не переносятся как live reference authority. Сохраняются original source/capture constraint и diagnostic raw history; новые attempts заново измеряют ВСЕ N на той же original revision/epoch либо требуют явный cold retarget. Нельзя соединить старый input0 с новым input1 по одному совпадению model hash. Для такого пути нужен private restart, сохраняющий source family и очищающий только staged weak measurements/seeds; public archive reference factory требует complete allN и не используется как partial proof.

Default/Pool/retarget очищают complete refs, adopted proof, original initial configuration и actor. Explicit Build/Uninit/rebuild отзывают inflight authority на штатной lifecycle границе. Обычный физический per-probe neuron.Reset не уничтожает семью. Invisible same-node direct-value ABA вне controlled path не объявляется покрытым; fresh boundary readback обязателен.

## 6. C0, notifications и бюджеты

C-trim Off работает без искусственного C0 и без нового общего требования C-property. При существующем bound C0 сохраняются original origin/baseline и actual current scales. Before-native witness относится к unmuted BASE candidate revision; prepared Branch effective routing может отличаться. После каждого raw trial используется прежняя C0 readback проверка; после lifecycle cancellation недоступный readback остаётся diagnostic unknown, не фиктивное подтверждение.

Сохраняется весь callback248 путь: exact raw run/trial/probe generation, capture-only cancellation, stable local callable и snapshot, mutable sink state, checks generation/attempt/lifecycle после callbacks, raw delivery ровно один раз. Callback после Reset/Default/retarget не завершает старый service. `SyncOutcome`/service certificate не публикуются до успешной доставки completed sink и свежей проверки времени. `search->Certificate()` после локального core finish не равен уже опубликованному service Exact.

Отдельные ledgers: controller logical probes; actor issued N+2 groups; реально issued/completed native probes; actual sampled/retained frames; materialized primary bytes; current attempt model/wall; per-group actual clipped model/wall caps. Reserving upper-bound bytes до queue сохраняется. Partial/ambiguous/stop/cancelled groups расходуют реальные budgets. Existing `CompositePrimaryByteReservation` и prefix/history проверки feb3 переиспользуются.

Actor Record5 уже содержит proof-bound attempt limits, primary cap и фактические clipped group limits. Service archive должен их проверять против объявления (<= declared group cap/remaining time), а не заменять исходным unclipped policy. Дополнение raw C0 witness IDs не изменяет scientific identity, но требует exact base revision и actual witness replay. No fake elapsed/wall attestation при offline import.

## 7. Service archive/cert boundary и зависимость от cold7

Service5 exporter нужен отдельной явной ветвью, сохраняющей record2/archive2 и настоящие accepted/final selections. Actor STEP2 exporter намеренно оставляет finals пустыми; его нельзя переименовать completed package6. Выбранные final group IDs — все N, current attempt, один последний OBSERVED final sweep, current model/epoch и правильный Classic/Branch order. Новый partial sweep отменяет selection старого полного sweep; отсутствие actual record не доказывает ещё не выполненное live намерение.

Portable cert3 factory должна отдельно replay strict closed archive2, complete RefSet и все actual final peaks через ту же residual math. Не вызывать старый `CompositePortableTrainingProof::Replay` с подменой5→4 и не восстанавливать `Prepared` callbacks. Typed live API и portable data proof остаются разными authority границами.

Код service Start уже сохраняет immutable initial configuration. Поэтому S3-B нельзя автоматически совместить с old `CaptureCompositeInitialConfiguration`4: либо вместе добавить только необходимый **неактивированный** cold7/protocol5/policy2 initial encoder/decoder, либо оставить новый service boundary явно непереносимым до S3-C. Предпочтительно первое, чтобы actual direct-service fixtures сразу сохраняли проверяемую исходную декларацию. Это не включает CLI factory/default. Далее S3-C — learned6/summary7/runtime2/execution4, actual-model import/export; прежние1–6 cold, package1–5, cert1/2 meanings сохраняются.

`NativeLearnedState.cpp`/`ProbeEvidenceJson.cpp`376 guards `requires_package6`/`requires_summary7` остаются, пока соответствующие новые serializers/replay реально не готовы. Нельзя временно экспортировать package5 или scalar packet для запуска тестов. Recognition/calibration/conversion не получают OriginalExact автоматически.

## 8. Адресные production controls для следующего implementation chunk

Это **план**, не существующий compiled inventory и не обещанный count. Точные literal IDs и hashes создаются после реализации; tests вызывают production Service/owner/storage/scheduler и сохраняют реальные raw CSV/модели.

| Fixture family | Конкретные проверки |
|---|---|
| Cold5 service | Classic/Branch × CalculateMode0/1, direct Start; original allN release; one Arm/Consume per N+2; N0 actual repeats; .2 engineering Exact и отдельный .02 non-Exact |
| Partial release | Stop/Need=false/throw после первого valid reference и перед последним release: no complete refs/search/cert, все prefix !consumed/null; failed last group сохраняет actual raw; completion marks только N selected refs, не старые retry diagnostics |
| AllN commit | Validation/copy failure до private commit не публикует partial consumed; failure создания search после commit сохраняет COMPLETE stopped target без certificate; callback не может увидеть промежуточную половину family |
| Warm complete | Реально изменённый trained graph, Reset/new attempt сохраняет original P0/C0/raw/proofs/plateau indices, fresh lease/current counters; old prepared не Consume; сначала только retained bytes, затем новые фактические N+2 |
| Warm partial | После input0 Reset: старый lease unusable, fresh allN capture на original graph; changed original graph требует retarget; отсутствие full refs не допускает перенос stale staged input0 |
| Import complete | Actual archive2 → actual physical owner import → fresh adoption5; fake initial-template current graph/wrong storage/source/C0 rejected; no callbacks restored |
| Growth/N0 | Actual L/Ns edit с assigned peak за initial narrow reference window; frozen candidate-frame proposal до queue, actual frame timestamp после closure, свежий final всех N; отсутствие пика/merged/edge remains non-Exact, no convenient post-hoc window |
| N1 physical path | Actual effective-domain action вне группы, real Rs edit/readback, fresh proposal, original baseline; standalone core fixed N1 pass не заменяет это |
| Bound C0 / Off | Off with no C0; existing origin preserved after warm; actual owned C edit invalidates all final values; wrong base/effective witness binding rejected |
| Cancellation/sinks | 42 callback controls baseline не удаляются; representative5 setter/direct/connected Need, Reset/Default/retarget from raw/before-consume/completed sinks, throw/mutable callable/slow callback, exact cancelled raw once, no stale Exact |
| Budget ledgers | One group budget reservation, partially issued raw sample counts, primary prefix cap on warm, actual callback/replay wall time; cached revision/delayed consume cannot bypass deadline |
| Final freshness | Same graph two sweeps; partial newer sweep; wrong run/attempt/proposal/source/epoch; Branch edit clears all inputs; pattern-relative arrival uses actual origin despite different ABS starts |
| Actual dimensions | N4/N6 Branch distinct declared attachments `[N..1]`, expected banks из fixture model declaration, actual ordinal/receiver/IsConnected witnesses. Отдельно legitimate shared-bank negative; dimension routing alone не утверждает valid allN targets/Exact |
| Legacy A/B | Same scalar97, fixed4 service/config/package/Console + full callback248 literal IDs, prior schema byte records/decisions. Никакого `protocol=4` rewriting внутри5 fixture |

Каждый retained positive/ambiguous/partial/C0/warm fixture сохраняет actual source+after snapshots, полный group native/context/proposal/policy/budgets, все full/omit/repeat CSV со всеми somas и actual input, refs/final raw targets/residuals. Sidecar cert3 не считается package6; source-only assertion не считается независимым numerical replay.

## 9. Обязательные независимые gates

| Gate/source | Зачем нужен | Что не заменяет |
|---|---|---|
| A0 Pulse823d47 / Root32702, old97 | Mechanical numeric preflight A/B с compiled macro-expanded inventory | Text-equivalence receipt не runtime A/B |
| STEP2 mechanical d688, соответствующий Root pin | Отдельная проверка extraction старого context path | Pure40 arithmetic не native/context acceptance |
| Callback Pulse88ea9 / Rootcc23, full248 source scope и отдельные timing controls | Raw cancel delivery/lifecycle/budget semantics реально на native пути | Targeted timing/resource controls не полный248; package6 не может объявить baseline принятым |
| STEP2 budget Pulsefeb3 / Root9f6988,102 новых / planned384 union | AllN factories/proposal/archive2/retained cap и native dimensions | Source review и pure40 не подтверждают native growth или portable runtime |
| Core Pulse376bee / Root6579c5,24 новых / planned408 union | Typed search/final/cert3 live guards и actual primary | Старый143 technical no-raw gate не независимый replay нового метода |
| Будущий S3-B source pin | Actual service5, sink/cancel/warm/allN/ledgers/physical N1 | Не завершает package6/CLI/recognition или научную convergence |
| Будущий S3-C/D | Actual Train→package6→actual import→Test, independent Python primary replay/visual evidence | Не переписывает прежние negative receipts и исходные августовские наблюдения |

Все новые native/mixed gates выше остаются непринятыми **этим документом**; их текущие результаты и dispatch ведёт root в отдельных immutable receipts. Полные408 source IDs из core inventory включают полный historical248 subset, но список ещё обязан совпасть с реальным compiled inventory на worker. Изменённые после pin источники проверяются новым job, без silent cache update. Source подготовка последующих commits допустима параллельно; runtime admission только после нужного source review и gates. Merge только `--no-ff`, без rebase/cherry-pick/amend. Локально здесь только Git/text/AST metadata, никаких C++/numerical runs.
