# Живой переход Train → финализация

Уточнение04.11: [расширенный SDK802 baseline133](Baseline133PrerequisiteReadback.ru.md) на отдельном архивном S08 fixture дал119 passed/14 failed: cold Train не получил certificate и не дошёл до queued boundary. Прежние receipts ниже сохраняются для своих исходников/входов; они не подтверждают произвольную другую cold декларацию. Подготовлен отдельный corrected cold fixture, runtime-приёмка ещё не завершена.

## Текущее состояние на 01.11.2026

Ветка `codex/timelearner-live-finalization`. Native dispatcher, явная отмена и
сохраняемый codec адресно проверены normal/ASan. Production Console Train
schema2 принят в указанной ниже normal/ASan-области; normal production
временные отчёты приняты в автоматической и selected visual области.
ASan temporal reports также проверены; selected legibility перенесена по точному совпадению PNG. Это подэтапы плана0–12; полные этапы6–8,
обязательная матрица и независимая оценка остаются открытыми.

| Область доказательства | Проверенная область | Источник |
|---|---|---|
| Первый normal live handoff |31 native +2 stopped serialization;4 payload checks,16 controls|[Normal proof](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-normal-a1/README.md)|
| Broad ASan предыдущего dispatcher |95/95 native,6 reader checks; Core cf530be, до Cancel/codec|[ASan proof](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-asan-a2/README.md)|
| Native explicit Cancel, normal |8/8 native,8 reader checks,48 malformed cancellation controls|[Cancel normal](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-cancel-normal-a1/README.md)|
| Cancel + persisted codec, ASan |9/9 native,8 reader checks; четыре codec plans и32 malformed declarations, Core019e5d1|[Cancel/codec ASan](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-cancel-codec-asan-a1/README.md)|
| Production Console schema2, normal |14 operations;1 codec test;3 original reader checks и4-check follow-up, включающий прежние проверки|[Production normal](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-normal-a2/README.md)|
| Production Console schema2, ASan |14 operations;1 codec;3 original и4-check complete reader, Core019e5d1|[Production ASan](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-asan-a1/README.md)|
| Production normal temporal reports |14 reports,3 checks;10 selected PNG просмотрены1920×960; весь cache вручную не принят|[Production visual](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-visual-normal-a1/README.md)|
| Production ASan temporal reports |14 reports,3 checks;10 точных ссылок на просмотренные normal PNG без дублирования|[Production ASan visual](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-visual-asan-a1/README.md)|
| Native integration temporal reports |16 reports,3 checks; восемь выбранных изображений просмотрены1920×960|[Visual proof](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-visual-normal-a2/README.md)|

Числа checks разных серий перекрываются и не складываются в число независимых
экспериментов. ASan leak detection выключен. Актуальные jobs и точные source
closures приведены в [CurrentStatus](CurrentStatus-2026-11-01.ru.md).

## Runtime-контракт

`ConfigureNativeFinalization(NativeLiveFinalizationSpec)` вызывается до Train.
Он задаёт implementation ID, conversion и полный PostTune design: фиксированный
порог либо реальную grid-калибровку. Конфигурирование не строит модель и не
выполняет Calculate. Декларация сохраняется отдельным codec и Console job2;
свойство `ControllerConfiguration` по-прежнему описывает cold training.
После XML Load runtime-план следует задать явно до нового обучения.
Отсутствие плана сохраняет прежние optional-mode guards.

Общая реализация `TimeLearner/NativeLiveFinalization.h` используется Classic
и Branch. Математическая цель CapturedPerInput не меняется.

```text
native AfterChildren:
    consume actual completed Train observation
    on Finished: capture immutable Solo boundary before closing request
    no completed certificate -> stopped diagnostic, no recognition import
    otherwise queue finalization and retain active request

next native BeforeChildren:
    validate controls, bindings, session and full source archive
    privately convert immutable Solo state
    import through native owner/storage path with original boundary
    Build / Init and effective package readback
    begin owned PostTune

ordinary ticks:
    owned PostTune advances before children
    native scheduler calculates physical children once
    collect phase report and execution separately from Train outcome
```

