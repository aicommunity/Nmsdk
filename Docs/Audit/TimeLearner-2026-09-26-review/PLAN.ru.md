# План исправлений и новых экспериментов TimeLearner Cold

Статус: план работ, реализация не начата. Дата: 2026-09-26.

Основание: [повторный аудит](README.md). Этот документ задаёт порядок устранения найденного дефекта и проверки Cold-обучения. Общие незакрытые пункты исходного [плана 2026-09-24](../TimeLearner-2026-09-24-review/PLAN.ru.md) сохраняются, если ниже не указано иное; прежде всего R01/R04 и полная provenance каждого запуска.

## 1. Цели и ограничения

1. Исправить и изолированно проверить termination defect классического `NNeuronTimeLearner`.
2. Проверить, меняется ли от этого поведение Cold AsymRm, не смешивая завершение Train с качеством PostTune/Test.
3. Получить диагностические данные для Branch `NonSeparable`, прежде чем менять морфогенез или ослаблять критерии.
4. Сделать фактическое состояние после reset и происхождение каждого опыта воспроизводимыми.
5. После точечных проверок завершить отложенные C1/C2 только на одной зафиксированной сборке и по неизменным gate-критериям.

**Не является целью:** добиваться PASS любой ценой, менять acceptance threshold/`LandscapeOk`, делать вывод о причине по одному `Need=0` или считать GoldTest доказательством успешного Cold-обучения.

## 2. Зафиксированный baseline

| Область | Наблюдение | Следствие для плана |
|---|---|---|
| Classic TimeLearner | `kAmpNormEps` имеет тип `int`, хотя значение `1e-5`; C4244 и комментарий о stalls около `6e-6` | Исправить до новых выводов по classic AsymRm Cold |
| Branch TimeLearner | br25 soft-cold после синхронизации Train flag остаётся `NonSeparable`; H1–H4 не выявили влияния Keep/strip/AutoScale | Диагностировать iteration path и live morphology; не менять рост по предположению |
| Branch cold reset | preflight валидирует XML `L=1 1 1 1`; `ResetToUntrained` устанавливает reference length в 0 | Уточнить контракт/намерение, писать состояние после C++ reset |
| Wave C evidence | 14 C1 случаев FAIL с разными причинами; run bundles локально отсутствуют; остаток C1/C2 DEFER | Сначала восстановить или заново собрать полное доказательство |
| Удалённая машина | Последние SSH-проверки завершились таймаутом TCP/22 до аутентификации | Удалённые артефакты и Ubuntu-прогоны — блокер для экспериментальных фаз |

## 3. Фаза 0 — восстановить экспериментальную базу

### Действия

1. Перед изменением кода повторно проверить доступ к Ubuntu-машине и наличие `Bin/Platform/Linux/NeuroModelerConsole`. До доступности машины не считать старые таблицы заменой исходных логов.
2. Если доступ восстановлен, собрать в read-only режиме inventory `/home/user/Nmsdk/Bin/Configs/SpikeSamples/StructTrain/_repro/runs`: список case/run-id, размер, время, наличие `provenance.json`, stdout/stderr, Train/Test flags, CSV, параметры и веса. Посчитать SHA-256 копируемых артефактов.
3. Сначала скопировать недостающие wave-C bundles и существующие br25 H1–H4 bundles без перезаписи удалённых источников. Сопоставить каждый bundle с таблицей `EXPERIMENTS.md`.
4. Для baseline фиксировать root/PulseLib/Bin HEAD, dirty diff, бинарный SHA, компилятор/флаги, ОС, harness/gate SHAs, исходные параметры/модель/матрицу и команды запуска.
5. Если bundle не восстановлен или в нём нет нужных событий обучения, выполнить один baseline-прогон на **текущем, ещё не исправленном** коде для выбранных classic cases и Branch br25. Поместить результат в отдельный чистый workdir.

### Приёмка фазы

- Каждой записи в реестре соответствует проверяемый run-id и полный manifest либо явно помеченная нехватка данных.
- До патча есть воспроизводимый контрольный baseline на том же Ubuntu/runtime, который будет использоваться после патча.
- Ни старые flags/CSV, ни конечные веса предыдущего прогона не попадают во входы нового clean workdir.

