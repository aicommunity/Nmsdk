# План рефакторинга TimeLearner

Принят пользователем 25.10.2026. Полная постановка включает код Classic/Branch,
storage physics, измерения, export/import, pipeline и документы. Научный PASS
8/8 не является условием завершения. Нормативные решения: [Decisions](Decisions.ru.md).
Фактическое выполнение: [ImplementationStatus](ImplementationStatus.ru.md).

| Этап | Изменения | Приёмка |
|---|---|---|
| 0 | --no-ff merge текущих PulseLib, Bin, root в develop; согласовать gitlinks | child commits опубликованы до root, чистая closure |
| 1 | evidence ledger с августа, режимы, property inventory, defect status, script blobs | вывод прослеживается до SHA/path, old/new gates разделены |
| 2 | изолированный deploy root для всех targets; runtime manifest; Reports exception | две сборки не перезаписывают runtime, artifacts доступны через Git |
| 3 | строгая схема analyzer/scorer, IDs, completeness, timestamps, arbitrary N; полные soma/stimulus traces для визуальных отчётов | permutation invariant, malformed/incomplete не дают PASS; все soma и фактические входные импульсы доступны без обрезки |
| 4 | native storage/lifecycle fixtures; graph, caches, dt coefficients, reuse/load/growth | одинаковый effective graph и отклик, без learner-specific wakeup Build |
| 5 | ModelSpec + LearnedSoloState + RecognitionState; полный native export/import | asymmetric/heterogeneous roundtrip, обнаружение потерянных узлов/связей |
| 6 | общий event-driven controller и topology adapters без смены цели | compatibility A/B сохраняет решения на контрольных случаях |
| 7 | valid measured peaks; signed residuals; bounded L/N/R searches; revision invalidation; optional C | no-peak, nonmonotonic, bounds, quantization, C/dt и stale-input tests |
| 8 | idempotent parallel conversion, transactional PostTune, honest threshold calibration | save/load/rollback, реальный threshold confirm, frozen hash |
| 9 | единый root Scripts package, CLI, report/plot generator и адресный config adapter; удалить старые scripts | нет wrappers/альтернативных запускателей; история извлекается по manifest; читаемый visual report строится production-командой |
| 10 | typed ConditionSpec, owned worker leases, fail-closed Git publisher; обязательные visual assets | duplicate/crash/timeout/push-failure tests; отсутствие требуемых графиков не позволяет объявить новый отчёт полным |
| 11 | исторический replay, cold, v1/v2 A/B, order/ITI, режимы и модели; визуальная проверка всех паттернов | полные observations, валидные negative и unresolved отдельно; временные графики всех soma с наложенными реальными входными импульсами в читаемом масштабе |
| 12 | актуализировать root/PulseLib/Bin docs и ClDesc; historical errata | одна поддерживаемая спецификация, нет ссылок на удалённый CLI |

## Физика и lifecycle

Build/Calculate/Reset возвращают true. Build→AfterBuild→Reset и Init→Reset
учитываются в реальной среде. Native scheduler рассчитывает детей; controller не
выполняет вложенный Calculate. Изменения применяются до импульса между пробами.
Probe reset затрагивает plant, а не весь learner. Uniform параметры задаются
storage-образами, learned overlay сохраняется после growth/load. Проверяется
конечный граф, internal indices и derived coefficients, а не только XML readback.

## Математическая цель и алгоритм

CapturedPerInput и фиксированный ref N−1 сохраняются. Default amp abs tolerance
1e-5, relative off, min measurable amp 1e-6, SyncTolerance из config (default .02).
Oscillation/slack/dead-tip exit — BestEffort, а не Exact. Модель времени предлагает
кандидата; отсутствующий пик не заменяется модельным доказательством.

```text
capture finalized valid references on declared initial model
measure reference timing
while declared probe/model/wall-time budget remains:
    select Classic round-robin or Branch reverse input
    collect native full-burst observation
    if invalid: bounded recovery or explicit unresolved stop
    propose legal L; evaluate actual timing
    normalize N0 integer count or N1 bounded positive Rs
    invalidate measurements affected by the edit
    commit input with local certificate
fresh verify all inputs, then record certificate for this model hash
```

