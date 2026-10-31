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

Открыты: ASan и расширенная серверная matrix этого контроллера, полные
временные графики, Console/learner public dispatch и параметрический codec,
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
receipt. ASan самого нового PostTune-контроллера выполняется на закреплённом A2;
его источники/runtime не обновляются до terminal outcome.

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

Реализация и четыре проверки полного cache добавлены отдельно от подтверждённого
normal native gate. До фактического серверного render/test и ручного просмотра
новых рисунков эта часть не принята. Полные cache сохраняются на диске Data M40;
в Git публикуются сжатые primary/metadata и только явно выбранные рисунки.

## Штатная операция Console: реализация до серверной приёмки

`NeuroModelerConsole --timelearner-posttune job.json --timelearner-output <new-directory>`
добавлен отдельной операцией, взаимоисключающей с Train/export/evaluate/calibrate
и выполнением проекта. После штатного `UAppCore.Init` используется свежий owner,
полный native import/readback и тот же `NativePostTuneTransaction`, без тестового
кода, вложенного Calculate или перезаписи runtime. Цикл исполнения, отмена,
ограничение модельных тиков и запись артефактов общие с calibration operation.
Пока серверная сборка и настоящие Console jobs не пройдены, это реализация,
а не принятая возможность production pipeline. Связывание с публичными свойствами
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
присутствует в `--help`, runtime manifest сохранён. Это ещё не проверка выполнения jobs.
Python-команда `posttune <job> --source-solo <state> --runtime-manifest <manifest>
--wall-seconds <limit> --output <new-run>` использует общий owned-process runner
и portable auditor calibration/PostTune, без второго цикла управления процессами.
Схемы jobs/executions/run-manifest различаются явно; default calibration API
сохранён. Preflight связывает physics, поиск весов, threshold design и модельный
budget с condition digest; native effective capability остаётся проверкой Console.
Новый `analyze --format posttune-run` повторно проверяет portable artifact closure,
declared PostTune parameters, родительский search, полный child calibration и
действительную конечную модель. Добавлены четыре проверки корпуса из 18 настоящих
Console runs; их серверная приёмка ещё не выполнена.
