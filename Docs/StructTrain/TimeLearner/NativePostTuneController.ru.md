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
не менялись ради прохождения N0. ASan N0 завершён: 2/2 native, 3351.650 s,
12/12 reader, 136.129 s. [ASan proof](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-controller-n0-asan-a1/README.md).

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
Эти cases выполнены normal и ASan; адресные результаты приведены выше.
Отсутствие положительного gap не является доказательством физической невозможности модели.

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

Подготовлен общий codec `NativePostTuneConfiguration`: точные девять controls
существующего schema-1 production job кодируются/декодируются в PulseLib.
Console использует этот путь вместо собственной копии разбора; configured
phase plan должен использовать тот же codec. Calibration design передаётся
отдельно и сохраняется целиком; codec не придумывает threshold grid, foil,
новые defaults или независимую partition. Pure type/budget validation отделена
от проверки физики/модели в `NativePostTuneTransaction` до live edits.
Это подготовка общего пути, не реализация learner dispatch: optional-mode
guard остаётся. На root `d48837f1ad9e49029493932ddabffe214c2827c5` / PulseLib
`30f737c8e445bc76be21c1e37eec1d1b99b90a6e` три native codec cases прошли без
skips, включая все 18 опубликованных jobs и независимые numeric bindings.
Два owned Console A/B (Classic Auto и Branch SearchSynthetic) прошли portable
audits: transaction и конечная модель побайтно совпали с исходным Git bundle.
[Primary proof](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-codec-normal-a1/README.md):
103 members / 630420 bytes; все member hashes перепроверены после merge.
ASan codec завершён отдельно после N0: 3/3 native и два byte-exact owned
Console A/B, [109-member proof](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-codec-asan-a1/README.md).

Проверка текущего кода показывает, что подключение нельзя свести к удалению
`configured_native_optional_mode_not_yet_supported`:

- `ConfiguredNativeOwner.h::PrepareConfiguredNativeOwner` сейчас явно отвергает
  C-trim, PostTune и auto calibration. Этот guard должен остаться до появления
  полного объявленного phase plan и адресных проверок; Console API его не отменяет.
- `BeginNativeTraining` обоих learner также отдельно отвергает PostTune/auto
  calibration. Снятие только guard в Prepare не включает фазы и создаст ошибку
  после cold Build. Оба пути должны использовать один сохранённый phase plan.
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
- `UContainer::Calculate` вызывает BeforeCalculate до пересоздания active-child
  cache; ACalculate вызывается после расчёта детей. Это определяет допустимую
  границу queued import перед следующими children. Проверить необходимо и
  родительский scheduler: нельзя запрашивать ComponentReCalculation и повторно
  рассчитывать уже прошедшие дети того же tick.
- Schema 1 `NativePostTuneTransaction::FinishWeights` делегирует threshold
  grid/fresh confirmation после положительного измеренного gap. Новая typed
  ветка schema 2 `KeepFixedThreshold` описана ниже; это ещё не подключение
  комбинации learner properties PostTune on / auto calibration off.

Требуемый порядок перехода: сохранить versioned Solo и честный training outcome;
сохранить объявленный phase plan отдельно от physical/owner mirrors; завершить
старый native callback; поставить переход на допустимую границу; импортировать
полную recognition-модель; передать её измерительному контроллеру; после каждой
фазы проверить фактическое состояние и сохранить новый результат. Ни один из
этих переходов не вызывает Calculate из контроллера и не повышает прежний
`search_unresolved` до Exact. Этот участок остаётся открытым требованием этапа 8.

### Выбор весов с неизменным порогом: schema 2

Добавлена явная typed-настройка `NativePostTuneFinalization::KeepFixedThreshold`.
Она использует те же native full-pattern probes, выбор лучшего измеренного gap,
integer/physical bounds, recording budget и rollback, но не создаёт threshold
candidate и не запускает calibration transaction. После положительного gap:

```text
assert threshold(selected measured candidate) == threshold(source)
import selected candidate through the native scope
Build / Init / Reset and verify effective package
emit weights_selected, calibration_status=fixed
retain measured selection proof separately from the model archive
leave recognition_success_confirmed=false and evaluation_verdict=null
```

Это успех выбора весов, а не детекции: молчащий target по-прежнему является FN
при оценке. `CalibratedPackage()` остаётся пустым; `FinalPackage()` возвращает
выбранный recognition candidate. Его исходный marker `candidate_unmeasured`
не подменяется embedded proof: фактическое доказательство измерений и выбора
находится в parent report. Source Solo, training outcome и отсутствие Exact
для изменённой recognition-модели сохраняются. Отдельная последующая
калибровка может стартовать с импортированной завершённой границы.

Фиксированный режим требует пустого threshold grid и нулевого calibration
candidate budget: неиспользуемый фактор отклоняется. Отсутствие положительного
gap даёт unresolved, исчерпание recording budget — budget_exhausted; rollback,
внешняя отмена и lifecycle interference используют прежний guarded scope.
Schema 1 по умолчанию продолжает Calibrate и сохраняет прежний формат.