Ни dispatcher, ни Console не вызывают вложенный Calculate. Булевы
Build/Reset/Calculate остаются true и не распространяют ошибки; Init — void.
Build/Init/Reset импорта проходят штатный lifecycle; depth scopes отличают
их от внешнего прерывания. Copy/Alloc не используются как динамический checkpoint.

CalculateMode0 закрывает локальный Need после объявленной финализации.
Connected provider не записывается; его true требуется до старта.
CalculateMode1 сохраняет внешнее управление. Снятие запроса между capture
и entry запрещает импорт. Внешние Reset/Default/UnInit/Build прерывают scope.
`failed/recovery_required` блокируют расчёт детей штатным ForceSkip.
`completed` означает терминальное выполнение фазы, а не Exact, calibrated,
separable или успешную классификацию.

Проверяются действующие mode/metric/policy, weight threshold, применимые
canonical floor/last и synthetic passes. До Train проверяются target hash,
размерность trials, уникальные IDs, обе метки для каждой reset policy,
полное окно, sample budget и единая частота дерева. Перед PostTune проверяется
фактическая конечная физика. Включённые C-trim, target-only calibration и
legacy nonseparable fallback в новом пути пока отклоняются явно.
Target-reference и Branch parallel-peak не заменяются target/foil grid.

## Явная отмена

`CancelNativeLiveFinalization(reason)` вызывается между тиками и идемпотентен.

| Момент | Сохраняемый результат |
|---|---|
| До старта |cancelled, boundary отсутствует; шаблонный Train package не создаётся|
| Активный Train |штатный ExternalStop закрывает пробу и evidence sink; stopped diagnostic без сертификата|
| Queued boundary |completed Solo сохраняется, conversion/import не выполняются|
| PostTune |общий transactional cancel/rollback; terminal live execution сохраняет отдельный phase status cancelled|

Cancel не продвигает время и не записывает connected Need. Оставшийся true
provider не запускает cancelled declaration повторно; новый запуск требует
новой декларации. До entry физические дети продолжают штатный расчёт.
Отменённая PostTune recognition-модель может существовать после rollback,
но Console не выдаёт её как обычный итоговый Test package.

## Сохраняемый план

`EncodeNativeLiveFinalizationSpec` / `DecodeNativeLiveFinalizationSpec` используют
подписанный `native_live_finalization_plan`, schema1:

- implementation_id;
- conversion через штатный recognition codec;
- post_tune controlsV3, включая nullable weight_probe_threshold;
- trials, thresholds, maximum_calibration_candidates;
- confirmation с protocol, partition, attempt, clock и criterion;
- sha256 канонического содержимого.

Decoder проверяет типы, лимиты, nested codecs и точное обратное представление,
включая отсутствие лишних полей и корректный digest. Он не создаёт Rdk-объекты
и не меняет физику. Effective preflight после построения модели остаётся
обязательным. Это декларация будущей фазы, не checkpoint динамики/контроллера.
Mid-probe resume не поддерживается.

## Production Console и worker

```text
python -m Scripts.StructTrain.TimeLearner train JOB.json --runtime-manifest RUNTIME.json --wall-seconds 1800 --output NEW_RUN
```

Schema1 сохраняет прежние поля и поведение. Schema2 добавляет обязательный
finalization_plan; optional_modes.post_train_tuning=true, C-trim=0 и
AutoCalibrateFixedLTZThreshold=false. Публичные параметры задаются до Build,
план сверяется с их эффективным readback.

Console фиксирует Solo и native summary до следующего импорта. Пересозданный
controller/граф не используются для восстановления старого Train результата.
Полный `finalization.json` содержит source outcome, conversion, реальные
PostTune/grid/confirmation данные и owned execution clock.

