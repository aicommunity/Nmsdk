# Минимальный отзыв live authority при новом Begin

Статус: **SOURCE DESIGN, production fix НЕ реализован**. Рассмотрен Pulse `800f92ae1f9e0133cefc0ccfe36abc3d8c99727f`, Root reproducer `f74b9fbf9ece38668396c21fa569d688f595bb05`, Rdk `d6c9df759a3ee20ad42fa0a83841f19385fba60a`. Четыре f74 controls не исполнялись. Baseline full248/S3-B470/runtime acceptance не следуют из этого review; package6/CLI/default activation остаются закрыты. Новых сборок, численных tests, server dispatch/cache updates нет.

## Решаемое правило

Чужой **явный Begin, дошедший до захвата executor**, отзывает право старого manual actor на НОВЫЕ Arm/measurement/Consume. Ни Finished, ни mode1 Need=true, ни восстановление прежнего semantic graph это право не возвращают. Исторические primary/proofs/DATA остаются читаемыми. Новый manual actor, явно созданный ПОСЛЕ Finished, должен получить текущую authority и работать; это не восстановление старого lease.

Обычные свои raw/N+2 next groups и owned edit → fresh prepared не являются чужим захватом. Они не должны инвалидировать immutable P0/C0/targets/family. Старый measurement до физического edit всё равно отклоняется существующими live model/instance/lease guards; новый proposal измеряется по actual current graph. Owner Reset/Default/Build/Init/UnInit и замена child nodes продолжают иметь прежние Rdk/physical-instance правила. Return values Build/Calculate/Reset не используются как error/control channel.

## Фактические переходы Pulse800

| Переход | `attempt` | `compositeGeneration` сейчас | Важное для guard |
|---|---|---|---|
| Manual Bind при Idle/Finished | Читается как initialEpoch отдельно; snapshot attempt сейчас не хранится | Snapshot не хранится | Owner service не регистрирует manual actor |
| Early Begin отказ до executor Reset: recognition / уже active / неподнятый external live-finalization request | Без изменения | Без изменения | Захват ещё не начат; сам такой отказ не должен отзывать authority |
| Begin после early checks: `NativeProbeControl.ResetControl`; затем service ResetControl/InvalidateTarget | Без изменения | `++` только если service уже хранит `composite` | **Дыра failed Begin при composite==null** |
| Успешный scalar3 Start (`NativeTrainingService.cpp:129`) | `++` | Без изменения | Snapshot только compositeGeneration пропустит takeover |
| Fixed4 construction/restart до публикации (`NativeTrainingServiceComposite.cpp:122–147`) | Ещё старый | Ещё старый | Новый actor проходит Bind/CheckBoundary до state Capturing; stored warm actor использует RestartOwned |
| Fixed4 commit | `++` | `++` | Новый actor уже/теперь `service.composite==this` |
| Candidate5 allocation/replay/fresh guard до publication (:151–208) | Ещё старый | Ещё старый | Actor ещё local; service по-прежнему Idle; guard не должен требовать будущий session |
| Candidate5 atomic commit | `attempt=nextAttempt` | `++` | Swap устанавливает actor pointer; complete/partial warm family/ledger уже подготовлены |
| Finish success/error (`NativeTrainingService.cpp:348`) | Без изменения | Без изменения | Смена state сама по себе не является новой authority и не должна восстанавливать старую |
| Service interrupt/cancel (:590) | Без изменения | `++`, только если есть stored composite | Его actor RevokeLive/SuspendOwned; own exact raw cancellation отдельно защищён executor generation |
| Own raw Queue / ResetControl executor | Без изменения | Без изменения service epoch | Меняется **другой**, raw executor generation; это не takeover epoch |
| Applied owned edit → RefreshOwnedAfterEdit (:543) | Без изменения | Без изменения | Actor обновляет собственный lease/generation; initial family и attempt clocks не перезапускаются |
| Service Reset/InvalidateTarget при наличии composite | Без изменения | `++` | Actor RevokeLive до возможного private RestartOwned; partial/warm DATA отдельно сохраняются |
| Portable restore / service move assignment | Может получить сохранённое значение `sessions` | Может снова стать default 0 | Числовая пара не является уникальной identity самого экземпляра service |

