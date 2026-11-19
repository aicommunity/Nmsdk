# Следующая реализация: portable terminal boundary

Это рабочее уточнение открытой части этапов5/7/10, не описание готового
формата. Адресная native transaction принята на Root3c5/Pulse1d8; последующие
source retention и historical-export context реализованы, но ещё не проверены.
Общая цель этапов0–12 не заменяется этим подэтапом.

## Уже подготовленные компоненты

- NativeTerminalSourceBoundary сохраняет полный source neuron/Dataset и owned
  C-state перед transaction. Публичный доступ возвращает только DATA, без
  Restore/permit. Новый retained источник ограничен64MiB отдельно от selected
  snapshot. Исчерпание retention прекращает завершение без physical edit.
- NativeHistoricalExportBoundary имеет закрытый constructor для будущего
  NativeTerminalStateFactory. Он проверяет тот же stopped service/session,
  неизменные outcome/reason, transcript epoch/parameters и полный private
  source graph. Публичные старые exporters по-прежнему не принимают этот scope.
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
проверки совпадения actual revision/epoch. Текущий historical context принимает
только stopped/null-certificate — этот случай ещё нужно реализовать отдельно.

Warm continuation и Reset не должны стирать журнал прежних transitions и
позволять экспорту потерять происхождение. Explicit cold retarget создаёт новую
evidence scope. Нужны сохраняемый DATA journal и проверка связей между epochs;
нынешний transient event/source сам по себе эту задачу не закрывает.

Добавить explicit cold/runtime declaration и включить фактор в production
condition identity. Обновить native model/summary dispatcher, Console jobs,
Python DATA/scorer/primary transport и reporting. До этого ordinary cold JSON
сохраняют текущую семантику, версия2 не объявляется рекомендуемой по всей матрице.

Сериализация primary выполняется отдельной операцией после Calculate. Не
выгружать/перепроигрывать1GB raw journal внутри последнего тика и не копировать
service ради override epoch. Контроль памяти, nested package/content-reference
transport и bounded decoder проверить на настоящем большом N=4 primary.

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
