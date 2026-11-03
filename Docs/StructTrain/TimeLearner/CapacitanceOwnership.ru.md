# Автоматическое владение исходной C₀

## Диагностика конфигурации dormant4, 03.11

E1 (`93e623903e4edf3bebb698ae26553772d910ee43`) локализует два отсутствующих
в live-графе соединения после смены класса канала напрямую. Повторный Build
готового родителя не перестраивает связи: setter инвалидирует только мембрану.
Строгий snapshot import обоснованно отвергает такой граф. Это ещё не дефект
сохранения dormant C₀. Проверка переходит на штатный Load всего owning tree.

E2 (`f6db81b9f4331fb221172271593c0626ba421b4f`) завершился ошибкой компиляции:
SaveComponent/LoadComponent принадлежат UNet, а rig.model объявлен UContainer.
Численные тесты не запускались. E3 использует проверенное приведение к UNet и
явный lifecycle UnInit → Load → SetGlobalTimeStep → Build → Init → Reset.
Дочерние handles обновляются после загрузки; все связи и исходная неоднородная
ёмкость проверяются до первого edit. Это исправление fixture, без ослабления
identity или изменения алгоритма.

E3 (`5d0438d14f5650917f541c99729dafe62f3c4d55`) успешно собран, но все4 tests
остановились до Train: после Load фактический ExcChannel сохранил прежний
storage-класс. Все47 members и outer hashes проверены, primary86 641 bytes.
E4 согласует ExcChannelClassName с Class дочернего ExcChannel в полном native
XML, сохраняет XML как артефакт и проверяет effective property/class, связи и
исходную heterogeneous C до edit. Root7a4417b5a4eaed6f42d1435e193d8072855e431f,
Pulse30495d143795022ad444bf290d2ac30b7e140199. Native normal4 назначен на Elder,
результат ещё не получен. E1/E3 не доказывают дефект dormant export: до него
эти попытки не дошли.

## Owning controller после Load: E4 и следующий адресный E5

E4 (`6cc7274d5a228954f6dbe7ad50c239381ba1b429`): сборка успешна,4 FAIL до Train;
все51 members/103 675 compressed bytes проверены. Сохранённый native XML
содержит новый storage-класс и в ExcChannelClassName, и в Class дочернего узла.
При полном model Build ещё не adopted learner выполняет legacy BuildStructure,
который штатно удаляет загруженный Neuron и создаёт новый из общего образа.
В таком порядке тест сам теряет неоднородную конфигурацию.

E5 готовит загруженные Dataset/Neuron через их native Build/Init, затем явно
AdoptNativeModel закрепляет готовый граф; обычный внешний scheduler завершает
lifecycle owner. Порядок соответствует construction/adoption API: Inspect
проверяет ready/initialized физических детей до принятия декларации, а Build
owner уже учитывает native-владение. Learner-specific Ready toggles, Default,
самоприсваивания параметров и вложенный Calculate не добавляются. Полные
bindings, класс канала и1.41nF сохранённой мембраны остаются assertions.
Результат E5 ещё не получен; dormant export по E4 не проверен.

## E5 не подтвердил достаточность перестановки adoption

E5 (`ca83319e75f4cf39f0ff6eec994ea84aa4845065`),51 members/103 681 bytes,
проверен полностью: успешная сборка,4 FAIL до Train с прежним классом канала.
Значит объяснение только последующим legacy Build owner недостаточно;
сохранённый XML по E4/E5 корректен, но точная стадия замены ещё не установлена.
E6 добавляет read-only snapshots после UnInit, Load, frequency assignment,
Dataset Build/Init, Neuron Build/Init, adoption и native model Init/Reset/Calculate.
Снимки включают реальные class names, Ready/Init и обе контрольные C. Они не
меняют структуру, физику, допуски или strict import identity. Следующая правка
должна опираться на первую фактически изменившую класс операцию, а не на
предположение о финальном месте отказа. E6 назначен на Elder с root
5f6add3064890a7647d43a2ec8ebc34fbe252695, Pulse30495d1, worker278449 и
publisher278450; результат pending. Ранее отдельным docs-only merge принят
точный канонический lifecycle Rdk (root develop3a6b83de2, Rdk33bdf2d1): Core
и Deploy совпадают с a62393f7; работающие jobs сохраняют собственные gitlinks.