Конкретные owner `BeginNativeTraining` находятся Classic:4420 / Branch:5199. Публичный `NativeTrainingController()` возвращает **const** service, поэтому тестировать его mutable Reset через const_cast нельзя. Для isolated no-stored-composite случая реальный вход — некорректный Begin ПОСЛЕ executor Reset и ДО успешного Start. Обычный owner.Reset полезен как lifecycle control, но его отказ нельзя приписать одному service epoch: Rdk observation уже истёк.

## Вариант A: существующая числовая пара

В Bind сохранить `(service.attempt, service.compositeGeneration)` в private lambda, и сохранить текущий запрет constructor при Active. Proposed guard, вызываемый лишь после проверки owner lifetime:

```text
if service.composite.get() == this:
    allow this ownership check            // cancelled/lifecycle/Need guards всё равно обязательны
else:
    require service.state is NOT Active
    require service.attempt == boundAttempt
    require service.compositeGeneration == boundGeneration
```

Исключение exact owned actor принципиально: cold actor constructed ДО publication, fixed4 RestartOwned и candidate5 adopted actor не обязаны наблюдать будущие counters в Bind. При service Reset ранее stored actor уже RevokeLive, поэтому pointer exception сам по себе не возрождает старый lease. Private RestartOwned/RefreshOwned создают новую authority только после штатных source/model/clock checks. Manual-after-Finished получает нынешнюю пару, хотя stored pointer относится к ранее завершённому service actor: его вход допустим.

**Нужное дополнение A:** service ResetControl должен продвигать control epoch **даже если composite==null**, иначе failed Begin остаётся обходом. Успешный scalar3 Start ловится attempt; successful4/5 ловятся обоими счётчиками. Finish не должен записывать snapshot заново. Snapshot старого manual actor никогда не «догоняется» по Finish/совпавшему graph/Need.

Преимущества: несколько private captures/сравнений, нет нового lifetime типа, существующие сервисные session IDs и counters сохраняют предназначение. Продвижение generation при empty-composite reset не влияет на callbacks отсутствующего actor; при наличии actor обычный шаг остаётся одним. Physics, residuals, ordering, schemas/proofs не меняются.

**Ограничения A для production-review:** нынешние Start3/4 и Reset/interrupt не везде защищены от overflow; mathematical equality числового epoch не должна превращаться в ABA после wrap. Полноценный A требует общего fail-closed правила nonwrap и проверки всех increments, не исключающей noexcept cleanup при Reset. Кроме того, portable restore/move service способен установить те же `(attempt,generation)` повторно; protocol5 дополнительно защищён actual node-instance/graph/Need checks, но одна пара не доказывает смену экземпляра service. Нельзя объявлять snapshot самостоятельным универсальным lifecycle proof или менять counters, приходящие из portable accounting, в фиктивный process-local lifetime. Эти края расширяют фактический patch по сравнению с двумя сравнениями.

## Вариант B: один private control-lifetime token

Предпочтительный узкий вариант, если нужен строгий отзыв без ремонта смысла существующих callback/accounting counters: добавить **только private, не сериализуемый identity token** в NativeTrainingService. Он не содержит model/targets/protocol/clock и не является отдельным orchestrator. NativeCompositeTrainingAttempt — уже friend service — получает weak observation при Bind. Concrete public API, configs, archives, schemas и существующие `attempt/compositeGeneration` не меняются.

