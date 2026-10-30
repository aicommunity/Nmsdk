# Повторный аудит структурного обучения — 2026-09-24

**Вывод:** основные технические замечания исходного аудита были обоснованы для зафиксированного тогда кода. Последующие изменения устранили многие конкретные контрпримеры, но заявление «A01–A16 закрыты» преждевременно. В текущем коде воспроизводятся ошибки границ измерения, валидации PostTune и проверки происхождения результатов. До их устранения нельзя уверенно локализовать пять заявленных cold-неуспехов исключительно в морфогенезе.

Это аудит кода и доказательств, а не реализация алгоритмических исправлений. Производственные алгоритмы в рамках этой проверки не менялись. [План исправлений и исследований](PLAN.ru.md), [машинный статус](status.json), [воспроизведение](../../../Scripts/audit-probes/review-20260924/README.md).

**Актуальные cold-результаты после remediation (постановки + цифры, без V1–V6):** [EXPERIMENTS_AFTER_FIXES.ru.md](EXPERIMENTS_AFTER_FIXES.ru.md).

## 1. Срезы и метод

Сопоставлены исходный отчёт в root **23e4e8231e2bd1c7201f724fd5510f824c229dad** и все восемь последующих root-коммитов до **14286c9ebf80193a3436790850ba39e3844fbe44** включительно. Код для исторической проверки взят из gitlinks исходного аудита, а не из сегодняшнего дерева.

| Репозиторий | Срез исходного аудита | Проверенный текущий срез |
|---|---|---|
| PulseLib | 17854a4fabd53841d8840d382a2186ba1cadbd80 | d4149190aa30a99366eb453bd69306a0278c34f9 |
| Bin | d2361191bdcc582e82eb1071571d185f6b35c79f | 9733281ccaf660785d4a77f95fcfd7cc82f392ca |
| Rdk | aeedfb80d9d34d5c7a1cd25bfad042ec0362f1f7 | c503a04090ea7aa8c4cd09f4abe8d86d68cd66d3 |

MotionControl, Basic, CvBasic и Hardware с исходного аудита не изменились. Полные SHA, журналы всех коммитов, diffstat и начальное рабочее состояние: [inventory.json](evidence/inventory.json). На момент проверки tracked-файлы указанных репозиториев соответствовали HEAD; существующие untracked IDE-файлы, Bin/settings и pycache не использовались как доказательства и не включались в изменения.

Проверка включала чтение исходных/новых тел функций, повторную сборку штатных probes, дополнительные контрпримеры на извлечённых производственных функциях и анализ сохранённых исследовательских файлов. SHA проверенных исходников: [source-sha256.json](evidence/source-sha256.json). Адаптеры заменяют framework, время, входные сигналы и I/O; это **не полная симуляция Rdk**. В Python-проверках run_case подменены внешние Train/gate, а проверяемая логика приёмки исполняется непосредственно.

Свежий полный Console/cold replay здесь не выполнялся. Linux Console с объявленным SHA и каталоги семи новых runs отсутствуют в доступной checkout. Отсутствие артефактов не доказывает, что разработчик не запускал моделирование.

**Согласованные ограничения:** A07 — принятая калибровка и оценка на текущей Matrix, sample 0 является target. Это не ошибка; обязательного held-out нет. A12 остаётся отложенным при достаточно малом шаге; замена интегратора/guard не входит в план.

## 2. Был ли корректен первоначальный аудит