Bisection не предполагает глобальной монотонности. При нескольких кандидатах
сначала сравниваются нарушения timing tolerance, затем amplitude tolerance,
суммарный нормированный остаток и стоимость edit. Отсутствие bracket или budget
не доказывают PhysicalInfeasible. N0 хранит реальные amplitudes/repeatability и
полный revision; cap 128 оценивается по остатку. N1 проверяет per-input numerical
bounds и суммарные фактические conductances, без требования общего Rs interval.
C-trim off остаётся обязательным baseline. При trim effective persegment C0 не
заменяется parent scalar/fallback; heterogeneous ratios сохраняются.

## Передача и оценка

Model export, parameter overlay и controller checkpoint различаются. Mid-probe
resume не обещается. Экспорт включает morphology, classes/profiles, links, Ns,
TipRs/C, dt, inhibition, targets, threshold provenance и conversion origin.

```text
export Train state → native construct/import/reset → effective graph readback
→ semantic fingerprint comparison → frozen evaluation
```

RecognitionState вычисляется из immutable solo state; повторный conversion не
умножает Rs снова. PostTune snapshots explicit model state, выполняет candidate
probe и commit либо rollback. Сертификат связан с конкретным hash. Same-Matrix
calibration и независимый frozen Test имеют разные protocol IDs. Candidate
threshold подтверждается реальным прогоном; silent 7/8 не объявляется detection.

## Pipeline и интерфейсы

CLI: inventory, preflight, prepare, train, export, calibrate, evaluate, analyze, report,
publish, history. Import не запускает работу. Новые команды вводятся по мере
реализации; отсутствие команды не маскируется пустым успешным stub.

Разделяются ModelSpec, ProbeSpec/Observation, TrainingCertificate, CalibrationResult,
RunManifest и ConditionSpec. Execution, validity, training, calibration, evaluation
считаются независимо. Полные observation IDs/schema/complete/censored обязательны
для нового verdict. Legacy adapters сохраняют unknown вместо выдуманных данных.

Runner: immutable sources/runtime → preflight → reserve → Train → validate →
export/readback → calibration → frozen Test → strict analysis → Git publication.
Diagnostic Test незавершённого Train маркируется отдельно. Publisher проверяет
каждый child push и reachability до root publication. Исторические scripts
удаляются после миграции; manifest хранит repo/fullSHA/path/blob.

## Проверки и merge

Дополнение пользователя 29.10.2026: обязательные визуальные отчёты входят в
приёмку новых экспериментов. Для каждой ожидаемой пробы каждого паттерна и всех
soma нужны крупные временные графики мембранного потенциала с наложенными
фактическими входными импульсами. Полное окно сопровождается увеличенными
фрагментами, достаточными для анализа амплитуд, формы, задержек и узких импульсов.
Мелкая сводная сетка не заменяет индивидуальные читаемые графики.
Проверяемый целевой формат: отдельная панель 1920×960 px и vector SVG/PDF
12×6 дюймов, шрифт не меньше 12 pt; overview дополняется временными zoom-панелями.
На zoom один native timestep должен занимать не меньше 8 px; при длинных
пробах добавляются панели, а не уменьшается масштаб. При общем Y-range,
скрывающем слабый ответ, обязателен подписанный detail с исходными амплитудами.
Приёмка включает открытие реальных рисунков: одного размера файла или DPI
недостаточно для подтверждения различимости импульсов, формы и задержек.
Нормативная детализация: [VisualTestReports](VisualTestReports.ru.md).

Обязательны Classic/Branch, N0/N1, N=1/2/4/>4, mode0/1, storage/load/reuse/growth,
Neuron structure0/1/2, используемые физические классы/LT/inhibition combinations,
2000/20000 Hz, reset/continuous, Ctrim off/on, все PostTune, malformed observations,
order/ITI, worker crash, suffix binaries и Git push failure. Сборки и experiments
только на серверах через jump, результаты только через Git.

Этапы выполняются в отдельных ветках от develop. Merge после приёмки через --no-ff
в изменённых дочерних repo, затем root. Непроверенный этап не объявляется закрытым.
Новые axonal/nonlinear модели и common A* остаются отдельной научной работой.
