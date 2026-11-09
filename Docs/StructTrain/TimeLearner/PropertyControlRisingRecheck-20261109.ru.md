# PROPERTY-CONTROL-RISING-001: повторная source-проверка

Статус: read-only source review и предложение для будущих Step6/7. Поведение
компонентов не изменено; компиляция, тесты, серверные команды и численные
вычисления не выполнялись. Этот пункт независим от frozen source35/native48.

Проверены Root `956443560ebdb788a0642856381c9c6a7a554b76`, его Pulse gitlink
`f7a0e3e63ec29d4647790a695606d1ca32164ef3` и Rdk gitlink
`d6c9df759a3ee20ad42fa0a83841f19385fba60a`. Rdk читался через Git именно в d6:
локальный рабочий Rdk HEAD отличается. Соседний `.source.json` содержит полные
Git blob IDs/SHA256 и точные line slices, включая исходные переводы строк.
Исходный finding сохранён в `PropertyOwnershipReviewFindings-20261108.ru.md`.

## Подтверждённые source-факты

Rdk `Core/Engine/UProperty.h` разделяет несколько механизмов:

- `SetData:705–749`: для локального свойства вызывает setter владельца перед
  записью `v`; равное значение может быть пропущено через CheckEqualsFlag.
- Connected `GetData:608–702` читает connected output без вызова setter learner.
  Connected `SetData` и `SetDataDirect` игнорируют запись.
- `SetDataDirect:752–785` для локального свойства меняет значение без setter.
- **AttachTo:789–815 — connected-read**, он устанавливает IsConnectedFlag и
  CachedConnectedOutput. Это не ExternalDataSource writable alias. SetPointer
  также устанавливает connected-read path (`:857–865`).
- Ветка ExternalDataSource при ненулевом pointer делегирует GetData и обе записи
  источнику (`:633`, `:709`, `:756`). Но сам pointer protected, конструкторы
  инициализируют его нулём, DetachFrom обнуляет. Публичный путь его активации у
  конкретного IsNeedToTrain в просмотренном pinned Core/Tests не найден.
  **Активация не прослежена, actual runtime reachability не заявлена.** До её
  установления этот путь нельзя изображать посредством AttachTo или тестового
  доступа к protected полю.

Последний пункт исправляет неточную группировку AttachTo/ExternalDataSource в
раннем read-only сообщении. Это уточнение источников, не изменение Rdk policy.

В Pulse Classic setter `NNeuronTimeLearner.cpp:2787–2810` и Branch
`NNeuronTimeLearnerBranch.cpp:3553–3577` при локальном V2 false→true после native
ownership очищают request intent, вызывают service ResetControl и probe
ResetControl. При false existing setter немедленно вызывает ExternalStop.
Owner.Reset/Build/Default из этого setter не вызываются.

`NativeLearnerLifecycle.h:58–76` допускает configured autostart только при
ControllerVersion2, true и **Idle** service с доступным runner. План берётся из
проверенной NativeConfiguredPlan; отсутствие или изменение configuration
требует штатного Build и даёт явный отказ. Наличие true само по себе не запускает
Finished service. В активном service false проверяется до/после native tick
(`NativeTrainingService.cpp:206–216`, `:279–289`); composite paths сохраняют свою
existing cancellation/harvest логику.

| Текущее состояние и способ | Текущее source-поведение |
|---|---|
| Первый Idle + true, configured V2 | Возможен initial autostart; способ чтения true не доказывает restart после Finished |
| Локальный V2 false→true | ResetControl переводит service в Idle; следующий native tick может начать warm attempt |
| Connected или direct false, наблюдённый активным tick, затем true | Stop оставляет Finished; rising обходит setter, поэтому autostart predicate не срабатывает |
| Постоянный true при Active или Finished | Не является новой командой и не создаёт бесконечные attempts |
| V1 | Existing automatic V2 dispatch отсутствует; явный BeginNativeTraining остаётся отдельным API |

ExternalDataSource условно имеет writable-alias semantics, если будет установлен
реальный путь его активации. Нельзя менять общий Rdk setter/direct-write
протокол ради унификации learner control. В частности, существующие
BeginNativeTraining и mode0 завершение используют SetDataDirect; для connected
read эта запись игнорируется, для реально активного external alias была бы
делегирована provider. Это source distinction, не доказанная learning bug.

## Reset, warm family и исторические данные

`NativeTrainingService::ResetControl:379–391` отзывает owner control lifetime,
live lease composite и текущий search/request. Он сохраняет полные references,
reference binding, retained epoch, C0/history и исходную source family; при
неполном capture сохраняет constraint исходной revision/epoch. Сам по себе он
не строит новый граф и не заменяет начальные targets текущим обученным графом.

`NativeProbeExecutor::ResetControl:506–512` повышает control generation,
отменяет raw probe, восстанавливает presentation/source bindings и очищает raw
result/trial IDs. Это отличается от общего learner.Reset: тот проходит Rdk
lifecycle и существующий InterruptComposite перед reset control. Его нельзя
подменять restart-командой при сохранении live lease.

Warm Start проверяет актуальную revision/epoch и family. Scalar Start,
StartComposite и StartCandidateWindowComposite сохраняют свои отдельные guards;
новый service attempt/request получает новую identity, old references остаются
исходными. Полный family guard, C0 ownership и partial allN semantics не ослаблять.
ResetControl может временно сохранять старый completed certificate как
исторические DATA. Новый Start его очищает; это не новая Exact попытка и не
разрешение recognition после преобразования модели.