## E6: первая потеря физики находится внутри LoadComponent

Evidence `38cf86675497e9d7ca441467b51393fc03f1baff` проверен:99 members,
106 654 bytes. Во всех4 случаях первое after_load уже содержит прежний channel
class и1nF вместо retained1.41nF; последующие frequency/Build/Init/adoption шаги
не являются первой причиной. Это уточняет предыдущую гипотезу о позднем Build.

Подтверждённая исходниками цепочка: UNet.LoadComponent(links=true) →
SetComponentInternalLinks → BreakLinks → DisconnectAll → Build. Поэтому
полный Load может войти в структурную сборку владельца до возврата управления.
E7 загружает готовый граф в штатном learner StructureBuildMode=0. После
проверки/AdoptNativeModel восстанавливается исходный mode1 до первого Train.
Это реальная смена режима явного графа на исходное управление, не самоприсваивание
для пробуждения. Режим вложенного нейрона2 не меняется; все class/C/bindings
assertions остаются. Нового результата пока нет. Независимые риски удаления
канала при повторной сборке самого NPulseNeuron требуют отдельной проверки,
а не предполагаются исправленными этим setup-переходом.

## Текущая приёмка, 03.11: открытый native roundtrip дефект

Normal owner8/readers19 пройдены, temporal48/72 построен, selected12 просмотрены.
Normal transport43 завершён:39 PASS и4 FAIL в NativeDormantCapacitanceTransport.
Evidence `e324c1603aa388c92a46c3be07d8927d1f69920c`: outer hashes и все846
members проверены; compressed primary6 535 342 bytes. Readers26 после failed
native gate не запускались. Полная приёмка owner остаётся открытой.

Все четыре topology/normalization случая остановились ещё в setup:
PrepareCapacitanceTransfer → native physical edit preview/import сообщает
archive_model_mismatch: model_mismatch: model.bindings.size. Перед этим fixture
получает новый channel image через RegisterClassImage, меняет ExcChannelClassName
одной мембраны и вызывает neuron Build/Init/Reset. До удаления последнего
потребителя образа, dormant export и fresh-process import тест не дошёл.
Нельзя приписывать этот отказ потере unused image или ослаблять graph identity.
Следующий шаг — адресно сравнить связи после смены класса/повторного Build и
native snapshot load, проверить создание через штатную storage image chain.
Исправлять подтверждённого владельца дефекта; дополнительные «будящие» Build
и подмена графа более простым профилем не являются решением.

ASan owner C3 прошёл5/8: первый20k ClassicN0 завершился за2798.618s, выполняется
ClassicN1At20000 (native handle2473290/start_ticks273872272 подтверждён).
ASan transport D1 со старыми четырьмя dormant fixtures отменён до source/build/
runtime mutation. Cancellation evidence d6135806b068100640afc6e16d278d693fa18324:
все4 file hashes проверены, точные PID/start_ticks закрыты, прежний HEAD
неизменен, активный ASan owner8 подтверждён живым. E3 normal4 на Elder использует
root3d144493aa073663d309946a961bf055bee617f4, Pulse30495d1; новая ASan transport
серия требует исправленного fixture и положительного адресного normal результата.

Следующий пункт этапа7 после explicit C₀ API. Он не включает bounded C-trim
search: V2 SyncCapacitanceTrimOn остаётся запрещённым до его отдельной проверки.
Capturing per-input amplitudes, anchor и исходные допуски не меняются.

Исходный Core Pulse develop `8b41ffe4c438b188ef83406cfda1b616e2f3b199` сохраняет
NativeLearnedCapacitanceState только при import. Bound edit и обычные L/Ns/Rs
edits не владеют полной картой исходных C₀/абсолютных scales; первый export
требует ручной передачи correction. Проверять этот риск надо на native owners,
а не копии helper-функции. Baseline gate8 добавляет Classic/Branch × N0/N1 ×
2000/20000 Гц и сохраняет физические waveforms и JSON каждой фазы. Результат
gate пока не получен; исходный Core в baseline не меняется. В первом A1 уже
наблюдается пустой owner state после bound edits. Найдены и исправлены две
ошибки fixture: после Reset необходимо заново завершить реальную probe до
структурного edit; чтение отсутствующего поля через неконстантный QJsonObject
не должно менять локальную копию state. Assertions сохранены, raw A1 остаётся
непринятым из-за этой примеси ошибок теста. Corrected baseline требует A2.