| ID | Вывод для кода на момент 23e4e823 | Состояние после доработок |
|---|---|---|
| A01 | Подтверждён: ранний ответ при первом стимуле; N=3 не распознаётся как полный паттерн | Основной путь исправлен; переход с неполного sample остаётся ошибочным, R01 |
| A02 | Подтверждён: timely fire закрывает trial до late-спайка | Старый пример исправлен; полное late-наблюдение при смене sample не обеспечено, R02 |
| A03 | Подтверждён: mutable class меняет метку незакрытого trial | Метка теперь immutable; неверная принадлежность новому sample возможна через R01 |
| A04 | Подтверждён: один spike покрывает несколько stimulus windows | Исправлен injective matching; отдельный край N=1 требует согласования метрик, R07 |
| A05 | Подтверждён: семь скрытых foil-spikes дают ложные 8/8 | Foil FP исправлены; полнота schema/target validation и legacy-версионирование остаются, R07 |
| A06 | Подтверждён: max(ISI) вместо реального конца sum(ISI) | Исправлен для представимых полных ISI; общая поддержка N>5 через старый CSV не доказана, R07 |
| A07 | Особенность по решению владельца, не дефект | Принята, без изменений |
| A08 | Подтверждён с прежней оговоркой: Branch уже защищал finite bad landscape, но не NaN; TL inference был слабее | Helper исправлен, сборщик/timeout/lifecycle остаются некорректны, R03–R04 |
| A09 | Подтверждён: TL best/metrics mismatch; Branch уже делал best reprobe, но ошибался на failure/fallback | Добавлены TL reprobe, setup failure и invalidation после fallback; основные описанные пути исправлены, сквозная корректность зависит от R03–R05 |
| A10 | Подтверждён: несовпадение измеряемого сигнала между режимами и фазами | Частично исправлен, R05 |
| A11 | Подтверждён: буфер давал N+1 вместо N тактов | Конкретный off-by-one исправлен; тест N=2 проходит |
| A12 | Математический пример верен вне принятого диапазона шага | Отложен, не блокирует |
| A13 | Обоснован статической цепочкой Build/Ready/setters; исходный отчёт правильно ограничивал утверждение прототипом | Явный ApplyElementDefaults исправляет регистрацию; полный Storage/XML runtime не проверен |
| A14 | Подтверждён пересечением узкого прямоугольника между точками дискретной проверки | Исправлен для отрезков; adversarial probe и 13 существующих GUI-тестов проходят |
| A15 | Обоснован чтением таймера/exit flag; исходный отчёт не выдавал это за runtime-тест CLI | Latch/stop и effective AppCore flag исправляют описанный однократный CLI-запуск; GUI-тесты этого не проверяют |
| A16 | Подтверждён: unchecked gate rc, старые outputs, нестрогие ожидания, неверная provenance | Существенно улучшен, но остаются принимаемые неверные результаты и stale-input пути, R06 |

Исторические и текущие analyzer-пробы показывают: early fire **1→0**, N=3 fire **0→1**, timely+late count **1→2**, label **0→1**, morphology **per_stim→single**. [Исторические результаты](evidence/analyzer/analyzer-historical.txt), [текущие](evidence/analyzer/analyzer-current.txt). Для A05 реальные историческая/текущая Python-функции дают **fa 0→7, acc 8→1, ok_audit 1→0**: [входы и результаты](evidence/analyzer/metrics-historical-current.json).

Исторические PostTune-пробы воспроизводят TL mid=.35 при target=.5 и foils=.2,.6; Branch в этом finite-сценарии правильно сохраняет silent=1. Branch с NaN-foil выдаёт mid=.495. TL применяет выбранные Tips без нового probe, Branch запускает probe; после отката Branch сохраняет rejected metrics. [Исторические результаты](evidence/posttune/historical_results.txt).

Нужно сохранить две поправки к интерпретации первоначального аудита:

1. Уже снятый в 23e4e823 тезис «diff с чужим Keep-клоном противоречит search_reverted» неверен. Откат проверяется относительно собственного snapshot. В настоящем отчёте этот тезис не используется.
2. Изолированные FAIL доказывали конкретные ошибки, но не измеряли их частоту во всех исторических опытах. Исходный аудит корректно не объявлял все сохранённые результаты ложными. Его MD-проверка не была исчерпывающей: в Architecture.md оставались два неверных раскрытия LTZone как long-term potentiation; сейчас они исправлены.

## 3. Подтверждённые текущие проблемы

