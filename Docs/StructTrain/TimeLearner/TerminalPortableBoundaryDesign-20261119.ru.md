# Следующая реализация: portable terminal boundary

Рабочее продолжение cold/runtime integration: Pulse codec cold9 явно хранит
terminal_selection поверх полной schema1–8 и отдельный terminal_base_schema_version,
сохраняя вложенный base_schema_version. Подготовлены2 native codec tests
(16 исходных wires) и8 configured owner entry controls: старт через штатный
Calculate/flag, readback бюджета7.25 и package8 roundtrip. Это engineering
completed controls с sync.2, не научная сходимость при.02 и не проверка реально
выполненного restore. Python4 читает эти реальные wires/DATA; он ещё не запускался.
Текущая A5 использует прежний Pulse13f и не проверяет новый codec.
Console execution/publication и native_pipeline_worker ещё не согласованы с
cold9; runner явно отклоняет такой Train до дорогого запуска. Эта открытая
часть должна быть завершена перед новым scientific cold A/B.

A4 остановилась при сборке теста: публичный helper ошибочно вызвал protected
NativeProbeModelBindings. Production PulseLib собрана, но выполнено0/60 native
cases, все группы закрыты и failure primary опубликован. Ошибочное обращение
удалено без расширения API; публичная trim=0 и end-to-end проверки сохранены.
Новая проверка разделяет существующий corpus60 и дополнительный actual-restore8
на два объявленных leaf gates. Полная приёмка требует оба; успех первого не
закрывает второй и не является завершением исходного плана.

Подготовлены ещё8 native scenarios NativeActualCompositeTerminalRestore:
protocol4/5 × Classic/Branch × N0/N1. Они должны получить настоящую измеренную
candidate/anchor pair, изменить L2→L3 и исчерпать заранее объявленный model-time
budget внутри следующей группы. Budget вычислен из числа raw probes, штатной
длительности окна и ограниченных scheduler gaps; wall budget не используется
как подмена model clock. Требуются source/selected/actual graph и epoch,
одна charged restore transaction, schema8/summary9 roundtrip, неизменный native
burst response и новая consumed warm measurement после импорта. Отдельные
precondition/warm-start artifacts сохраняются до утверждений, чтобы отличать
недостигнутый сценарий от дефекта. Эти8 cases ещё не выполнялись и не входят
в активную A4/60. Восстановление C0/heterogeneous growth имеет отдельный остаток.

Уточнение A3: четыре protocol4 stopped warm cases отклонены при повторном
экспорте с terminal_selected_composite_measurement_missing. Warm Start оставлял
только captured reference groups и удалял candidate/anchor primary старого
terminal journal. Рабочее исправление сохраняет требуемое объединение и проверяет
его byte budget до изменения активной попытки. Journal validation не ослабляется.
Все восемь composite warm controls усилены: перед stop должен быть принят хотя
бы один настоящий logical measurement новой попытки. Исправление ещё не принято
на сервере. A3 закрыта:50 PASS/10 FAIL, все60 cases выполнены;1123 primary
members и17 log aliases опубликованы во внешнем архиве M40. Исходный A3 runtime
не изменён. Кроме4 protocol4 и2 C0 отказов,4 plain completed cases обнаружили
ошибочный snapshot guard: CapApplyPending отвергался даже при trim=0.
Guard согласован с NativeProbeModelBindings/scheduler без сброса флага или
изменения параметров. Все исправления требуют нового native gate.

Ещё два A3 C0 transport cases не достигли проверяемого unmeasured edit:
10s wall budget истёк после capture и первого search input, до anchor.
Следующая постановка объявляет30s только для двух C0 fixtures; остальные
deadline fixtures сохраняют10s. Model-time20s, edit budget, физика, научные
допуски и бюджеты реальных Train не меняются. Precondition schema2 сохраняет
elapsed wall time, число валидных raw trials/измеренных кандидатов и наличие
selected boundary. Сценарий всё ещё обязан наблюдать настоящий edit, дождаться
реального deadline и проверить полный native restore. Более долгий fixture
budget не является научным улучшением обучения.

Это рабочее уточнение открытой части этапов5/7/10, не приёмка готового формата.
Адресная native transaction принята на Root3c5/Pulse1d8. Factory schema8,
event2 и summary9 реализованы; первая сборка A1 остановилась до тестов на
сравнении Qt JSON типов. Исправленная комбинация Root3916cf6da8157cfbe84ef0f54a1a446824d70e0a /
Pulsec84a1c1e864786660d7626d2e577fb3b83eeb67b проверяется отдельно в A2.
Общая цель этапов0–12 не заменяется этим подэтапом.

## Уже подготовленные компоненты

- NativeTerminalSourceBoundary сохраняет полный source neuron/Dataset и owned
  C-state перед transaction. Публичный доступ возвращает только DATA, без
  Restore/permit. Новый retained источник ограничен64MiB отдельно от selected
  snapshot. Исчерпание retention прекращает завершение без physical edit.
