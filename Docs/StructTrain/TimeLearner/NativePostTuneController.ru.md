# Native PostTune: измерительный контроллер

Рабочая реализация `NativePostTuneTransaction<Owner>` добавлена отдельно от
механического выделения guards. Normal root
`44a1598af2cfdd2fa1703d5ea70f8f1e8beabc9b` / PulseLib
`c8a1995019be944acb0cbfd7f40d6ff7cba111c9` прошёл 10/10 native cases
(501.475 s) и 19/19 independent checks (192.578 s), без skips.
[Lossless primary bundle](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-controller-normal-a2/README.md)
включает все 24 parent reports, raw matrices, модели и исходные неуспешные попытки.
Это адресная приёмка N1/2000 Гц/двух входов, не полная mode/profile matrix.
Этап 8 и исходный план 0–12 остаются открытыми.

Дополнительно N0 normal на source `fe45166a132a97aefcd62318125604bb066b57ff`
прошёл два реальных native cases Classic/Branch (459.529 s) и 12 независимых
evidence checks (157.913 s), без skips. Все 24 controls сохранены в
[N0 primary bundle](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-controller-n0-normal-a1/README.md).
Целевая физика, допуски, full-matrix threshold proposal и fresh confirmation
не менялись ради прохождения N0. ASan N0 запущен отдельно; пока не принят.

Контроллер действует между native ticks и не вызывает Calculate. Он принимает
полностью импортированную исходную recognition-модель с conversion spec schema 1.
Для каждого кандидата заново выводит полную модель из immutable solo и исходного
conversion spec, применяя typed PostTune edit. Никакой реконструкции с fallback C,
изменения storage prototype, повторного parallel scaling или XML-overlay нет.

Алгоритм:

```text
validate source model, complete labelled trial design, metric and budgets
create initial candidate:
  Off/KeepDone: inherited recognition Rs
  CanonRmin: declared floor except last, declared last on reference input
  FlatLastR: declared last on all inputs
  SearchSynthetic: same declared canonical seed
for each allowed proposal:
  derive candidate privately; reject illegal physics with an explicit reason
  deduplicate actual effective model identity after individual clipping
  import candidate through native lifecycle at an idle boundary
  present the entire declared target/foil matrix in its declared order
  validate every actual observation against its independent request
  gap = minimum(target trial peaks) - maximum(foil trial peaks)
  keep the best actually measured gap; ties retain the earlier candidate
  for SearchSynthetic propose coordinate factors 0.5, 1, 2 from the best measured
    effective Rs; default 12 passes, declared proposal/recording limits
if no measured gap exceeds declared minimum:
  restore the complete original recognition state
  return SearchUnresolved or BudgetExhausted, never PhysicalInfeasible
otherwise:
  rebuild the selected candidate from its immutable archive
  execute the existing real threshold grid and fresh confirmation
  commit the resulting native calibrated state only on confirmed success
  otherwise restore the complete original recognition state
```

Metric Auto означает LTZone.Potential для Classic и одновременную сумму
фактических соматических потенциалов для Branch. LTZone и SomaSum можно выбрать
явно. Максимум начинается с −∞, не с нулевого rest state. Все значения должны
быть конечны, окна — полны; отсутствующий пик/данные не заменяются прогнозом.
Это измерения полных пачек, не single-pulse characterization.

Положительный gap — лишь основание проверить выбранные веса калибровкой.
Кандидаты измеряются при реальном действующем пороге; новый порог затем
проверяется физическими прогонами с его собственным обратным влиянием на динамику.
Никакого offline threshold sweep по единственному spiking CSV нет. Успешная
калибровка не повышает исходный training outcome до Exact и не доказывает
разделимость независимой матрицы. Полный weight-search и threshold-grid provenance
хранится в transaction report; schema-1 calibrated package не объявляется
доказательством оптимального выбора по всей истории.

Typed fixed-mode candidates сохраняются как раньше. Для управления полным поиском
введён отдельный `NativePostTuneControllerMode::SearchSynthetic`; его нельзя
смешивать с `NativePostTuneMode::SearchSyntheticCandidate`, означающим один
неизмеренный вектор в model archive.

Передача управления threshold-контроллеру использует общий guarded scope:
обновления lifecycle/context после разрешённых native imports видят оба уровня.
Проверяется соответствие owner и implementation ID. Отмена родителя отменяет
только собственную пробу или поручает отмену дочернему контроллеру. Чужой trial,
Reset, смена частоты/clock или идентичный внешний import не дают права откатывать
чужое состояние: результат RecoveryRequired сохраняет его для явного восстановления.

