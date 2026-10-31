# Живой переход Train → финализация

Реализация в ветке `codex/timelearner-live-finalization`; адресная normal
приёмка и первичная ASan пара получены, широкая ASan/visual приёмка открыта. Это продолжение полного плана 0–12,
а не закрытие этапов 6–8 или обязательной матрицы.

`ConfigureNativeFinalization(NativeLiveFinalizationSpec)` задаёт неизменяемую
runtime-декларацию до старта Train: implementation ID, conversion и полный
PostTune design с фиксированным порогом либо реальной grid-калибровкой.
Само конфигурирование не строит модель и не выполняет Calculate. Декларация
не является checkpoint и пока не сериализуется свойством ControllerConfiguration.
После Load её необходимо явно задать; отсутствие декларации сохраняет прежние
guards optional modes и прежнее завершение Train.

Общая реализация `TimeLearner/NativeLiveFinalization.h` используется обоими
learner. Структурные действия разрешены только до штатного расчёта детей:

```text
native AfterChildren:
    training service consumes the completed observation
    if Finished and live finalization was declared:
        capture immutable boundary before closing the request
        if no completed certificate: stopped diagnostic, no recognition import
        else: queue finalization; retain active request

next native BeforeChildren:
    validate original controls, bindings, session and full source archive
    privately convert the captured Solo state
    import with the original boundary through the native owner path
    Build / Init; verify effective recognition package
    begin native owned PostTune

ordinary native ticks:
    owned PostTune advances before children
    scheduler calculates children once
    collect terminal PostTune report and execution separately from training outcome
```

Восстановление finished-состояния публичным Need=false→true не используется.
CalculateMode0 сохраняет Need до конца объявленной финализации, после чего
закрывает только локальный запрос. Подключённый provider никогда не записывается
dispatcher; его true требуется до старта. CalculateMode1 оставляет внешнее
управление запросом. Снятие внешнего запроса между capture и entry запрещает
импорт. Reset/Default/UnInit и внешняя перестройка прерывают queued/running scope;
внутренние lifecycle-вызовы импорта и PostTune отделены depth scopes.

План сверяется с действующими public mode/metric/policy, измерительным порогом,
действующими canonical floor/last и числом synthetic passes. Входные trials
объявлены явно, проверяются до обучения: размерность, target hash, уникальные
trial IDs, обе метки для каждой reset policy, полное окно и sample budget.
PostTune повторно проверяет фактическую конечную физику перед изменениями.
Неподдержанные target-only AutoCalibrateFixedLTZThreshold, C-trim и legacy
nonseparable fallback отклоняются явно. Target-reference и Branch legacy
parallel-peak calibration не подменяются target/foil grid; их включение в живую
последовательность остаётся отдельной обязательной работой.

`NativeLiveFinalizationReport()` содержит подписанные declaration, request,
boundary, capture/entry time и отчёты PostTune. `completed` означает терминальное
выполнение финализации; её собственный результат хранится отдельно. Оно не
означает Exact, calibrated, separable или успешную классификацию.
`failed/recovery_required` запрещают дальнейший расчёт детей через штатный
ForceSkipComponentCalculation. Булевы Build/Reset/Calculate не используются
для распространения ошибок. Dynamic checkpoint и mid-probe resume отсутствуют.

Новые native fixtures холодно строят модель из исходного физического профиля,
сохраняют реальные Train CSV/packets, ждут capture естественного Finished и
выполняют PostTune на обычных тиках. Проверяются fixed/calibrated policies,
local/connected request, stop без сертификата и control/reset/stop между capture
и entry. Последующий frozen replay той же target/foil матрицы проверяет
неизменность модели; это не независимый научный Test. До терминальных receipts
и проверки доступных в Git primary эти сценарии не считаются пройденными.

Остаются production job/CLI declaration, независимый evidence reader живого
перехода, all-pattern temporal reports, target-reference/parallel-peak фазы,
вся физическая/режимная матрица и independent frozen evaluation.

Первый проверяемый source: root6659caaf5 / PulseLib69eba48; normal PID2180613,
ASan PID1251, readbacks s08-native-live-finalization-{normal,asan}-a1. Отдельный
reader добавлен в root761c1f7c5; его runtime-приёмка ожидается. Следующая версия
PulseLibcf530be дополнительно завершает live state при ошибке до Start и
проверяет uniform frequency до Train; добавлены invalid-design/multirate fixtures.
Она не подменяет source уже работающего ASan a1. После терминального normal a1
и независимого reader запущена normal a2 на root5afe5b963 / PulseLibcf530be,
31 case; результаты пока ожидаются. Первый normal native набор прошёл 6/6,
reader — 2/2 без skips. Его supervisor status1 сохранён: ошибочный glob
считал вспомогательные JSON вместе с control records. Native XML/process
receipt и runtime equality проверены отдельно; это не полный accepted gate.