Обязательная последовательность baseline: initial bound trim heterogeneous
Exc/Inh → trim другой мембраны → native Reset → обычный growth без correction
аргумента → реальные probes → попытка recapture/rebase trimmed baseline.
Проверяются полная owner-state карта, исходные C₀, storage-origin новых каналов,
model revision, сохранность прежних поправок и отсутствие изменений при отказе.
Это проверка API владения, не сертификат завершённого обучения и не классификация.

Реализация должна разделять исходную C₀, текущую ёмкость и controller history.
Нельзя захватывать текущую trimmed C как новую исходную baseline или обновлять
метаданные отдельной fallible операцией после необратимого физического commit.

```text
resolve optional correction against owned complete state
validate current owned state against the effective live graph
reject a conflicting/rebased baseline before live mutation
merge requested absolute scales with previous complete scale map
build native preview of L/Ns/Rs/C together
extend original C0 of added channels from verified storage images
encode and validate complete prospective state on preview
commit the verified physical candidate
verify effective graph and assign the already prepared state
on failure: restore graph/aliases and original owner state
```

`NativeEditResult` и `NativeCapacitanceEditResult` должны возвращать заранее
проверенное committed parameter state. Его authoritative owner — learner;
контроллер и отдельные callers не должны хранить конкурирующие копии. Ordinary
structural edits и resistance-domain preview автоматически используют owned
correction. Subset edit сохраняет уже применённые scales остальных мембран.
Первый schema2 bound edit начинает владение; schema1 primitive сохраняется как
legacy API без автоматического provenance. При имеющемся bound state нельзя
обойти его schema1-вызовом. История поиска при изменении влияющей C инвалидируется
штатной revision policy; поправка не применяется заново на каждом тике.

Приёмка далее расширяет baseline: repeated edits, shrink/regrowth, параметры
inhibition, rollback/injected failure, unchanged frozen model, warm continuation,
неявный export после completed/stopped Train и fresh import/re-export. Native
export/import переносит исходную C₀; XML/Copy не объявляются checkpoint этого
private controller/parameter state без самостоятельной проверки. Reset learner
не означает возврат физики к исходному storage image.

Для shrink/regrowth нужно явно определить dormant scales: отсутствие физического
сегмента не означает разрешение забыть исходную C₀ и повторно захватить ёмкость
из trimmed-состояния. Версионированное состояние должно различать применённые
scales существующих мембран и сохранённые scales удалённых мембран. Перед ростом
они заново разделяются на active/dormant по preview-графу. Recreated каналы
получают исходные индивидуальные C₀, новые имена — проверенный storage C₀.
Codec обязан отвергать active/dormant overlap, неизвестный baseline path,
не-конечные/bound-нарушающие scales и dormant запись существующего узла.
Storage closure проверяется целиком, включая исходные образы временно удалённых
каналов; изменение неиспользуемого сейчас образа нельзя скрыть shrink-операцией.
Кандидат Pulse `4ae7e5c7ecb6ee7b05003b0f49a9f514afcd55f1` реализует эти
механизмы, но ещё не прошёл server build/runtime. NativeLearnedState export
дополнительно сохраняет образы dormant-каналов для fresh-process import.
Root candidate расширяет8 ownership tests shrink/regrowth и negative codec
controls, сохраняет48 независимых effective graph/image/state snapshots;
production reader проверяет их физику, исходную C₀ и continuity maps между
фазами. Новый schema2 state не выдаётся за legacy schema1 без dormant history.
Потеря этой истории должна отвергаться даже при пересчитанных envelope hashes.

Ownership gate8 получает wall budget7200s для более тяжёлых наблюдений; model
time, physics, search tolerances и assertions не ослаблены. Более широкая
regression47 объединяет прежние8 legacy C edits,8 bound C cases,13 joint/failure
controls и14 completed/stopped/recognition transfer cases с8 ownership cases:
47 уникальных IDs после удаления4 повторов legacy cases внутри joint-контракта.
Она запускается
после ownership gate; до положительных normal/ASan и полных reader checks
в develop ничего из owner-кандидата не объединяется. Это всё ещё не C-trim
controller search, полная lifecycle/physics матрица либо научное8/8.