### R01 — P2: граница нового sample зависит от полноты старого

Источник: [NPatternResponseAnalyzer.cpp](../../../Libraries/Nmsdk-PulseLib/Core/NPatternResponseAnalyzer.cpp), ACalculate, ветки смены sample и stim_edge. Условие немедленного закрытия по sample id применяется при отсутствии нового stimulus edge. Если предыдущий trial неполон, coincident первый стимул нового sample попадает в AppendStim старого trial.

Контрпример с тремя наблюдёнными из четырёх старых стимулов: dataset уже sample 1/class 0, но новый stimulus становится четвёртым стимулом sample 0/class 1; simultaneous output получает fired=1 у старого target. Immutable label не устраняет неверную принадлежность. Это условный граничный сценарий coincident sample advance/stimulus edge. Обычный NDatasetBase гасит генераторы при переходе; частоту и достижимость совпадения в полном scheduler этот probe не устанавливает. Считать его доказанной причиной штатного cold FAIL нельзя.

Нужно обрабатывать смену sample id до событий, независимо от complete/stim_edge; явно завершать неполный старый trial как invalid/incomplete и открывать новый. [Воспроизведение](evidence/analyzer/analyzer-boundaries.txt).

### R02 — P1: смена sample молча обрезает заявленное окно наблюдения

Источник: тот же ACalculate; [NDatasetBase.cpp](../../../Libraries/Nmsdk-PulseLib/Core/NDatasetBase.cpp), границы samples; EffectiveDatasetDelaySec обоих учителей. Deadline analyzer и dataset delay не связаны общим контрактом.

При last stimulus=.06 и LateResponseWindow=1.5 deadline равен 1.56. Dataset advance в .31 закрывает trial в .31. Neuron edge в .4 до первого стимула следующего sample в .5 не записан ни в один trial. Старый контрпример A02 внутри неизменного sample исправлен, но полное окно в новых MD обещано без основания.

Не следует автоматически приписывать активность нового sample старому. Нужно выбрать явный контракт: гарантировать межsample-интервал для полного окна либо регистрировать фактическое окно, censored/incomplete и самостоятельные события до первого стимула. Обрезанный trial не должен молча подтверждать отсутствие foil-ответов за полный заявленный интервал. [Воспроизведение](evidence/analyzer/analyzer-boundaries.txt).

### R03 — P1: неполный или NaN free-run превращается в пригодный mid

Источники: [TL](../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.cpp), UpdatePostTuneFreeRunPeak 3797+, FinalizePostTuneMid 3930+; [Branch](../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.cpp), UpdatePostTuneFreeRunPeak 4201+, FinalizePostTuneMid 4480+.

Проверка isfinite в LandscapeOk полезна, но применяется после накопления максимумов. NaN во входном amp не проходит сравнение amp>max и исчезает, оставляя конечный 0. Неизмеренный foil также представлен 0; visited/valid mask отсутствует.

| Сценарий реального Update + Finalize | TL | Branch |
|---|---|---|
| Timeout до измерения foil, target=.5 | Result=Success, Complete=1, mid=.25 | Result=Timeout, Complete=1, mid=.25 |
| NaN в foil trace после target=.5 | Result=Success, mid=.25 | Result=Success, mid=.25 |

Branch присваивает Timeout, но Finalize всё равно применяет recognition threshold. TL даже не переводит timeout в соответствующий Result. Это отдельный дефект валидности измерения, не отложенный A12.

Нужны per-sample observed/finished/finite flags, invalidation при любом нечисловом измерении и запрет применения mid на неполном/timeout/invalid run. Нули должны означать измеренный нулевой ответ, а не отсутствие данных. [Скомпилированные контрпримеры](evidence/posttune/results.txt).

### R04 — P2: PostTuneResult переживает новый цикл обучения