## Адресный результат и независимая проверка

Normal:31/31 и два stopped-serialization follow-ups2/2; полный reader4/4
проверяет16 live records,32+60 повреждённых controls, реальные Train CSV,
completed/stopped summaries и immutable boundary.
[Compact proof](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-normal-a1/README.md)
содержит599 members /1943492 compressed bytes; все hashes проверены после merge.
Source snapshots перечислены отдельно: исходные31 cases root5afe5b963, два
дополнения первичных данных rootf0cf989cb, один PulseLib corecf530be.
Composed view не подменяет историю источников. Полные исходные данные сохранены.

Оба fixed controls выбирают веса; оба grid controls завершаются SearchUnresolved
с восстановлением source. Во всех четырёх frozen replay target иfoil молчат,
Train остаётся SearchUnresolved. Functional pipeline success не является
успешной классификацией. Первые ASan6/6 и reader2/2 подтверждены, broad95-case
ASan gate ещё работает. Полная матрица, production CLI, independent Test
и временные отчёты нового handoff остаются открытыми.

Поддерживаемый receipt checker:
`python -m Scripts.StructTrain.TimeLearner.native_execution_gate --spec SPEC --root RUN --runtime-after SNAPSHOT`.
Декларативные coverage contracts находятся в `Specifications/native-live-finalization-*.json`.
Он сверяет точные test IDs, полные имена control files, process/runtime/loader
receipts и явную supervisor policy. Корректность payload проверяют отдельные
readers; origin JSON и полный lifetime loader closure этот checker не удостоверяет.
Initial supervisor failure сохраняется даже при successful native receipts.

## Временные отчёты и CLI: приёмка выполняется

`live_finalization_reports` проверяет control и все нужные primary по inventory,
затем отображает все записанные Train probes, измеренные PostTune/calibration
матрицы и frozen replay. Остановка показывает только реальные partial samples;
отказ до первой пробы не создаёт кривых или шаблонного recognition Test.
PNG1920×960, полные samples, фактический общий вход, overview и подробные zooms.
Train probes имеют общие per-soma Y limits; неизвестные spike responses не
заменяются отсутствием спайков. Единицы SI остаются явно непроверенными.

Первый renderer root3d679ec7f построил16 отчётов:213 training trial-soma pairs
и42 recognition pairs,6928 cache files /447227287 bytes,516.173 s. Три проверки
прошли и931 source files не изменились, но отдельная review обнаружила
лексикографический порядок trial_1,trial_10,...,trial_2 в10 training reports.
Этот cache не принят по требованию хронологии; прежний status0 не переписан.
`chronology-review.json` хранит фактические begin times и причину отказа.

Rootd16237f83 проверяет непрерывные числовые writer ordinals и возрастающее
native время, отвергает пропущенную промежуточную пробу до output. Сейчас
выполняется повторное построение normal visual-a2, PID53240, на тех же
неизменяемых первичных данных; численное обучение не повторяется. Первичный
cache/data и numeric runtime работающего ASan не обновляются.

Корневой CLI (пока для native integration-control artifacts этого формата):

```text
python -m Scripts.StructTrain.TimeLearner analyze CONTROL.json --format native-live-finalization --primary-inventory INVENTORY.json
python -m Scripts.StructTrain.TimeLearner report CONTROL.json --format native-live-finalization --primary-inventory INVENTORY.json --output NEW_REPORT
```

Нужны распакованные primary и inventory/composition со связанными SHA/размерами.
Посторонние model/trace overlays запрещены. CLI root10032be3c прошёл2/2 на
реальном invalid-design control: analysis, no-data report, missing inventory
и model overlay; primary hashes не изменились, новых numeric runs0.
Это не production Train-job declaration и не отдельный научный эксперимент.

## Явная отмена: реализация, проверка ожидается

`CancelNativeLiveFinalization(reason)` вызывается между тиками. При активном
Train используется штатный ExternalStop, закрывающий текущую пробу и передающий
частичные samples в evidence sink. Полученное stopped diagnostic состояние не
превращается в recognition. До старта и в queued boundary отмена не импортирует
модель. Отмена внутри PostTune использует общий transactional cancel/rollback;
терминальный live execution при этом сохраняет отдельный PostTune status cancelled.

Отмена не вызывает Calculate, не увеличивает model time и не записывает
подключённый внешний IsNeedToTrain. Cancelled declaration не запускается снова
при оставшемся true provider; повторный Cancel не изменяет terminal report.
Физические дочерние компоненты продолжают рассчитываться штатным scheduler.
До старта boundary отсутствует: шаблонное состояние не выдаётся за Train result.

Добавлены восемь native controls: Classic/Branch × armed/training/queued/PostTune.
Это пока непроверенная реализация: серверные сборки и runtime receipts ожидаются.
Production job schema2 остаётся отдельной незавершённой задачей.