- NativeHistoricalExportBoundary имеет закрытый constructor для
  NativeTerminalStateFactory. Он проверяет тот же stopped service/session,
  неизменные outcome/reason, transcript epoch/parameters и полный private
  source graph. Terminal scope направляется в новый factory, а прежний формат
  используется только как явно вложенная историческая граница.
- Historical export paths подготовлены для plain protocol3, composite4 и
  candidate-window5, включая recovery family. Они сохраняют исходные проверки
  measurement proof, native graph, storage images и C0; epoch берётся из source
  context. Controller и большой raw sample journal не копируются.

## Требуемый полный data path

```text
finished native service at a closed boundary
    read immutable pre-transaction source and selected/actual identities
    construct a PRIVATE native source owner from retained snapshots
    validate source graph, Dataset, frequency, parameters and C-state
    mint read-only historical export context
    export/replay old stopped evidence against source revision/epoch
    export actual graph/Dataset/C-state against physical revision/epoch
    validate selected trial/anchor and full physical bindings
    publish one versioned envelope and matching summary
```

Private owner можно создавать обычным новым UNet с установленными storage,
environment и frequency; Default относится только к свежему пустому owner.
Дети создаются native ImportDatasetSnapshot/ImportPhysicalGraphForEdit с Init
и полным readback. Нельзя делать Default полученного проверенного образа,
Build/Reset live learner, nested Calculate или изменять физику shared prototype.
Снимки доступны через read-only NeuronSnapshot/DatasetSnapshot.

Предпочтительный новый learned-state envelope8 содержит обычный исторический
package как явно historical_state, actual model archive/Dataset/C-state,
terminal policy/event/journal, actual revision/epoch/parameters, исходы,
implementation/session/configuration bindings и общий digest. Старые schemas
не получают нового смысла. Формат и список полей должны быть закрытыми.

При import сначала штатно replay historical package в его source revision/epoch;
отдельно проверить event и фактически импортированный actual graph. Финальные
groups истории нельзя перепривязать к новой epoch. Для restored модели
certificate=null до новой all-input verification. Импорт возвращает Finished
DATA без search traversal, executor callbacks, token или старого actor.
Повторный export/import должен сохранять переход и не выполнять его ещё раз.

Событие связывает реально принятое candidate/anchor measurement, input index,
full native identity, параметры/C0, source и actual epoch, charge/rollback.
Проверять accepted complete primary через существующие validators. Наличие
измеренной точки не доказывает глобальную оптимальность или сходимость.

## Полнота перед включением в эксперименты

Поддержать обе topology и все три существующих protocol families, N0/N1,
heterogeneous/dormant C-state, successful/rollback/no-edit transitions.
Не ограничивать формат только удобным успешным restore. Отдельные обязательные
случаи: policy включена, но reference capture остановлена до selection;
нет transition; завершилось Exact без необходимости изменения графа; external
stop; interrupted/invalid outcomes; недостаток reservation/retention.
Сертификат прежнего unchanged Exact можно сохранить только после строгой
проверки совпадения actual revision/epoch. Historical context теперь принимает
unchanged certified scope; новые4 composite cases проверяют его отдельно с
явно инженерным sync0.2. Они не доказывают научную сходимость при sync0.02.

Warm continuation и Reset не должны стирать журнал прежних transitions и
позволять экспорту потерять происхождение. Explicit cold retarget создаёт новую
evidence scope. Реализован DATA journal до4096 записей; его warm/re-export
проверки ещё не приняты. Aggregate byte budget и сохранность всех dormant C0
после роста и отката к более ранней геометрии остаются отдельными проверками.

Добавить explicit cold/runtime declaration и включить фактор в production
condition identity. Обновить native model/summary dispatcher, Console jobs,
Python DATA/scorer/primary transport и reporting. До этого ordinary cold JSON
сохраняют текущую семантику, версия2 не объявляется рекомендуемой по всей матрице.

Сериализация primary выполняется отдельной операцией после Calculate. Не
выгружать/перепроигрывать1GB raw journal внутри последнего тика и не копировать
service ради override epoch. Контроль памяти, nested package/content-reference
transport и bounded decoder проверить на настоящем большом N=4 primary.

Summary9 описывает actual revision/physical epoch и terminal journal. В рабочей
ветке добавлен historical_summary: прежняя source summary на transcript epoch,
со ссылками на reference/candidate trials, C0 witnesses и search counters.
DATA reader terminal_package_evidence отдельно проверяет actual graph и
вложенный historical_state, используя исходные validators и реальные CSV.
Эти изменения ещё требуют серверной проверки. Нельзя подставлять в прежний scorer
actual summary с новой epoch или достраивать отсутствующие measurement proofs.
Конкретные места: ProbeEvidenceJson/NativeCompositeLearnedState в PulseLib;
learned_evidence, stopped_evidence, composite_package_evidence, native_evidence,
native_pipeline_worker и recognition_evidence в корневом пакете. Unknown schema
должна оставаться отказом до согласованного обновления этих путей.