Временной report-контракт native-capacitance-ownership-report-v1.json объявляет
48 фактических полных probe traces (serial2/4/6/8/10/12 на каждый case): до C
edit, после Reset с сохранёнными C, после growth и regrowth для обоих input IDs.
Используется production native_test_reports: soma всех доступных каналов,
фактический stimulus overlay и zoom с native samples. После положительных
native gates нужны проверка полноты72 trial-soma pairs, читаемости выбранных
изображений и неизменности первичных CSV. Полные PNG/SVG/PDF — cache на M40;
Git — сжатые первичные данные, модели, метрики и выбранные проверенные рисунки.
До рендера/прямого просмотра визуальная приёмка не назначается.

## Уточнение roundtrip: параметры и полный граф

Первый кандидат B1 выявил избыточное требование теста: одинаковые L/Ns/Rs
после shrink/regrowth не задают весь граф. NativeModelEditor::Transform явно
освобождает прежние learner-owned excitation banks, сохраняя остальные банки
поставленной модели, особенно explicit neuron mode0. Исходный профиль имеет
idle ExcSynapse1 на внутренних мембранах. После временного превращения такой
мембраны во вход этот банк становится owned и при уходе входа освобождается.
В первом Classic2k case idle bank переместился с Dendrite1_1 на Dendrite1_2;
все C₀/scales восстановились, но разные nodes/bindings/caches дали разные SHA.
Это не доказательство потери C₀ и не разрешение удалить все unowned banks.

Исправленный контракт проверяет точный возврат C₀, scales и фактических
L/Ns/Rs, включая их независимое соответствие каждому живому банку. Каждый
полный граф сохраняет собственный реальный fingerprint; их равенство отдельно
измеряется и не подменяется равенством нескольких параметров. Frame schema2
содержит input_parameters плюс полный effective_model и class_definitions.
Production reader возвращает отдельно parameter_roundtrip_cases и
whole_graph_roundtrip_cases. Legacy frame schema1 не дополняется вымышленными
readbacks. B1 с избыточным assertion сохраняется отрицательным; C2 — отдельная
проверка уточнённого контракта, без изменения допусков и физики C₀.

Точное соответствие полного графа при native preview/live commit и model
export/import по-прежнему обязательно. Политика idle/released banks относится
к описанию математической модели и Stage6/7: полный state/revision нельзя
заменить в fingerprint/candidate cache одним L/Ns/Rs. Отдельный профиль с idle
банками0 можно задавать через storage, но это другая явно объявленная модель;
он не заменяет исходные профили незаметно и требует самостоятельной матрицы.

ASan B1 измерил308.652s уже на одном2k case с6 реальными probes. Нельзя
экстраполировать normal wall budget на инструментированный20k matrix. Для
исправленного контракта выделен отдельный native-capacitance-ownership-asan-v1
с outer execution budget18000s; обычный gate сохраняет7200s. Это не меняет
model time, физику, критерии, windows либо учебные tolerances. Старые B1
используют заведомо неверный whole-graph assertion; их намеренная остановка
должна сохраняться как interrupted/incomplete с точным owned process handle,
а не трактоваться как научная несостоятельность C₀ или успешная полная матрица.

## Проверенный checkpoint

Corrected baseline A2 завершён:8/8 отрицательных cases на Core8b41 без прежней
ошибки edit после Reset; evidence `a054904f31160271a87ea327353890f052d540f1`,
191 members/1 565 650 bytes проверены. A1 `f903a8273c28bb7597cb8008c095d31933322dff`
с ошибками fixture тоже сохранён:81 members/408 997 bytes проверены.

Первый owner-кандидат B1 намеренно остановлен по точным native handles после
выявления избыточного whole-graph assertion, без подмены результатов:
normal `81d4cad7211c633c37bef142707e486e66050cba` (183 members/6 651 611 bytes),
ASan `9168972e48e1181ae71033c19ce605b900ff7b52` (130 members/3 799 254 bytes).
Все members и intentional-stop receipts проверены. Raw native_gate сообщает
process_error/incomplete_test_observation из-за отсутствующего cooperative exit;
семантика задания — interrupted, acceptance=not_accepted. Отдельный audit JSON
Reports/StructTrain/TimeLearner/s07-capacitance-owner-interruption-audit-b1/audit.json
связывает эти уровни и точные PID/start_ticks/executable hashes. Это не научный FAIL.

