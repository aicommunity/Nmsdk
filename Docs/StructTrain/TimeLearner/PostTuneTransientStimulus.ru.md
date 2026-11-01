# PostTune: transient stimulus и неизменяемая обучающая цель

Проверенный подэтап рабочей ветки `stage08/posttune-transient-stimulus`.
Этап 8 целиком не завершён и не принят в develop.

## Изменение и контракт

Оба `PushPostTunePattern` записывали временный pattern в публичный InputPattern
через SetDataDirect. Поиск кандидата тем самым подменял обучающую цель без
штатного retarget/invalidation. Удалить только запись недостаточно: ожидаемые
времена в BeginTrainingIteration должны соответствовать предъявляемому pattern.

InputPattern, material Neuron.TrainingPattern и сохранённый PostTuneTargetIsi
сохраняют исходную цель. Dataset.MatrixData задаёт transient presentation.
В single-presentation PostTune ожидаемые relative arrivals читаются из этой
матрицы; обычное обучение продолжает читать InputPattern. Multi-sample free-run
сохраняет отдельный playback path. Invalid index не меняет цель и часы.

Новые Build/Default/Calculate и изменения storage physics не вводятся.
Существующий native Reset dataset/generator/neuron выполняется до следующей
пробы. PulseLib production commit: `0e1b01ae91addfe27c3a4731596f82d27321d01b`.

## Проверки на обоих workers

Корректный pre-fix root `f9a30cb72b08e800cada41c6c547f2b63db0c9c9`, PulseLib
`6e28d2033802c0ce98ba3f6ec496412b5e2b40c2`: по 4 ожидаемых failures normal
на Elder-1 и M40. Actual Classic/Branch production Push/Begin вызываются на
native graph при 2000/20000 Гц. Каждый case предъявляет два разных pattern,
включая первое ISI=0. Старый код изменяет цель.

Fixed native root `a5ada26f4ff0d6e6e1292cffc83df26bb004026b`, PulseLib 0e1b01ae:
по 4/4 C++ и 7/7 Python на Elder normal и M40 ASan (detect_leaks=0).
На каждом worker — 8 полных presentations, 19368 actual CSV samples.
Python-only root `bb4a351185956365d483d1db5e2d7309bd39ab31` прошёл 8/8 tests:
добавлена подмена goal/stimulus посреди окна с восстановленными endpoint metadata.
Все 8 общих time/stimulus/soma проекций byte-exact к baseline на каждом worker;
physical model hashes также совпадают. Это контроль сохранения физики данных
fixtures, не доказательство причин исторических научных результатов.

`analyze --format posttune-transient` независимо проверяет schema, конечные
числа, полное окно/gaps, stimulus timestamps и relative expected arrivals,
размерность и изменяемость отклика, обе goal copies, frozen model hash и goal /
presented ISI в каждом raw frame. Endpoint metadata недостаточно. Native
execution и measured training certificate анализатор не удостоверяет;
scientific verdict остаётся null.

## Исправления постановки сохранены

Первый baseline root 8f341775 не собрался из-за отсутствующего include теста.
Root 8a5873c5 и первый fixed 794695f3 использовали фазу 4 для обеих топологий:
у Branch это PostTune, у Classic — failed. Classic timing failures тех попыток
не являются установленным дефектом алгоритма или lifecycle. Корректная фаза
Classic — 3; см. [контракты](DiagnosticPropertyContracts.ru.md).
Все эти попытки сохранены отдельно; результаты корректного baseline приведены выше.

## Артефакты

- [Elder-1](../../../Reports/StructTrain/TimeLearner/s08-transient-elder1/README.md),
  commit `9bc7a07fdf86666068c2be1a98fdca3157a61f43`.
- [M40](../../../Reports/StructTrain/TimeLearner/s08-transient-m40/README.md),
  commit `83e4148f0f3cbac990166f67c259ce5a8d0a2479`.

На каждом worker опубликованы 198 stored / 196 raw checksums; все локально
проверены по Git-файлам и распакованному содержимому. Новая симуляция локально
не выполнялась. Raw traces, runtime/source metadata, failed attempts и independent
analysis доступны в пакетах.

## Открытая работа

Fixture вызывает production Push/Begin на настоящем native graph; он не
выполняет весь SearchSynthetic, candidate selection или обучение до сертификата.
Полная транзакция кандидата, произвольный retarget во время legacy PostTune,
production wiring V2, реальный подбор/проверка порога и independent frozen Test
остаются открытыми. Finalize legacy сохраняет собственную restore logic.
Mid-probe checkpoint и произвольный warm continuation этим не подтверждены.

## Уточнение следующей транзакции по текущему коду

Read-only сверка 29.10: Branch EnterPostTunePhase вызывает parallel scaling для
SearchSynthetic до сохранения PostTuneTipSnapshot, затем ApplyPostTrainTipMode
до RebuildCableForPostTuneProbes. Успешный rollback последнего helper возвращает
состояние непосредственно перед реконструкцией, которое уже содержит candidate
edits. Поэтому это не rollback к началу PostTune. Classic также меняет режим
до настройки пробы. Ни один из этих выводов не объявляется новым runtime defect:
полная транзакция ещё не реализована и baseline отказа именно этой границы
ещё не поставлен.

Следующий подэтап должен различать source recognition state, выбранный best
candidate и текущий speculative candidate. Snapshot в начале этапа должен
предшествовать любому scaling/canonicalization. Достаточен checkpoint завершённой
границы этапа; физическую динамику посреди пробы сохранять не обещаем.

```text
at legal completed boundary:
    capture complete native neuron + dataset snapshots and boundary sources
    capture threshold policy, training goal, conversion and controller state
    validate source identity
for each declared candidate:
    construct from immutable source/best state through native import
    apply candidate only before arming a new observation
    validate effective model and numerical domain
    observe complete window through scheduler
    bind observation to candidate revision and presentation ID
    retain best only with complete valid evidence
on failure/cancellation:
    restore source graph, dataset policy, thresholds and controller boundary
    refresh all cached aliases; verify effective identity; native physical reset
on selection:
    commit selected state; invalidate source-only certificate/calibration
    freshly verify final recognition state and chosen threshold separately
```

Нельзя восстанавливать только TipRs: сохранить реальные classes/children/C,
Rs/Ns, связи и owner order, Dataset matrix/classes/one-pass/delay/generator
настройки, исходные threshold properties, goal и provenance conversion.
Контроллер хранит собственные counters/results, а не передаёт их neuron Reset.
Восстановление физического графа не означает восстановления старого runtime clock.
Не вводить nested Calculate или Build, предназначенный лишь для пробуждения.

Приёмка через реальные Enter/Finalize и candidate loop: успех, rejection после
изменения physics, setup failure после candidate edit, timeout, external stop,
ошибка attach, повторный запуск; Classic/Branch, N0/N1 и все tip modes.
Проверить source/committed graph identities, Dataset/threshold policy и новую
полную waveform после rollback. Отдельные helper tests не заменяют эти controls.
Исторический Same-Matrix и independent frozen Test должны иметь разные metadata;
legacy поведение нельзя молча заменить новой научной задачей.