Лимиты: максимум 4096 предложений и 128 passes; default 256 предложений и 12 passes.
Дубликаты/отклонённые предложения расходуют proposal budget, не считаются
независимыми опытами. Default stored-sample budget 2 млн ограничивает weight
observations и заранее проверяет верхнюю границу grid+fresh-confirmation.
Исчерпание proposal budget отдельно записывается даже при подтверждении лучшего
из уже измеренных кандидатов. Это не заявление об оптимальности решения.

Первая normal попытка root c1895c4b / PulseLib bdcc762 завершилась с двумя
отказами новых test cases при восьми прошедших ownership regressions. Ложное
`calibration_observation_budget` возникало из-за использования разрешённого
`maximumSamples=1 000 000` как ожидаемого размера каждой короткой пробы.
Исправление ограничивает размер физическим числом native ticks:
`min(maximumSamples, ceil(duration * frequency) + 2)` для каждой пробы. Частота
дерева едина; +2 учитывает обе границы и один запасной тик закрытия. Request cap,
модель, длительности, допуски и критерии не меняются. Реальный слишком малый
sample budget по-прежнему завершает поиск честным BudgetExhausted. Отдельно
проверяются форма N×1 и возможность менять порог до первого физического прогона.

Адресная native fixture использует настоящие Classic/Branch N1/2000 Гц и все пять
режимов, реальную калибровку, silent-grid rollback, recording budget, отмену до
и после передачи управления и отказ от отмены чужой пробы. Все raw observations
записываются в report. Сначала должны пройти отдельные scope A/B grid/ownership
gates; их первый запуск пропустил восемь ownership cases из-за отсутствующей
fixture-переменной и не считается 10/10. Recovery сохраняет фактические два
grid-контроля и выполняет восемь ownership controls отдельно на обоих binaries.

Открыты: расширенная серверная matrix этого контроллера, полная visual QA,
production Console ASan, learner property dispatch,
continuation с уже завершённого PostTune/calibrated checkpoint, вся матрица
N0/N1/частот/размерностей/физических профилей/общих attach positions и научная
серия. Отказ от nested PostTune source сейчас явный; поддержку continuation нельзя
считать реализованной только из-за существования model export/import.

Текущий independent auditor `posttune_transaction_evidence.py` уже проверен на
24 настоящих reports: replay signed peaks/gap, исходную физику кандидатов,
coordinate proposals, duplicate clipping, selected index, labelled complete
matrices и передачу в реальную калибровку. Перестановка observation rows не меняет
результат; удаление foil, ложный gap/metric, изменение search condition, criterion,
selected index или schema отвергаются. Partial/cancelled observations остаются
диагностикой без доказательства полноты; валидность произвольных native physics
rejections не выводится из JSON. 19 checks включают 11 новых и 8 compatibility
candidate checks; это не 19 независимых обучений.

Следующая matrix-проверка добавляет `NativePostTuneTransaction.ClassicN0_2000`
и `BranchN0_2000` в тот же реальный fixture. Сохраняются 2000 Гц, два входа,
начальная физика, допуски, исходный protocol и native предложение порога по
полной неспайковой характеристике. Меняется только normalization N1 → N0.
До серверного выполнения эти cases не приняты; отсутствие положительного gap
не должно переименовываться в доказательство физической невозможности модели.

В normal fixture Off/KeepDone и Auto/Soma controls подтверждают пару у обеих
топологий; Classic подтверждает также CanonRmin. Branch CanonRmin, оба FlatLastR
и оба one-pass SearchSynthetic остаются `search_unresolved` на объявленной сетке
и восстанавливают source. Synthetic измеряет три уникальные модели, четыре
предложения являются физическими дубликатами. Calibrated confirmations имеют
TP1/FP0/FN0/TN1 на одной паре; source Train остаётся search_unresolved. Результаты
не являются научной восьмипаттерновой серией или проверкой generalization.

Механический scope A/B отдельно завершён на normal и ASan: у каждого бинарника
два grid cases и восемь ownership controls, по четыре independent checks на каждый
набор; все 28 CSV pairs и восемь ownership JSON совпали точно. Первый A1 с восьмью
skips сохранён как непринятый, фактические grid cases восстановлены отдельным
receipt. ASan нового PostTune-контроллера завершён на source 44a1598a / c8a1995:
10/10 native (3733.602 s) и 19/19 исходного reader (158.845 s). Поздний строгий
reader e9f3cc852 прошёл 20/20 на тех же данных (159.205 s), без native rerun.
Leak detection выключен; этот gate не доказывает отсутствие утечек и не заменяет
отдельный ASan production Console.