Native CheckStoppedPackets явно разрешает warm references из прежней попытки.
Python stopped_evidence теперь различает observed текущей попытки и retained
reference packets, требуя реальные CSV для точного объединения обоих наборов.
Версии аудита6/7 отмечают такой retained-reference случай; исходные4/5 и их
результаты не переименовываются. Никаких отсутствующих observations или
сертификатов не достраивается. Полная pipeline/primary интеграция всё ещё открыта.

## Проверки и следующий научный опыт

После исходного Root d9b9df7 для A6 отдельно добавлена Console publication8:
publisher публикует неизменённый historical measurement archive, но receipt
удерживает весь actual outer package8. Проверяются оба digest и общие
source metadata; history1–7, рекурсивный8 запрещён. Старые publication1–7
сохраняют wire. Native assertions проверяют точное совпадение опубликованного
index с embedded source и запрет подстановки history/изменённого actual package
в receipt. Эта правка не входит в уже работающий A6 и ещё не собрана.
Execution6, Python execution audit и фактический cold Console Train/Test
остаются необходимыми; cold9 pipeline guard пока сохраняется.

Следующий source-only срез добавляет execution6 с отдельными terminal_boundary,
source_measurements и native_execution_counts. Ни actual модель, ни её epoch не
подставляются в старые execution3/4/5. Общий pipeline auditor использует прежние
package/scorer readers, затем проверяет новые связи и внешние primary. Snapshot
terminal8 composite теперь проверяет и переносит реальные source CSV; embedded
blobs не скрывают отсутствующий внешний файл. Launch guard cold9 остаётся в
run_job(train), а DATA audit/preflight способны проверять новый формат.

Подготовлен worker-only Console integration test:16 N2 cases (completed8 и
реальное восстановление8), настоящие public preflight/Train, полный source/actual
аудит, export либо diagnostic transfer и frozen probes, отрицательные проверки
re-signed epoch/policy и отсутствующего CSV. Native fixtures экспортируют
декларации cold9-job.json с исходной геометрией и storage images; обученная
модель не используется как начальное состояние. У completed cases sync=.2 —
только engineering transport fixture; actual restore cases сохраняют .02.
Этот новый код не входит в A6 и ещё не проходил серверную сборку/проверку.
Live finalization/posttune с cold9 пока отклоняется явно, без имитации поддержки.

Actual8 на неизменном A5 runtime отделены от original60: исходный worker
остановился после59/60, поэтому новый owned gate выполняет все8 самостоятельно.
Runtime/native source не обновляются. Первые два Fixed N0 случая подтвердили
отказ imported epoch после настоящего восстановления L3→L2. Исправление
принимает только тот typed historical proof, который установлен actual owner,
и проверяет source/actual revision+epoch последнего validated terminal event.
Исторические measurements не перепривязываются; новый actor получает actual
граф и обычную native owner lease. Новая серверная приёмка ещё требуется.

Cold configuration9 и actual C0 warm-admission исправление включаются в
следующий native SDK gate с78 cases: прежние60, actual8, codec2 и configured
entry8. Все cases объявляются в одной leaf, чтобы assertion failure одного
случая не скрывал остальные. Python readers проверяются на фактическом corpus
отдельно; Console execution/publication integration остаётся открытой.

Сначала новые14 source readback assertions плюс прежние44 regressions;
затем actual export/import/re-export и fresh-process frozen response. Негативные
проверки: потерянный узел/связь/C0, чужие trial/anchor, смешанные epoch, испорченный
primary, подмена actual graph, replay live authority, неуспешный rollback.
Проверять native scheduler/lifecycle, а не возвращаемые bool.

Текущая A3 серия60 и Python fixture-reader охватывают28 исходных boundaries,
12 plain и8 composite warm Start/Stop exports. Это не доказательство полноценного
продолжения поиска. Дополнительно нужны protocol4/5 × Classic/Branch × N0/N1
с реально изменённым неизмеренным кандидатом при model/wall budget stop,
native restore выбранного другого графа, переносом и frozen response. Проверять
независимый source/selected/actual readback, charged epoch и сохранность primary;
не считать fixed-geometry already_current эквивалентом такого transition.

После приёмки — same-budget cold Classic/Branch A/B и actual frozen8 с полными
окнами и читаемыми Soma/input графиками. Tolerances, CapturedPerInput, assigned
pulse Train и whole-response Test сохраняются. Положительный результат8/8 не
является условием рефакторинга; валидные отрицательные/unresolved результаты
публикуются с теми же первичными данными и provenance.
