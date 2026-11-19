# Следующая реализация: portable terminal boundary

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

Сначала новые14 source readback assertions плюс прежние44 regressions;
затем actual export/import/re-export и fresh-process frozen response. Негативные
проверки: потерянный узел/связь/C0, чужие trial/anchor, смешанные epoch, испорченный
primary, подмена actual graph, replay live authority, неуспешный rollback.
Проверять native scheduler/lifecycle, а не возвращаемые bool.

После приёмки — same-budget cold Classic/Branch A/B и actual frozen8 с полными
окнами и читаемыми Soma/input графиками. Tolerances, CapturedPerInput, assigned
pulse Train и whole-response Test сохраняются. Положительный результат8/8 не
является условием рефакторинга; валидные отрицательные/unresolved результаты
публикуются с теми же первичными данными и provenance.