## Отчёты измерительного контроллера

Новый `report --format posttune-transaction --source-solo <original_learned_state.json>`
строит отдельные графики каждого завершённого weight candidate и вложенного
threshold grid/fresh confirmation. Требуются исходный transaction JSON и полный
соседний комплект первичных данных Solo. Перед созданием каталога проверяются
родительский auditor, связь с Solo и все завершённые matrices. Каждый паттерн
показывается для каждой сомы с реальными входами, overview и детализацией без
прореживания. Незавершённые пробы сохраняются в lossless transaction, но не
подменяются полными графиками. Графики weight selection используют унаследованный
порог и не доказывают распознавание; калибровка не становится independent Test.

Серверный render завершён: 24 reports, 61 completed matrices, 184 trial-soma
pairs; 4 новых и 5 plotting checks прошли (20.592 s), hashes 8668 cache files
проверены. [Compact bundle](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-controller-visual-normal-a3/README.md)
содержит 455 metadata members (445980 bytes), все они локально сверены; 16
selected PNG просмотрены в исходном размере. Отдельный QA описывает конечные
окна с ещё положительным потенциалом: settling/late events не подтверждены.
Полные cache остаются на Data M40; полный manual/PDF/SVG QA и новые Console
waveforms этим gate не приняты.

## Штатная операция Console: адресная normal-приёмка

`NeuroModelerConsole --timelearner-posttune job.json --timelearner-output <new-directory>`
добавлен отдельной операцией, взаимоисключающей с Train/export/evaluate/calibrate
и выполнением проекта. После штатного `UAppCore.Init` используется свежий owner,
полный native import/readback и тот же `NativePostTuneTransaction`, без тестового
кода, вложенного Calculate или перезаписи runtime. Цикл исполнения, отмена,
ограничение модельных тиков и запись артефактов общие с calibration operation.
Сборка и настоящие Console jobs прошли адресную normal-приёмку, описанную ниже.
Связывание с публичными свойствами
learner, Python runner и продолжение checkpoint остаются отдельными открытыми пунктами.

Вход `timelearner_native_post_tune_job`, schema 1, имеет точные поля прежнего
`timelearner_native_calibration_job` и дополнительный объект `post_tune`:

| Поле | Контракт |
|---|---|
| `mode` | `off`, `keep_done`, `canon_rmin`, `flat_last_r`, `search_synthetic`; не single-candidate API |
| `metric` | Явно `auto`, `ltzone` или `soma_sum` |
| `canonical_floor`, `canonical_last`, `resistance_bounds` | Те же mode-specific условия и per-input bounds, что у native-контроллера; unused значения не применяются |
| `search_passes`, `maximum_candidates` | Целые 1–128 и 1–4096 соответственно; это budget поиска весов |
| `maximum_recorded_samples` | Целое 1–100000000; физический budget, включая калибровку |
| `minimum_positive_gap` | Конечное неотрицательное число в единицах выбранной метрики |

Верхнеуровневые `thresholds`, `maximum_candidates`, `specification`, `trials`
задают реальную последующую калибровку. SHA256 подписывает весь job. Неизвестные
поля/режимы отвергаются. Output содержит исходный job, полный transaction,
действительную конечную модель и signed execution с `post_tune_status`.
`completed/search_unresolved` — допустимый отрицательный исход выполнения,
а не успешная классификация. При tick limit применяется native Cancel/rollback;
завершение процесса без terminal artifacts само по себе не подтверждает rollback.