Для быстро меняющегося direct/connected false→true между двумя наблюдениями
нельзя утверждать, что false когда-либо был замечен. Отдельно не проверена
смешанная последовательность direct false → local true в активной raw-пробе:
она может войти в reset control до обычного stop/harvest. Это адресная ветка
для controls, а не уже установленная ошибка сохранения данных или обучения.

## Что уже есть в Root956

Это source coverage существующих real component fixtures, а не новый runtime
receipt и не утверждение приёмки всех перечисленных tests:

- `NativeConnectedStop.*`, 20 macro-expanded cases: Classic/Branch × modes0/1 ×
  Early/Partial/Search/AfterSample/KeepTrue (`NativeModelEditor.cpp:4223–4311`).
  Доказывают заданный stop/hold contract, но не rising restart после Finished.
- `NativeCompositeAutostart.*`, четыре cases (`CompositeTraining.cpp:934–983`):
  configured V2 initial Idle/start, без второй rising-команды.
- `NativeTrainingService.ExactAutoCompletionResetWarmRestartAndRetarget`
  (`NativeModelEditor.cpp:4633–4666`): явные Reset + Begin, сохранение reference
  trial/targets и invalidation при retarget. Не supplier restart.
- `NativeTrainingIntent.*`, восемь macro-expanded local/connected cases
  (`NativeModelEditor.cpp:4314–4397`): request identity, явные Reset/Begin/import,
  сохранение параметров и supplier binding.
- `NativeCompositeService.*WarmResetPreservesInitialFamilyAndC0`, обе topology;
  existing partial/default/retarget/cancelled delivery controls. Warm использует
  явный Reset/Begin.
- CandidateWindow Factory/Core/Service Need-false controls и warm-after-growth/
  partial warm controls: защита admission при false и сохранение исходной family.
  False-before-consume не доказывает произвольный unobserved ABA/restart.

## Предложенное будущее поведение V2

Предложение родительского source review: общий native lifecycle наблюдает
external request edges **на native ticks**. После реально наблюдённого false
следующий true разрешает warm restart; constant true никогда не повторяет
завершённое обучение. Первый Idle/start остаётся отдельным исходным случаем.

Это ещё не код. Минимальная логика должна находиться рядом с existing configured
BeforeCalculate dispatch, без нового orchestrator и вложенных Calculate:

```text
observe actual request level at a legal native tick
if false:
    remember that low was observed; keep existing stop/cancel/harvest path
else if true follows an observed low and service is at a closed restart boundary:
    validate current configured plan, graph, source family, epoch and C0
    prepare warm restart preserving original complete references/targets
    commit one new attempt/request; consume that edge exactly once
else:
    keep existing initial-start or active/finished behavior
```

Немедленная revocation существующего локального setter сохраняется. Нельзя
потерять её из-за polling, двойным dispatch создать два attempts или после
отказа повторять один edge на каждом true tick. Initial ownership, Reset,
Default/pool, retarget/import и already-finished Recognition требуют явного
инициализирования/сброса edge state в своих existing control boundaries.
V1 и стандартные connected/alias writer semantics Rdk не меняются.

Альтернативы: оставить restart только явному Reset/Begin; либо оставить
текущее различие local/connected с явным документированным ограничением.
Обе проще, но не дают единой tick-observed V2 команды внешнему supplier.
Выбор polling не восстанавливает ненаблюдавшийся false, не делает thread/ABA
теорему и не разрешает обход expired owner/native proof. Более тяжёлые изменения
UProperty или общий reset графа для этой задачи не требуются.

## Адресные paired controls для будущих Step6/7

Использовать существующие fixtures/runner и честные native clocks. Начать с
Classic/Branch × CalculateMode0/1, одинаковой модели и terminal boundary;
семантические scenarios ниже не являются уже добавленными TEST IDs/inventory:

1. Local против SetPointer supplier: observed false до Finished ExternalStop,
   затем true без Reset/Build/Begin. Сначала сохранить baseline текущих разных
   transitions; только после реализации ожидать один одинаковый warm restart.
2. Те же пары после Exact и после unresolved Finished. Не требовать Exact от
   новой физики; проверять новый attempt/request, отсутствие нового сертификата
   до fresh allN final и удержание результата при постоянном true.
3. SetDataDirect после tick-observed false против локального setter. Отдельный
   контроль false→true без промежуточного наблюдения — без обещания обнаружить
   скрытый edge. Смешанный direct false→local true во время raw-пробы сохраняет
   отменённый/partial packet и restore readback либо даёт явный отказ.
4. Явный learner.Reset → true/autostart как положительный contrast control:
   физические L/Ns/Rs/C0/instance identities сохраняются по контракту, owner
   lifecycle lease истекает; это другой путь, не реализация rising команды.
5. ExternalDataSource variant не включать до установления действующего
   production activation path. AttachTo можно проверить как connected variant;
   он не заменяет доказательство external alias activation.

В каждом pair сохранить public SessionAttempt/ModelEpoch/request identity,
current model/readback и original P0/reference proofs/C0/source family,
восстановленные MatrixData и connections, raw cancellation/partial journal,
supplier value/binding и public owner lifecycle observation. Не читать private
поля через test hooks. Существующие target/family/budget guards, allN final и
прежние numerical tolerances остаются прежними; warm не recapture trained graph.
Старые certificates помечать историческими DATA, не новым success. Retarget/
Default должны по-прежнему invalidировать family. Ни один source-факт здесь
не является scientific PASS, новый control gate или activation defaults.