```text
service private shared_ptr<const ControlLifetime> controlLifetime // initially null

ObserveForBind():                         // private actual-owner factory path; fallible
    if null: allocate new empty token
    return weak observation of current token

InvalidateControlLifetime():              // private, noexcept
    controlLifetime.reset()               // no allocation; all older observations become stale

RequireOwnerControl():                   // owner lifecycle must already be current
    if service.composite.get() == this:
        return                           // STILL subject to cancelled/lease/Need/model guards
    require service.state is NOT Active
    observed = boundWeak.lock()
    require observed exists AND service.controlLifetime == observed
```

Сравнение с **нынешним** token обязательно, одного `!weak.expired()` недостаточно: временный lock другого stack frame может ещё удерживать старый token во время reentrant invalidation. Actor сохраняет weak observation, не shared ownership; callbacks/portable DATA не получают token. Нет numeric overflow и повторного совпадения epoch после invalidation. Guard после owner life не читает уже умерший owner/service.

Минимальные invalidation sites:

1. **Вход service ResetControl**, без условия composite!=null. Он вызывается реальным Begin ПОСЛЕ executor.Reset, поэтому failed Begin отозван даже при нулевых counters и отсутствии actor. InvalidateTarget делегирует ResetControl и не mint-ит новый token.
2. **Успешный commit каждого Start3/4/5**, рядом с существующей publication, без allocation/callback. Это покрывает настоящий низкоуровневый successful Start и не зависит от версии. Factory actor, созданный до commit, остаётся допустим по exact owned pointer. Pure rejected direct Service.Start, не тронувший executor/не опубликовавший attempt, сам по себе не является takeover; rejected concrete Begin уже отозван пунктом1.
3. **Явное CaptureCompositeInterrupt**, перед early return при отсутствии composite: управленческое прерывание владельца не должно зависеть от наличия stored actor. Дальше прежняя raw cancellation/lifetime/notification логика сохраняется. Private owned edit Refresh не вызывает invalidation.
4. **Замена service при native import** естественно уничтожает старый private token. Нынешние prepared portable services не имеют native actor/token; наличие arbitrary imported token запрещено конструкцией codec. Shared native authority не переносится через JSON. Временные internal locks старого token всё равно не пройдут сравнение с текущим token.

Finish ничего не инвалидирует и ничего не обновляет у manual actors. Own next-group Queue не меняет token. Новая manual factory после Finished при необходимости lazy-mint-ит свежий token; allocation — часть уже fallible construction. Reset/interrupt остаются allocation-free; Build/Reset bool semantics прежние. Одновременная конкуренция нескольких manual actors не вводится и не объявляется урегулированной этим узким правилом; задача здесь — явный чужой **service Begin**, а не новый общий scheduler.

B требует чуть больше private source, но оставляет callback-generation арифметику full248 полностью прежней и не использует portable session counter как lifetime. Поэтому B предпочтителен для source review; A допустим как более узкая альтернатива только с явным nonwrap/service-incarnation scope. **Ни A, ни B этим документом не реализованы.**

## Все live входы должны использовать один guard

Нельзя исправить только closed RequireLiveModel. В Pulse800 open `RequireIdentity → lease.requireCurrent → requireLiveModel(false)` НЕ проходит CheckClock/requireOwnerControl. Точки установки guard:

- Bind создаёт private owner-control observation/closure; constructor по-прежнему запрещён при активном чужом service.
- CheckClock и CheckBoundary продолжают вызывать её после owner-lifecycle проверки.
- **Все три** lease.requireCurrent (InitializeShared:271, RestartOwned:629, RefreshOwnedAfterEdit:715) вызывают тот же guard после `!cancelled && ownerLife.IsCurrent`, до actual Need/readback. Так старое open Arm не обходит отзыв и accepted previous-final values recheck также отзывается.
- Adapter.queue проверяет её снова **после** `beforeNativeQueue` callback и **до** реального Queue: callback мог начать чужой service без owner Reset. Сначала прежняя проверка actor/owner lifetime, затем новый guard; никакого raw-trial cancellation чужого поколения.
- Queue/takeResult/cancel generation checks остаются точными: guard не превращает старый actor в владельца нового raw trial и не меняет full248 callback/sink ordering.
- Record, Selection, saved raw samples, strict archive/portable DATA decode не требуют текущего token/epoch. Они не mint-ят lease и должны оставаться читаемыми после отзыва.