Текущие jobs используют уже merged parser develop, Pulse
`f899ef024698afa7bc8e9a17f2307116368048da` (owner code как4ae7e5c, плюс принятый
NDataset), Rdk a62393f7 и Bin14a88195:

- Elder normal C2: root `3a1b7fe1f0a2a958d034736613f2793abe16c5ec`, readbacks
  s07-capacitance-owner-current-normal-c2, owner185679/start_ticks323290894,
  publisher185680/start_ticks323290894; outer7200s.
- M40 ASan C3: root `eab5e61c2c246d15dcf28ba03454b8ae44b1f6c2`, readbacks
  s07-capacitance-owner-current-asan-c3, owner2470460/start_ticks273856765,
  publisher2470461/start_ticks273856765; outer18000s.

Оба прошли server build и начали native8. Ожидаются19 reader checks после
native success. Результат пока pending, publisher ждёт закрытия точного owner.
M40 queued C2 (2467199/2467200, start_ticks273833678) отменён до fetch/checkout/
runtime changes ради измеренного ASan budget; cancellation receipts копируются
в C3 primary. Работающие source/build/runtime нельзя переключать вручную.
После успеха ещё нужны transport/legacy regressions и временные
отчёты с прямой visual QA. Общая цель и этапы4/5/6/7/11 не завершены.

Изменения выполняются в codex/timelearner-capacitance-owner от принятого develop;
server jobs не должны вытеснять текущую invalid-reload проверку. После адресной
приёмки — --no-ff merge Pulse develop, затем root с точным gitlink. Полные
этапы4/5/6/7 и исходная цель остаются частичными.

## Уточнённая проверка автоматического export и dormant import

Существующие completed/stopped fixtures теперь передают в same/fresh-process
import результат ExportNativeLearnedState без correction аргумента. Явный
export сохраняется как compatibility control: C₀ state, configuration, trained
inputs, полный semantic graph identity и image fingerprints должны совпасть.
Incidental XML State bytes не используются как подмена физического равенства.

Четыре NativeDormantCapacitanceTransport cases (Classic/Branch × N0/N1 при2k)
создают приватный проверенный образ канала через RegisterClassImage и native
структурную настройку мембраны. После удаления его последнего живого сегмента
имя образа сохраняется только в исходной C₀. Training при явно фиксированной
геометрии и sync=.2 нужен как completed transport boundary, а не новый научный
результат. Автоматический export обязан сохранить dormant scale и неиспользуемое
определение образа; same/fresh-process import обязан сохранить фактический граф,
состояние и полный stimulus/soma response. Parent overrides и post-Take Default
не добавлены.

Общий контракт51 объединяет ownership8 и43 сопряжённых проверок. После уже
пройденного ownership8 используется отдельный transport-regression43: не надо
повторять дорогие неизменённые8 owner cases лишь из-за правки transport fixture.
43 включают прежние39 уникальных explicit/joint/boundary cases и4 dormant cases.
Capacitance readers получают явный TIMELEARNER_CAPACITANCE_DORMANT_CONTROLS=1:
тогда обязательны10 completed+2 stopped C₀ packages, а не прежние6+2. Отдельный
reader требует4 реально dormant packages и проверяет отсутствие их образа в
живых nodes при наличии определения в archive. Без флага старый inventory
остаётся строгим; пропущенные новые cases не превращаются в PASS.
Это пока постановка адресной проверки, не полученный runtime-результат.


## Продолжение после восстановления Automats2, 03.11 00:15 UTC

Связь с обоими workers проверена. Elder C2 завершил все8 native cases успешно
(1409.723s); independent readers и публикация ещё проверяются. M40 C3 прошёл
четыре2k cases и выполняет ClassicN0At20000; процесс и start_ticks совпадают
с исходным owned handle. Повторные numerical jobs не запускались.