В SetIsNeedToTrain, reset/входах в PostTune обоих учителей сбрасываются другие служебные состояния, но не PostTuneResult. Для конечных метрик Finalize записывает Success/NonSeparable только при прежнем None; InvalidMetrics присваивается безусловно. После прежнего Success и нового nonseparable [.5,.6] оба учителя сохраняют **Result=Success при silent mid=1**. Обратная последовательность может оставить старую ошибку после нового успешного измерения.

Статическая цепочка повторного обучения того же объекта не сбрасывает Result; отдельный новый процесс для каждого опыта снижает риск. Сам probe вызывает Finalize с прежним Result, а не моделирует два полных физических цикла. Сбрасывать состояние результата при начале нового attempt; отделить termination status от validity и результата конкретной калибровки. [Контрпример](evidence/posttune/results.txt).

### R05 — P2: PostTrainMidMetric всё ещё не имеет единого смысла

В Branch ReadPostTuneLiveMetric теперь учитывает mode, но ACalculate 5577–5580 перед UpdatePostTuneFreeRunPeak всё равно пишет soma_amp в общий PostTuneLiveSomaMax. При mode=LTZ, LTZ=.2 и soma=.8 получается peak=.8. Значит правка mode-aware helper недостаточна.

В TL ReadPostTuneProbeMetric 3612+ для Soma теперь возвращает мгновенную сумму потенциалов на момент завершения итерации, тогда как free-run накапливает максимум суммы во времени. Прежняя сумма отдельных максимумов заменена другой величиной, а единый objective не получен. Пример: сумма на конце окна .1 и пик суммы .5 дают разные оценки одного паттерна. Последующий reprobe уменьшает риск применения плохого best, но не делает поиск оптимизацией заявленной метрики.

Нужен один collector и явно заданная величина для каждой пары learner/mode на iteration/search/free-run. Branch Auto=Soma и TL Auto=LTZ — допустимые разные defaults. Ошибки явных режимов не доказаны причиной всех текущих cold FAIL. [Branch mode-контрпример](evidence/posttune/results.txt).

### R06 — P1: verifier ещё допускает чужие/незавершённые результаты

Источники: [posttune_verify.py](../../../Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py), wait_need0 367+, run_case 621–812; [phase9_preinh_bc_gate.py](../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityAsymRm/scripts/phase9_preinh_bc_gate.py), overlay_train_params 35–46 и main 215–221.

**Старый Test mid.** Run очищает Train-флаг, но сохраняет Test-флаг. Phase9 переносит в новые параметры любой старый mid<.9, затем пропускает новую inference-калибровку. В git уже лежит Asym50 Test/posttune_complete.flag от 22 сентября: mid=.0116458, inference=1, landscape_ok=1, без Result. Подстановка именно этого файла в реальный overlay с новым silent Train возвращает .0116458; mid_source_of называет его cpp. Таким образом cpp не доказывает свежесть калибровки под новые веса.

**Незавершённая Train / неверный Search.** С благополучным внешним gate реальный run_case даёт exit=0 в трёх недопустимых случаях: search_reverted=1, но final TipR отличается от собственного snapshot; Search без Train flag/snapshot при Need=1/status=exited; Keep с произвольными весами при Need=1/status=incomplete. Классы keep/search выводятся из ожидаемого имени, а не из полного постусловия. diff_after_revert и unknown не запрещены.

**Старый live salvage.** posttune_tipr_live.txt не очищается перед Train. После нового child crash rc=9 wait_need0 может записать старые TipR/L из live в Parameters и вернуть exited. Это повторный-run путь; в начальной checkout такого live-файла не найдено.

Есть и более узкие validation-пробелы: NaN TipR сравнивается как равный, -inf mid определяется как cpp, пустой fires не проходит обязательное сравнение ожидания. Последний сценарий использует подменённый успешный gate; штатные дочерние gates обычно сами проверяют наличие CSV. Не следует ставить его доказательность выше реального tracked stale-флага.

Нужен единый validator полного run, исполняемые чистые каталоги и текущие run-id/weights/config hashes у Train/Test. Отдельно сохранить режим inherited/smoke и контролируемый salvage, не повышая их до завершённого cold-обучения. [Входы/выходы](evidence/research/a16-boundary-fixtures.json).