`Encode/DecodeNativePostTuneControlsV2` явно записывают schema 2 и finalization.
Попытка сохранить fixed-режим старым codec запрещена, чтобы не потерять фактор.
Production Console/job/worker root 2d6ab1a0 добавляют explicit schema-2 job;
scoped серверная проверка normal/ASan выполнена; подробности ниже.
Schema 1 остаётся прежним API.
Python analyze/report transaction уже поддерживают schema-2 native reports;
это не поддержка production fixed job. При lifecycle interference raw fixed
обозначает объявленную политику, а derived calibration status — `unverified`;
успешное восстановление live owner из sidecar не предполагается.

Восемь native controls и четвёртый codec case прошли на Elder normal (12/12,
67.946 s) и M40 ASan (12/12, 401.903 s; leak detection off). Проверены оба
learner, silent target, roundtrip waveform/parameters, отдельная следующая
calibration phase, budget/cancel/Reset. По два owned legacy Console A/B
в каждой сборке сохранили исходные transaction/model bytes. Normal source
root 3d922ba2, ASan source 38cd68a0, PulseLib 03d1ea86; latest readers b7cab734.
[Normal](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-normal-a2/README.md)
и [ASan](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-asan-a1/README.md)
содержат полный источник каждого portable run. Это проверенный typed API,
а не подключённый learner-property dispatch и не приёмка этапа 8.

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
проверки выполнены на всех 18 production reports: 59 завершённых матриц,
178 trial-soma pairs, 8437 cache files; 8/8 проверок (13.076 s), без skips.
На последнем test revision `7e8d97f3f` те же 8/8 прошли за 12.419 s,
включая отсутствие частичного output при недоступном plotting backend у
обоих PostTune entry points. [Compact evidence](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-console-visual-normal-a1/README.md):
422 metadata members и 12 выбранных PNG. Все 12 PNG вручную просмотрены;
это приёмка читаемости выборки, не полного кэша, PDF/SVG или независимого Test.

### Production job schema 2: граница реализации

Root 2d6ab1a059005af30bc3d55a78c2192e6cbd9813 добавляет explicit schema-2
job в Console и owned worker. У job schema_version=2, внутри post_tune
schema_version=2 и finalization=calibrate либо keep_fixed_threshold. Остальные
девять controls не меняют смысл. Для fixed обязательны thresholds=[] и
maximum_candidates=0; последний относится к калибровке, а отдельный
post_tune.maximum_candidates продолжает ограничивать поиск весов.

Команда остаётся штатной:

```text
python -m Scripts.StructTrain.TimeLearner posttune JOB.json \
  --source-solo LEARNED_STATE.json --runtime-manifest RUNTIME.json \
  --wall-seconds SECONDS --output NEW_RUN_DIRECTORY
```

Worker проверяет labelled design без фиктивной сетки калибровки. Общая функция
validate_trial_design используется также прежним calibration validator;
неизменённые schema-1 conditions/preflight должны подтверждаться реальными
portable regression runs. Fixed design fingerprint не утверждает выполнения
калибровки или независимого разделения данных. Единый научный ConditionSpec
всех runner ещё не реализован; это scoped job identity, не закрытие этапа 10.

Внешние execution и run manifest сохраняют schema 1. Fixed transaction
возвращает schema 2/weights_selected; calibrate (включая новый explicit job)
сохраняет прежний transaction schema 1. Worker связывает конечную модель с
selected_package при weights_selected, с calibrated_package при calibrated
или с исходной моделью при подтверждённом rollback. Модель selected не получает
нового Exact или встроенного selection proof. Полная матрица режимов,
configured learner phase dispatch остаются незакрытыми. Scoped production
normal/ASan проверка выполнена отдельно: по шесть actual owned jobs, 3 preflight
checks и 4 final worker checks (включая повтор preflight), четыре actual Console
rejections без native output. Обе topology fixtures: fixed weights_selected;
Classic calibrate calibrated, Branch calibrate search_unresolved. Legacy и
explicit v2 calibrate сохраняют исходные transaction/model bytes.
[Normal proof](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-console-normal-a1/README.md):
317 members; [ASan proof](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-console-asan-a1/README.md):
322 members, leak detection off. Каждая упаковка замыкает шесть run snapshots /
252 artifact entries, все hashes повторно проверены после merge. Shared design
validator также прошёл 4/4 portable regression tests на всех 18 прежних runs.
Это не приёмка полной матрицы или этапа 8.

Все шесть новых production ASan runs также прошли реальный CLI
report --format posttune-run: 62 полные trial-soma реакции. Полный cache
2979 files / 304534961 bytes хранится на M40 Data; 210 metadata members /
674200 compressed bytes находятся в [Git bundle](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-fixed-console-visual-asan-a1/README.md).
Все cache/member hashes проверены. Полная ручная визуальная приёмка этих
62 реакций остаётся открытой; предыдущие selected roundtrip PNG описывают
свои отдельные пробы и не заменяют эту проверку.