Сборка Console root `ffd5b15a264f6d66e131230ddd301ef8ae754ea3` на Elder завершилась
успешно в отдельном `runtime-s08-native-posttune-console-normal-a1`; новая операция
присутствует в `--help`, runtime manifest сохранён. Затем выполнены реальные jobs.
Python-команда `posttune <job> --source-solo <state> --runtime-manifest <manifest>
--wall-seconds <limit> --output <new-run>` использует общий owned-process runner
и portable auditor calibration/PostTune, без второго цикла управления процессами.
Схемы jobs/executions/run-manifest различаются явно; default calibration API
сохранён. Preflight связывает physics, поиск весов, threshold design и модельный
budget с condition digest; native effective capability остаётся проверкой Console.
Новый `analyze --format posttune-run` повторно проверяет portable artifact closure,
declared PostTune parameters, родительский search, полный child calibration и
действительную конечную модель. [Корпус normal Console](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-console-normal-a2/README.md)
опубликован в 3c1751f9: 18 PostTune jobs (9 Calibrated, 7 SearchUnresolved,
2 BudgetExhausted), 6 прежних calibration regressions, 2 дополнительных public
CLI jobs, 2 tick-stop controls и 4 native parser/mode rejections. Четыре новых
reader checks прошли; поздняя ревизия повторила четыре. Восемь calibration worker
checks прошли; пропущенный из-за отсутствующей fixture provenance class затем
восстановлен отдельными четырьмя actual checks, без повторения native jobs.
В архиве 1146 members / 5936272 bytes; все локально сверены. Source Train не
становится Exact, калибровка этой пары не доказывает независимую классификацию.
ASan Console выполнил отдельный корпус: 18 PostTune jobs, 6 calibration regressions,
дополнительные CLI/tick-stop/strict controls; 4/4 PostTune reader (112.103 s),
8/8 calibration worker (234.799 s), 4/4 provenance (15.333 s), без skips.
[Primary bundle](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-console-asan-a1/README.md)
88c47ddf сохраняет 1089 members / 6054552 bytes. Это replay сохранённых normal
моделей, не новые независимые обучения. Полная matrix и новые production
waveform reports остаются открытыми.

### Ограничения следующего связывания с learner properties

Проверка текущего кода показывает, что подключение нельзя свести к удалению
`configured_native_optional_mode_not_yet_supported`:

- `ConfiguredNativeOwner.h::PrepareConfiguredNativeOwner` сейчас явно отвергает
  C-trim, PostTune и auto calibration. Этот guard должен остаться до появления
  полного объявленного phase plan и адресных проверок; Console API его не отменяет.
- `NativeRecognitionOwner.h::InstallNativeRecognitionState` устанавливает новый
  recognition context и очищает training service/probe. Solo proof, outcome и
  исходные optional controls требуется сохранить **до** первого import. Хранить
  долгоживущий orchestration state в очищаемом training service нельзя.
- `VisitNativeRecognitionControls` зеркалирует `IsNeedToTrain=false`,
  `EnablePostTrainTuning=false`, auto calibration off и фиксированный threshold.
  Последующие фазы не могут восстанавливать исходный план из этих transient mirrors.
- `NNeuronTimeLearner::ACalculate` (и соответствующий Branch путь) сначала
  обрабатывает recognition hold. Переход Training → Recognition меняет маршрут
  расчёта; новый управляющий объект должен продолжать получать ровно один
  boundary callback, после завершения callbacks прежнего context. Import не
  должен уничтожить исполняющийся управляющий объект.
- `ABeforeReset`, Build/Init и native import уже имеют lifecycle/edit guards.
  Нельзя добавлять reentrant import/rollback из Reset hook или подменять
  физический reset сбросом всего phase plan. Explicit Reset, implicit Reset из
  Build/Init, внешний stop и retarget нуждаются в отдельных native проверках.

Требуемый порядок перехода: сохранить versioned Solo и честный training outcome;
сохранить объявленный phase plan отдельно от physical/owner mirrors; завершить
старый native callback; поставить переход на допустимую границу; импортировать
полную recognition-модель; передать её измерительному контроллеру; после каждой
фазы проверить фактическое состояние и сохранить новый результат. Ни один из
этих переходов не вызывает Calculate из контроллера и не повышает прежний
`search_unresolved` до Exact. Этот участок остаётся открытым требованием этапа 8.

### Отчёт для production run manifest

`report RUN_MANIFEST --format posttune-run --output CACHE` сначала проверяет
полную portable artifact closure запуска, условия задания, runtime fingerprint,
owned-process evidence, исходные primary data и фактический результат native
операции через production `audit_run_manifest`. После этого общий renderer
строит все завершённые weight/threshold matrices и fresh confirmation: каждый
паттерн, каждый канал сомы, фактические входные импульсы, обзор и временные
увеличения без прореживания native samples. Partial probes сохраняются в
первичных данных, но не выдаются за полные реакции.

`run-binding.json` связывает рисунки с attempt, source closure и runtime;
SHA256SUMS охватывает также эту связь. Это проверка согласованности сохранённых
свидетельств, а не независимая аттестация произвольного process record:
`native_execution_verified=false`, `visual_acceptance_complete=false`,
`evaluation_verdict=null`. Same-matrix данные не становятся независимым Test.
Полный cache хранится на M40 Data; в Git публикуются компактные первичные данные,
модели, метрики, metadata и выбранные рисунки. Новая обёртка и три адресные
проверки добавлены; серверная проверка всех 18 production reports пока ожидается.