Если SSH остаётся недоступен, продолжить исправление и локальные проверки, но отложить все выводы, требующие Ubuntu; отдельно записать, что baseline до/после исправления несопоставим.

## 4. Фаза 1 — исправить classic epsilon и проверить критерии завершения

### Изменение

В `Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h` заменить целый тип `kAmpNormEps` на `double`, сохранив `1e-5`, если проверка алгоритмического контракта не выявит иного ожидаемого допуска. Просмотреть все употребления в classic `ChangeSynapseResistanceStatus`, `AllSynapsesNormalized` и ветках synapse status. Не переносить автоматически это исправление на Branch: там тип уже `double`.

### Регрессии

1. Добавить проверку, что classic epsilon остаётся положительным и равен ожидаемому `1e-5`; ошибочное integral narrowing должно приводить к ошибке сборки/теста.
2. Проверить поведение tolerance на остатках ниже, на границе и выше epsilon (например `6e-6`, `1e-5`, `1.1e-5`) в тех критериях, которые его используют.
3. Проверить альтернативные Done-пути (`at_r_min`, `dead_tip`, `oscillation`, `no_improve`): исправление не должно маскировать ошибку знака, мёртвый tip без нового peak или незавершённый sync.
4. Сохранить отдельный тест, что Branch epsilon по-прежнему floating-point и не меняется от classic-патча.
5. Собрать Windows и Ubuntu Release targets; устранить предупреждение C4244, не отключая диагностику narrowing.

### Приёмка фазы

- Classic завершает нормализацию при остатке, который контракт считает допустимым, и не считает допустимым остаток выше порога без одного из явно описанных best-effort условий.
- Regression tests показывают ненулевой epsilon; тесты stale/invalid/incomplete PostTune продолжают проходить.
- Linux/Windows Console построены из одного зафиксированного source commit и имеют записанные SHA.

## 5. Фаза 2 — точечно перепроверить classic AsymRm Cold

Сначала прогнать затронутый классический алгоритм; не смешивать его с Branch. Для каждого опыта сравнивать unpatched baseline и patched build, меняя только бинарник/исходный commit с исправлением.

| Case | Роль | Что установить |
|---|---|---|
| `asym50_preinh` | основной незавершённый кейс с gate, который отдельно прошёл | Сбрасывается ли `Need`; соответствует ли residual амплитуды диапазону около epsilon; завершается ли Train корректно |
| `asym100_preinh` | основной кейс с `Need≠0` | Повторяется ли зависание normalization и меняется ли termination reason после патча |
| `asym25_preinh` | контроль того же classic learner с gate failure | Не превращает ли исправление только termination в ошибочный PASS; качество gate остаётся отдельным результатом |
| `asym100_gen` | дополнительный случай с прежним `TipR=flat`/ранним выходом | Отличить epsilon-эффект от выхода до нормализации или иной причины |
| Gold/SkipTrain контроль | проверка Test/gate pipeline на готовых весах | Подтвердить только работоспособность измерительного контура, не Cold-обучение |

Для каждого запуска сохранять: child rc и сигнал/причину завершения; число и время итераций; `Need`; `DendriteLength`, `NumSynapse`, `TipR`; `InitialSomaPotential`, измеренную амплитуду и signed residual по каждой ветви; `ResistanceStatus`, `NoImproveResistanceCount`, `PeakSeen`, длину/синхронизацию; Train flag и XML после flush; полный Test CSV, `fires`, target/foil metrics, `mid`, `Result`, gate rc.

Не менее двух независимых clean workdir для каждого основного случая, если первый результат не является детерминированным. Если доступна только одна машина/длительный прогон, сначала выполнить один прогон каждого основного case и решить о повторе по variability.

### Приёмка фазы

- Для classic случаев процесс завершения отдельно классифицируется как завершённый Train, некачественный landscape, gate failure или прерванный запуск.
- Исправление считается подтверждённым для termination, только если `Need=0` достигается без salvage и параметры/flags относятся к текущему run-id. Gate PASS не требуется для доказательства termination и не выводится из него.
- Любой `NonSeparable` сохраняется как отрицательный результат качества, даже если Train завершился штатно.