Conditional transport43 на root `3b55ff17ae1c28332882d2755a3b0bb9681bd860`
запущен заранее в ожидании успешной публикации своего owner8 и закрытия lease:

- Elder normal D1: owner203893/start_ticks323443588;
- M40 ASan D1: owner2488268/start_ticks273986367.

Readback names: s07-capacitance-owner-transport-normal-d1 и
s07-capacitance-owner-transport-asan-d1. После43 native обязательны26 readers:
native_gate8, capacitance_evidence15, dormant_evidence3. До проверки prerequisite
и process guard очереди не меняют source/build/runtime. Это pending, не PASS.

На M40 отдельно поставлен readonly renderer normal C2:
s07-capacitance-owner-temporal-normal-c2, supervisor2492051. Он ждёт evidence
branch codex/evidence-s07-capacitance-owner-current-normal-c2, требует passed
bundle с точным root3a1b7fe1f, проверяет outer SHA256 и каждый member, извлекает
production scripts из Git в отдельный source и строит отчёт в Data cache.
Обязательное покрытие:48 complete trials/72 rendered trial-soma pairs по
native-capacitance-ownership-report-v1.json, с реальными stimulus overlays.
Полный cache не публикуется в Git; selected figures и direct visual QA ещё
не выполнены. Renderer не использует leased ASan source/build/runtime.

Впоследствии normal C2 завершён:8/8 native и19/19 readers PASS. Evidence
`a928fb92edd0880728a697da0fed6d7ede3e7d4a`: outer SHA256 и все259 members
проверены локально, compressed archive10 491 579 bytes. Результат добавлен
merge commit в feature-ветку; это ещё не merge owner в develop. Transport normal
проверил prerequisite bundle и начал собственную сборку в новом runtime.
На M40 renderer проверил тот же bundle и строит отчёт. Отдельный publisher
s07-capacitance-owner-temporal-selected-normal-c2 (PID2494602) ждёт завершения
render, проверяет все cache hashes и выбирает12 PNG: overview и zoom по
измеренному пику всех сом для regrowth ClassicN0/BranchN1 при2k/20k. Он сохраняет
visual_review=false до прямого просмотра. ASan owner и transport ещё pending.

Documentation closure: Pulse feature commit
`1e7ce7a286296b16a265c49ab241c3c3f9a65193` обновляет только описание приёмки.
Его Core tree `e667aeb7f50774ca2baf16c284e9b3a04a3ad2d2` полностью совпадает
с tested f899ef024. Gitlink feature-корня обновлён после child push; работающие
jobs сохраняют свои исходные SHA и не переключаются на documentation commit.

## Временной отчёт normal C2

Production native-test renderer завершил48 complete native trials/72 actual
trial-soma pairs. Полный cache на M40 Data занимает761 345 710 bytes:2697 PNG,
2697 SVG и2697 PDF. Все8895 files в checksum inventory проверены publisher.
Compact proof `b4617156d8578d5dbe22ab9a5fa21b5bbcc9fb09` содержит12 selected PNG,
сжатые manifest/checksums и renderer receipts (2 280 244 bytes вместе).
Все17 опубликованных file hashes проверены локально; все12 original PNG
непосредственно просмотрены. Visual-review sidecar фиксирует фактическое
покрытие, hashes и ограничения; полной visual acceptance всех2697 PNG нет.

На overview видны оба реальных входных импульса и полная реакция сомы;
zoom windows сохраняют native samples при1920×960, без downsampling.
Для Classic общий выбранный arrival-window может показывать рост другой сомы,
а не её собственный максимум; отдельные пики близки к границе grid zoom.
Полный cache содержит соседние окна и обзор для восстановления контекста.
Единицы остаются явно model_units_SI_unverified. Это engineering two-pulse
probes, не новая eight-pattern classification или сходимость при default tolerances.

Служебный renderer-terminal.json ошибочно содержит png_count=0: одноразовый
job использовал shallow glob */*.png для более глубоко вложенного native-test
отчёта. Production inventory72, primary и полная hash-проверка были корректны.
Raw receipt не переписан; cache-count-correction.json отдельно связывает
рекурсивно подтверждённые2697 PNG с исходным cache SHA256SUMS hash. Временной
отчёт не требуется пересчитывать ради исправления этого счётчика.