Execution schema2 разделяет training_started, completed_boundary,
finalization_status и recognition_available. Если boundary не возникла,
package_path/sha/model_revision/training_outcome равны null, learned/stopped
шаблонов нет. recognition-model.json создаётся только для разрешённого
нормального terminal outcome. Доступность модели не доказывает сходимость
или распознавание.

При cancel.request или общем tick budget вызывается native Cancel. Completed
Solo может сохраниться, но recognition_available=false. Точное содержимое
cancel.request сохраняется. Внешний лимит отмечается в execution; native
training_outcome при этом может быть external_stop, а не внутренний
budget_exhausted алгоритма.

Python проверяет source CSV/model/summary, immutable plan, public controls,
каждый owned tick от entry до конца execution и итоговый effective package.
Typed exit2 schema2 позволяет анализировать partial evidence при том же
process/runtime ownership audit; process_error не превращается в completed.
Историческая schema1 nonzero manifest semantics сохранена.

Frozen evaluate вызывается отдельно с genuine новым Train source. Его model
hash неизменен; same-matrix не становится independent Test. Общий bundle
verifier принимает native pipeline manifests: cold Train требует source=null,
export/evaluate — реально включённый source artifact. Это проверка inclusion/
bytes после production audit, не отдельная научная или origin-аттестация.

## Production временные отчёты

```text
python -m Scripts.StructTrain.TimeLearner report RUN/run-manifest.json --format pipeline-run --output NEW_REPORT
```

Portable manifest задаёт полную source closure; overlays model/trace/source и
external inventory запрещены. Train schema1/2 и отдельный evaluate читаются
непосредственно. Writer ordinals непрерывны и числовые, измеренное native время
возрастает. Partial Train не получает recognition-график. Все soma channels,
реальные входы и отсчёты сохраняются; overview и zoom1920×960, минимум8px/tick
на zoom, без downsampling. SI units остаются непроверенными.

Normal production14-report rendering и3 report checks завершены на M40:
93 training и42 recognition trial-soma pairs,543 неизменённых source files.
Full cache4119files/291766358bytes хранится на Data; Git содержит272 metadata
members/190348bytes и10 выбранных PNG/1500834bytes. Эти10 непосредственно
просмотрены1920×960, scope/ограничения записаны в SELECTED_VISUAL_REVIEW.json.
Полная ручная приёмка cache отсутствует. ASan14-report rendering выполнен
на собственных primary из Git:3 checks,521 unchanged source files,93 training
и42 recognition pairs. Все10 выбранных ASan PNG побайтно совпали с directly
reviewed normal images; перенесена только их читаемость, новый прямой просмотр
или full-cache acceptance не заявляются. Git содержит272 metadata members/
190708bytes и точные normal PNG references, без новых копий изображений. Интеграционный `native-live-finalization` формат остаётся
отдельным адаптером старых control records с обязательным primary inventory.

## Научная граница и остаток

Четыре production cold Train сохранили SearchUnresolved. Fixed выбрал веса;
grid восстановил source после unresolved search. Во всех четырёх реальных
frozen same-matrix target/foil парах TP0/FP0/FN1/TN1. Это молчание с пропуском
target, не успешная классификация. Двухпаттерновые engineering controls не
воспроизводят и не опровергают августовские визуальные4/8–6/8.

Открыты target-reference/parallel-peak,
optional C-trim, independent frozen evaluation и полные normalization/model/
profile/frequency/dimension/lifecycle матрицы. Версия2 не рекомендуется для
всей матрицы до их приёмки. Native integrated gate95 относится к более раннему
Core cf530be; новые Cancel/codec проверены отдельно на Core019e5d1.

Исторические ошибки auxiliary-glob supervisor, reader path/start_ticks,
лексикографической сортировки trials, standalone codec output directory и
первого packaging gate сохранены в соответствующих proof packages. Их статусы
не переписаны. Подробная хронология: [CurrentStatus](CurrentStatus-2026-11-01.ru.md).