Новый отказ — invalid live authority, обычный `invalid_argument` с отдельным reason, например `native_training_owner_control_replaced`. Final/Bounded уже умеют fail closed через InvalidObservation без accepted input/new certificate; Need=true не выдаётся за ExternalStop по данным flag=false. Никаких physics/finite guards, parameter writes, component calls, predictor/peak/tolerance changes здесь не требуется.

## Контроли следующего reviewable patch

Сначала сохранить f74 negative receipts на Pulse800 как отдельные actual outcomes (root решает dispatch); затем production fix в отдельном commit и повторить их вместе с положительными controls. Не переписывать historical pin или expected assertions ради зелёного.

1. **Существующие f74 4:** Classic/Branch foreign Begin5→Finished и own-next-group positive. До old Consume оба original group clocks и оба attempt elapsed должны быть доказанно ниже действующих caps, graph/source/Need/C0/lifecycle прежние, frozen candidate/proposal replay точный. DATA decoder после takeover по-прежнему проходит.
2. **Failed concrete Begin до constructor, no stored composite, Classic/Branch:** после old final measurement подать plan с invalid reference-probe budget; actual Begin сбрасывает executor и возвращает Finished InvalidModel, attempt не увеличен, old Need=true/graph/source/UM прежние. Old Consume обязан отказать. Это основной дополнительный control, который one-counter/неизменённая пара не закрывает.
3. **Scalar3 takeover, Classic/Branch:** построить настоящий старый scalar3 plan штатным config builder (без подмены protocol5 raw packet), начать actual service, завершить реальным коротким model budget в mode1 при fixed geometry/zero edits. Exact не требуется; Started/actual raw work, terminal state, восстановленный source и неизменная semantic physics обязательны. После окончания old protocol5 Consume отозван. Это защищает от guard только по compositeGeneration/только новым protocol5.
4. **Fixed4 takeover, Classic/Branch:** настоящий штатный fixed4 Begin/Finish, прежние source/graph/Need, старый5 token не возвращается. Separate branch coverage, не blind `>=4`.
5. **Manual-after-Finished, Classic/Branch:** после чужого завершённого service явно создать НОВЫЙ native actor/current observation и новый complete reference set. Он вправе получить собственную новую family и завершить typed measurement; старый retained actor одновременно остаётся revoked. Это защищает от запрета любого Finished pointer!=this.
6. **Own service warm/edit controls:** существующие fixed4 warm/owned edit и Service5 actual owned growth/warm/partial recapture cases остаются обязательными. Prepublication fresh checks должны проходить; old pending до edit не принимается, но новый prepared после штатного Refresh принимается. Ни старые group deadlines, ни targets/family не продлеваются/переснимаются из trained graph.
7. **Open Arm / reentry:** до full closure старое prepared не должно Arm после foreign Begin; beforeNativeQueue callback, начинающий чужой service, не должен затем поставить старую raw trial. Сохранение partial primary/точного чужого raw-result owner отдельно проверяется с callback248; это не разрешение nested Calculate.
8. **Lifecycle/import:** existing Reset/Default/native node replacement controls; для B — same-package repeated import не переносит control token, для A — отдельное доказательство nonwrap/incarnation scope. Unobservable direct-value ABA и непрочитанные кратковременные Need transitions НЕ объявлены покрытыми. Need=false, наблюдаемое на штатной boundary, по-прежнему ExternalStop.

Все новые controls — real owner/storage/scheduler/source и actual clocks, без fake certificate/valid flag/cached-only source; numerical execution только на разрешённых серверах позднее. Old scalar/fixed4 scientific math A/B, full248 и S3-B470 остаются самостоятельными gates. Новое source-correct control lifetime не является доказательством сходимости, полноты всех режимов или готового package6/Train→Test pipeline.