### R07 — P2: контракт Python-метрик и CSV остаётся неполным

Источники: [selectivity_metrics.py](../../../Bin/Configs/SpikeSamples/StructTrain/scripts/selectivity_metrics.py), classify/classify_trial_morphology; [audit_structtrain.py](../../../Bin/Configs/SpikeSamples/StructTrain/scripts/audit_structtrain.py), last_pulse_ok; CSV writer analyzer.

Оригинальные A04–A06 контрпримеры исправлены. Но schema_ok=1/ok_audit=1 возможны при противоречивом target fired=1, count=0, t_rel=-1 или при spike_times=nan. Это проверка повреждённых/несогласованных входов, **не доказательство, что текущий analyzer штатно пишет такие строки**. last_pulse_ok отдельно отвергает часть таких данных; classify не обеспечивает его автоматически.

Для корректного N=1 single response classify_morphology объявляет per_stim, ok_audit=0, а last_pulse_ok возвращает 0 из-за пустого ISI. N>5 не может быть полностью представлен четырьмя isi-полями старого CSV. Следовательно обещание общей поддержки N=1,2,3,4,5,8 из плана ещё не подтверждено сквозным тестом.

Новое ok_audit_legacy не является точным воспроизведением старой функции: для семи hidden foil-spikes исторический ok_audit=1, новое поле ok_audit_legacy=0, поскольку оно использует уже изменённые strict-поля. Нужно либо сохранить настоящий исторический scorer, либо переименовать поле и документировать версию. [Контрпримеры](evidence/analyzer/metrics-counterexamples.json), [историческое сравнение](evidence/analyzer/metrics-historical-current.json).

## 4. Исправления, которые следует сохранить

Dataset metadata/Branch binding, immutable label, запрет раннего fired, продолжение наблюдения после timely fire, injective matching и учёт всех записанных foil-spikes — полезные исправления. Правильны глобальный gap относительно максимального foil, finite check helper, защитный silent для invalid inference, TL best reprobe, явный setup failure финального Search free-run, очистка rejected metrics после fallback и численное сравнение TipR.

Gap для scalar-метрики обязан учитывать **все** foils: target=.5, foils=.2,.6 не допускает разделяющего порога, даже если между .2 и .5 можно вычислить число. Поэтому предположение NEXT_PLAN «LandscapeOk слишком строг» нельзя использовать для ослабления условия, чтобы получить зелёный gate. Сначала проверяется выбранный сигнал и полнота замера.

NAxoneDelay исправляет точный off-by-one. Внесённая дополнительно такая же правка NPulseDelay не устраняет его старый pass-through при |DelayTime|<.001; утверждение RECONCILE «оба всегда дают N ticks» шире проверенного. Прототип Preinh теперь явно применяет defaults. Router использует геометрическое пересечение отрезка. Console прекращает повторный Save и учитывает effective exit flag. Полный runtime-регистрационный/CLI цикл в этом аудите не запускался.

Повторно собранные штатные цели ([журнал сборки](evidence/build-output.txt)): [GUI 13/13](evidence/audit_existing_gui.xml), [CE 9/9 без A12](evidence/audit_counterexamples.xml), [Branch 8/8](evidence/audit_branch_update.xml). Штатные Python unit tests verifier: [15/15](evidence/verifier-unit.txt). Их прохождение воспроизведено; оно не покрывает R01–R07. Особенно важно: Branch probes извлекают Finalize/Handle, подменяя setup/live sampling; поэтому они не замечают R03/R05. GUI-тесты не являются проверкой Console.

## 5. Что можно заключить об исследованиях

Сводка разработчика сообщает **2/7 PASS**: asym50 и br100_search; остальные пять FAIL. Это честнее заявления о полном завершении V1–V6, но уровень доказательств недостаточен для независимой приёмки:

- В семи case-каталогах между аудитом и текущим Bin изменились только README. Model/Parameters/старые CSV/flags не заменены новыми run-артефактами; у Asym25/50 Test CSV нет. [Инвентаризация](evidence/research/artifact-inventory.json).
- _repro/runs и новый Linux Console отсутствуют локально. Записанный SHA идентифицирует заявленный бинарник, но без build manifest не связывает его с полным деревом исходников и настройками сборки.
- Provenance_SOURCE_REL хеширует пять cpp, но пропускает обычный NNeuronTimeLearner.cpp, headers и Python/gate-скрипты. Одного Parameters hash недостаточно для Model, Matrix и преобразований Train→Test.
- Времена некоторых runs предшествуют коммиту FixedLTZ soft_cold fix. Это не доказательство старого кода: изменения могли быть в рабочем дереве. Нужны конкретные per-run hashes/inputs. Аналогично mtime Console за 15 секунд до commit d414919 не доказывает устаревший бинарник.
- br100_search PASS с search_reverted подтверждал бы работоспособность fallback, если артефакты свежие; он не доказывает, что Search улучшил решение.
- Ожидание phase6_480 в CASES — fires=10000010. Это регрессия известного поведения с одним foil FP, а не строгая избирательность 8/8. В отчёте нужно различать regression-pass и strict calibration-quality.

Gold Branch25 с mid≈.0718 и Branch100 с mid≈.00718 — разные контроли, а не ошибка масштаба сама по себе. NEXT_PLAN не уточнял case у gold-сравнения. Успех inherited gold и неуспех soft_cold **не локализуют причину только в retrain**: различаются веса, flags, reset, timing, перенос Train→Test и калибровка. R02/R03/R06 дают альтернативные причины, которые сначала надо исключить.

soft_cold FixedLTZ=1 исправляет конкретную утечку recognition threshold в обучение. Это полезно, но soft_cold поверх fat Model не равен полной новой инициализации. Идущий морфогенез после reset ещё не доказывает корректность итоговых весов/калибровки. Причины пяти FAIL остаются исследовательскими гипотезами.

В рамках этого аудита **не подтверждена и не опровергнута сама численная сводка 2/7**; показано, почему доступные доказательства и текущий harness не позволяют принять её как проверку всего исправленного HEAD.

## 6. Изменение NEXT_PLAN и документации

Исходный NEXT_PLAN в 14286c9 полезно выделял cold fail-list и предлагал сравнить длины, TipR, timing и landscape. Ошибочны были общий статус закрытия дефектов по probes, вывод об однозначной локализации в переобучении и условие «пока probes PASS, повторный remediation не нужен».

Обновлённый [план](PLAN.ru.md) сначала закрывает R01–R07 и обеспечивает проверяемый протокол, затем проводит контролируемое сравнение gold/fresh weights и только после этого исследует морфогенез. Старые работающие исправления повторять не требуется.

Исправлены текущие контракты Analyzer/PostTune/Verify, указатели на новый аудит и семь README экспериментальных клонов. Старые gold PASS отделены от developer-reported cold verdict. В PulseLib Architecture исправлено раскрытие LTZone. Исходный отчёт и after-fixes status сохранены как исторические снимки с явной ссылкой на настоящую переоценку; это не переписывание результатов прошлых запусков.

## 7. Практический статус

Из 14 активных исходных ID конкретные дефекты A03/A04/A05/A06/A09/A11/A13/A14/A15 исправлены полностью либо в указанном узком пути; A01/A02/A08/A10/A16 имеют подтверждённые остаточные сценарии. Для A05/A06/A09 сохраняются дополнительные ограничения сквозного контракта, указанные выше. Это не подсчёт независимых багов: R01–R07 пересекают старые ID.

Следующий значимый результат — не ещё одна таблица PASS, а минимальный воспроизводимый run с полными наблюдениями, доказанно свежими weights/mid и явными причинами завершения. После этого неуспех структурного обучения можно будет отделить от неуспеха измерения или проверки.