## 6. Фаза 3 — проверить фактическое Cold-состояние после reset

### Код/harness

1. Добавить в C++ диагностический snapshot после `ResetToUntrained`/`AReset` и до первого Train iteration: learner class, reset flag, `DendriteLength`, `NumSynapse`, `InitialSomaPotential`, `TipSynapseResistance`, `IsNeedToTrain`, LTZ threshold, segment/tip topology, reference/active indices.
2. В `repro_cold_lib.py` разделить два контракта: **входной XML** до загрузки и **runtime state** после reset. Preflight должен проверять правильное состояние в соответствующей фазе, а не выдавать XML-вектор за подтверждение live state.
3. Подтвердить с владельцем алгоритма/код-контрактом, что нулевая последняя Branch length является намеренным reference anchor. До подтверждения не менять `ResetToUntrained` на длину 1.
4. Расширить provenance `posttune_verify.py`: записывать source SHA-256 **до и после** запуска для всех файлов из `PROVENANCE_SOURCE_REL`; различие должно давать явный verdict. Уже сохраняемые `config_sha256_before` дополнить итоговыми hashes входов/конфигов и связать их с phase/run-id.
5. Разделить в machine-readable результатах `train_incomplete`, process error/timeout, Train complete + quality failure и gate failure. `Need=1` и отсутствующий Train flag не могут считаться завершённым обучением даже при `gate_rc=0`.

### Приёмка фазы

- Bundle показывает XML до запуска и runtime state после reset; Branch anchor отражён явно.
- Повтор одного case из одного manifest воспроизводит заявленный initial live state.
- Hashes source/config до и после совпадают или запуск маркируется как изменённый во время исполнения.

## 7. Фаза 4 — диагностические эксперименты Branch br25

Повторять H1–H4 только если восстановленные bundles не содержат нужных исходных событий/метрик или бинарник/входы не соответствуют provenance. Уже имеющиеся агрегированные выводы не заменяют per-iteration trace.

### Сравнение

| Run | Протокол | Назначение |
|---|---|---|
| B0 | br25 gold / SkipTrainGold | Положительный контроль Test и gate на тех же входных матрицах; не контроль обучения |
| B1 | br25 soft-cold + Canon | Основной воспроизводимый Cold case |
| B2 | br25 cold + Keep | Использовать H1 result; повтор только при неполном evidence |
| B3 | soft-cold vs strip/full-init | Использовать H3 result; повтор только при неполном evidence |
| B4 | AutoScale 0/1 | Использовать H4 result; повтор только при неполном evidence |

B1/B2/B3 должны начинаться с зафиксированного и идентичного runtime-state policy. Для каждого сохранять per-iteration: active/ref dendrite; `PulseSynced`, valid peaks/`PeakSeen`; `PeakRel`, ожидаемые времена, `DelayFromPulse`, `DelayLen`, `Dissynchronization/dt`, `SyncTolerance`; `DendStatus`; применённые delta длины; `NumSynapse`, `SynapseStatus`, `TipR`, сопротивления и статусы; phase, iteration count, stop reason и все amp значения. После Train сохранять неизменённый Train state, затем отдельно Test state.

### Дерево интерпретации

- **Нет active/ref peak:** проверять Dataset→Generator→Neuron wiring, sample playback, LTZ и измерение; не менять шаг длины.
- **Есть peak, но нет anchor snapshot:** проверять bootstrap reference и корректность live state после reset.
- **`dt` указывает на рост, но длина не меняется:** локализовать блокировку в `ChangeDendriteStatus`/`ApplyPendingDendriteLengthChanges`, индексы active/ref и reason остановки.
- **Рост применяется, но target/foil landscape не разделяется:** измерить изменение target, каждого foil и global gap на каждом уровне длины; исследовать критерий/эвристику отдельно от gate.
- **`Need=0`, но `NonSeparable`:** считать штатно завершённым некачественным результатом, а не PASS.

### Приёмка фазы

