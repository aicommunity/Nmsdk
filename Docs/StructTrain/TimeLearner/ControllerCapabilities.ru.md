# Возможности TimeLearner: принятый код и проверяемый кандидат

Сверка06.11.2026. Этот документ отделяет реализованный и объединённый код от
последующего кандидата; он не является полной приёмкой режимов или научным отчётом.

Принятый PulseLib develop: `0ec9193e6620ae2439329eece5ecd6d6f167c70a`.
Проверяемый PulseLib: `12d8c8a41c998ae1516496f716a0ae0f3d312b3e`, compiled root
`2e0618110a9abb48b94f6edc6b63c51f829ec810`. Последний не становится исходником
принятого develop лишь потому, что его результаты опубликованы в корневом Git.
[Сверка20 исходных blobs и ancestry](ControllerCapabilityReconciliation.json)
выполнена по неизменяемым Git commits, без новых численных запусков.

Последующий feature Pulse70f / rootef215 прошёл116 C++ controls на M40,
включая opt-in recovery и общий invalid budget; это отдельный срез, не
ASan-приёмка SDK12d и не merge в develop. Новый typed recovery journal
Pulsea34 ещё не проверен; его Python history-validator прошёл54/54 на каждом
сервере на hypothetical metadata, без native execution proof.
[Exact source, primary и пределы](UnassignedBurstCandidateRecovery.ru.md).

| Возможность | Принятый develop | Проверяемый кандидат / остающиеся ограничения |
|---|---|---|
| Совместимость старых конфигов | ControllerVersion по умолчанию1; V2 включается явно | Полная legacy/V2 A/B и multirate матрица открыты |
| Повторы N0 | Реализованы, адресно приняты; default1, schema2 задаёт>=2; N1 отвергает N0-only repeats | Это повторы измерения кандидата, не независимые случайные обучения; final repeatability и полная физическая матрица открыты |
| Порядок поиска N0 | Измеренная timing-ready геометрия может предложить соседние Ns; fresh исходные допуски сохраняются | Не гарантирует сходимости произвольной физической модели, не равен старому quantization tracker |
| Измеренный поиск L и Rs | Есть bounded measured proposal helpers и обычный ограниченный перебор | Локальный bracket не доказывает глобальной монотонности/PhysicalInfeasible |
| Полный learned-state перенос | Completed/stopped native packages, архив графа/storage и boundary restore реализованы; есть адресные проверки | Stopped не получает сертификата и Test как обученная модель; mid-probe checkpoint не обещается; вся matrix не закрыта |
| C₀ / разрешённые поправки C | Есть physical baseline/edit, owned correction и schema2 learned transfer | Наличие API не доказывает всю owner/growth/physics матрицу |
| Автоматический bounded C-search | В принятом BoundedTrainingConfig отсутствует | В кандидате отдельные TrainingCapacitance/MeasuredCapacitanceSearch и cold schema4; общий срез ещё не объединён |
| Legacy SyncCapacitanceTrim>0 в native Train | Отклоняется | Отклоняется и в кандидате. Новый C-search включается декларацией, а не этим legacy-полем |
| PostTune/calibration | Есть typed фазовые планы, native import/transactions и адресные runtime controls | Public legacy flags не заменяют план; все режимы/прерывания/независимая оценка остаются открытыми |
| Общее управление lifecycle | Общий native service уже есть; часть hooks ещё дублируется | NativeLearnerLifecycle и NativeRecognitionControl выделены в кандидате; полная совместимость не следует из механического выделения |
| Общий invalid budget попытки | Полная приёмка всей области остаётся открытой | Fix Pulse2c7 и последующий70f проверяют общий бюджет search/final sweeps; подготовленный journala34 не входит в PASS116 |
| Неидентифицируемая пачка | Старые конфигурации сохраняют retry/явную остановку | Opt-in AdvanceUnassignedBurst в feature70f прошёл controller/classifier/codec controls; stock cold Train и сквозной audit ещё не приняты |

## Версии схем — разные оси

- `ControllerVersion=1/2` — выбор компонента управления, а не версия архива.
- Cold `ControllerConfiguration` schema1/2 поддерживаются принятым кодом;
  schema2 задаёт повторные измерения N0.
- В кандидате cold schema3 добавляет capacitance_history, schema4 —
  capacitance_search. Эти поля не являются legacy SyncCapTrim* properties.
- Feature cold/summary schema5 объявляет recovery поверх base1..4. Это
  незавершённый формат кандидата; не ControllerVersion5. Full Python audit5
  пока явно отклоняется, а старые1..4 означают прежний retry.
- ModelSpec1/2 — версии физической декларации; одинаковая модель в двух
  сериализациях не является двумя независимыми экспериментами.
- Completed/stopped package schema2 с capacitance_state — перенос C₀;
  это не cold schema2 и само по себе не включение bounded C-search.
- Production job, observation, scorer и runtime manifest имеют собственные
  версии; ни одна из них не подменяет model identity или trial completeness.

## Откуда взялись уточнения статуса

[N0 repeats](N0CandidateRepeats.ru.md) и [порядок кандидатов](N0CandidateOrdering.ru.md)
имеют опубликованные адресные приёмки. Соответствующий repeat merge и fix
boundary summaries являются ancestors принятого PulseLib; первоначальные слова
«пока не объединён» больше не являются текущим статусом этих подэтапов.

[Learned-state API](NativeLearnedState.ru.md), [repeat boundary](RepeatBoundaryState.ru.md)
и [C₀ transfer](CapacitanceStateTransfer.ru.md) реализованы позднее первоначальной
постановки ModelArchive/Configured controller. Cold marker удерживает неверный
путь загрузки, но не означает отсутствия отдельного полного native import.

Для кандидата уже приняты [normal304](SharedSdkNormal304Acceptance.ru.md),
[normal8+133](IntegratedSdkResults-2026-11-05.ru.md),
[ASan build/focused8](SharedSdkASanFocusedAcceptance.ru.md) и
[сквозной инженерный coordinator](IntegratedCoordinatorAcceptance.ru.md).
ASan lifecycle133 ещё не принят. Старый isolated ASan304 относится к SDK802,
поэтому не объявляется ASan PASS нового SDK2e. Последующие merge сохраняют
реальные исходные manifests; merge SHA не подставляется задним числом.

Новые эксперименты должны сохранять точный root/child/runtime и действующего
владельца каждого параметра. Успех загрузки UProperty не доказывает влияние
фактора: например, legacy IterationGap не задаёт V2 протокол, а SynapseClassName
не заменяет выбор реальных storage-образов. Полный production factor preflight
остаётся открытым. Все исходные этапы1–12 частичны;8/8 не условие рефакторинга.