- Есть минимум один полный B1 run с runtime-state, per-iteration trace, полным gate CSV и provenance.
- Каждое последующее изменение algorithm основано на конкретной строке/событии trace и проверяется отдельным one-factor A/B.
- Gold control, Train completion, separability и final gate представлены как разные verdicts.

## 8. Фаза 5 — завершить отложенную wave C только после целевых проверок

После фаз 1–4 и фиксации сборки:

1. Для уже завершённых 14 C1 повторить все случаи, если отсутствующие bundles восстановить нельзя; если bundles полны, повторно прогнать как минимум classic cases, затронутые epsilon, и все записи с `exited`/неизвестным состоянием.
2. Выполнить оставшиеся 8 C1 случаев, которые ранее были DEFER, и весь C2. Не переносить старые flags, XML output, CSV или веса.
3. Для каждого case создавать новый workdir и manifest из явного списка входов; не использовать `--allow-salvage` и архивный inplace режим для принятия verdict.
4. Обновить обе таблицы по каноническому алгоритму и протоколу: `Train status`, `Need`, TipR class, `Result`, `fires`, Acc/target, gate rc, run-id и bundle. `GoldTest`, `SkipTrainGold`, `SoftCold+PostTune` остаются разными протоколами.

### Приёмка фазы

- Все запланированные случаи получают однозначный статус: PASS по прежнему критерию, завершённый quality/gate FAIL, или DEFER с причиной. Прерванный процесс не выдаётся за завершённый quality FAIL.
- Каждая строка указывает на сохранённый bundle и согласованные source/config hashes.
- Ни один критерий успеха не ослаблен в процессе кампании.

## 9. Фаза 6 — интеграционные остатки R01/R04 и документы

Проводить после восстановления полного run environment; эти проверки независимы от исправления epsilon.

### R01 — sample boundary в настоящем scheduler

- Использовать production Dataset/Generator/Analyzer wiring, не probe со stubbed вызовами.
- Инструментировать sample id, stimulus/response timestamps, expected stimulus count, observation deadline, incomplete/censored state и закрывающий event.
- Покрыть sample advance до полного старого паттерна, смену sample без stimulus edge и coincident sample/stimulus edge.
- Приёмка: ни один event не приписывается новому target, пока относится к старому trial; частота/достижимость сценария измеряется и записывается отдельно.

### R04 — два полных цикла на одном объекте

- Для classic TL и Branch выполнить два последовательных полных Train→PostTune→Test циклов на одном объекте, включая новый `IsNeedToTrain` attempt и fallback.
- Проверить сброс `PostTuneResult`, observed/finished/finite state, metrics identity, flags и mid; добавить timeout/invalid trace контроль.
- Приёмка: второй цикл не наследует Success, metrics или weights первого; остановка процедуры не подменяет validity/quality.

### Документы и архивы

- В заголовках двух реестров различить Bin commit, использованный для сборки Console, и commit редакции реестра; привести текущий HEAD/date отдельно.
- Исправить неверное утверждение о месте хранения FAIL-строк и проверить все новые ссылки.
- На каждый запуск публиковать компактный bundle с manifest, logs, flags, output params/weights и полным gate CSV; крупные временные `_work`/StatisticLog не коммитить.
- После каждого этапа обновлять статус аудита и регистры; не объединять завершение Train с качеством результата.

## 10. Общие критерии завершения плана

План считается выполненным, когда:

1. Classic `kAmpNormEps` исправлен и защищён регрессией на narrowing и tolerance boundaries.
2. Затронутые classic Cold cases имеют сопоставимые pre/post runs с полным provenance; вывод о epsilon отдельно подтверждён или опровергнут.
3. Для Branch br25 есть полный диагностический run, показывающий путь от peak measurements до роста/остановки длины и separability verdict.
4. Cold preflight сообщает как входной XML, так и effective runtime state.
5. Отложенные C1/C2 и выбранные R01/R04 integration checks получили проверяемые verdicts либо явно зафиксированы как blocked внешней недоступностью.
6. Реестры, артефакты и audit status согласованы между собой; PASS не присваивается по одному факту завершения, а failure не маскируется изменением порогов.
