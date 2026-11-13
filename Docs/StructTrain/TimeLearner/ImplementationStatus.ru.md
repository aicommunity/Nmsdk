# Состояние реализации TimeLearner — 13.11.2026

Полностью принят исходный этап0. Этапы1–12 частичны: адресные проверки и реальные эксперименты существуют, но полная обязательная матрица и завершение миграции не приняты. Научный результат8/8 не является условием завершения; количество инженерных PASS не доказывает работу классификатора. Источники требований: [утверждённый план](RefactoringPlan.ru.md), [исходный аудит](PlanCompletionAudit-2026-10-25.ru.md).

## Последний завершённый Train и текущее задание

[Cold Branch N4/N1 coupled-search](ValidationPlans/M40N1CoupledBranchTrainA1-20261113/RESULT.ru.md) завершён: production1/1 PASS, native/outer closed. Один реально измеренный кандидат input2 одновременно удовлетворяет timing/amplitude допускам; следующий input1 дал5 ambiguous rejections. Итог invalid_observation, certificate=null, all-input verification отсутствует. Это локальный прогресс относительно прежних0 jointly-ready, не работа всей модели/классификатора.

Source SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8, runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. Actual job/initial bytes равны baseline; scientific limits не изменены. SDK A4[93/93](ValidationPlans/M40N1CoupledSdkA4-20261113/RESULT.ru.md) принята адресно; A1/A2/A3 failures сохранены. Этапы1–12 остаются частичными.

Сейчас строится read-only отчёт групп48/58 с actual input overlays; полные первичные данные упакованы для Git, графическая галерея остаётся кэшем M40. Следующий научный шаг — frozen diagnostic8pattern evaluation фактического остановленного состояния без completed-training claim и template fallback.

## Последние научные результаты

| Результат | Что подтверждено | Ограничение |
|---|---|---|
|[Same-budget Branch N1 local turn](N1LocalTurnScientificReport-20261113.ru.md)|Train completed/valid, unit1/1;52 consumed candidates/55 domains/105 search probes. На[26,26,25,1] Rs86M и2.880071555M дают противоположные amplitude residuals при обоих timing-valid. Job/initial bytes совпадают с baseline; первые600 CSV равны. Четыре temporal originals с omission controls просмотрены.|BudgetExhausted, certificate=null;5 timing-ready,0 jointly-ready, поиск только input2. Классификация не измерялась. Последний unconsumed graph не становится лучшим кандидатом.|
|[Actual Classic fixed threshold](ActualThresholdScientificReport-20261113.ru.md)|Два completed/valid native runs,16 полных observations, модель неизменна. При фиксированном0.013048873000159292:TP1/FP2/FN0/TN5. Все8 LT overview, target zoom, target Soma1 и два выбранных details просмотрены.|Target0.2645s раньше последнего входа0.49s;3 из4 событий относятся к foils. Это Same-Matrix partial6/8 остановленной модели, не completed-pattern detection/завершённое обучение. Общий acquisition test FAILED при cleanup; исправление не делает исходный тест PASS.|
|[Branch shared-bank Rs](BranchSharedBankScientificReport-20261113.ru.md)|Matched replay86M и coherent bank21.5M при[27,27,27,1], общий Soma1 max0.005456576369859967→0.02235560254260882. Все3 выбранных waveform originals просмотрены.|Глобальный максимум не assigned-input certificate. Нет доказательства обучения либо классификации.|
|[L14→L15 и потеря assignment](L14L15AssignmentTransitionScientificReport-20261113.ru.md)|Реальные full/omission controls показывают4→3 вершины; [L22 Rs study](L22BurstResistanceScientificReport-20261113.ru.md) усиливает сигнал, но не восстанавливает отдельную вершину на четырёх Rs.|Не менять смысл закреплённого импульса ради положительного verdict.|
|[Исторический август](HistoricalAugustColdStart.ru.md), [order/ITI](HistoricalFrozenProtocolMatrixScientificReport-2026-11-07.ru.md)|Сохранены рабочие4/8–6/8 исходного протокола, cold/replay и отдельная frozen protocol matrix.|Современные отрицательные результаты не отменяют исходные визуальные наблюдения. Проверки одной frozen модели не доказывают универсальную устойчивость обучения.|

## Первичные данные и воспроизводимость

- [Branch local-turn whole primary44.21MB](ValidationPlans/M40N1LocalTurnPrimaryA1-20261113/RESULT.ru.md):2175 regular files+2 aliases, включая модели/summary/652 CSV и terminal partial material. Независимый restore этого нового пакета ещё не принят.
- [Прежний Branch full-domain44.06MB](ValidationPlans/M40BranchFullDomainPrimaryA1-20261113/RESULT.ru.md):[независимый Elder restore/audit1/1](ValidationPlans/ElderBranchFullDomainPrimaryReplayA2-20261113/RESULT.ru.md), corrupt extracted CSV отвергнут.
- [Branch Rs whole primary27.42MB](ValidationPlans/M40BranchSharedBankPrimaryA2-20261113/RESULT.ru.md):[restore2087regular files и3 DATA audits1/1](ValidationPlans/M40BranchSharedBankPrimaryReplayA1-20261113/RESULT.ru.md).
- [Threshold whole primary56.37MB](ValidationPlans/M40ThresholdPrimaryRecompressionA2-20261113/RESULT.ru.md):точное сохранение uncompressed tar,881-file production restore1/1,1931.572s; первичные size failures сохранены.

Git содержит compact primary/models/metrics/selected figures. Полные PNG/SVG/PDF galleries — воспроизводимый M40 cache. Raw receipts сохраняются побайтово; ns timestamps не проходят через binary64 JSON rewrite.

## Проверенное состояние

| Область | Фактический результат и граница вывода |
|---|---|
| Предшествующий SDK полного Classic Train | Root92ad93cdf453967ac29108a9bbef5fd3905da59d / Pulsedfb9a98244f91b4f4029d8470465fd40116436ca. Свежие сборки и publication7: [M407/7](ValidationPlans/M40PublicationReceiptSdkA1-20261113/RESULT.ru.md), [Elder7/7](ValidationPlans/ElderPublicationReceiptSdkA1-20261113/RESULT.ru.md), процессы закрыты, reservations освобождены. Устранена повторная полная обработка пакета при публикации; [Большой native N4 export завершён в прежнем лимите](ValidationPlans/M40PublicationReceiptBudget16TrainA1-20261113/NATIVE_COMPLETED.ru.md); [Полный внешний DATA audit1/1 принят](ValidationPlans/M40PublicationReceiptBudget16TrainA1-20261113/RESULT.ru.md), whole group closed/lease released. |
| Finalization/DATA перед этим изменением | На Root929/Pulsedfb проверены52 исходных IDs: M40 explicit composition с сохранённым исходным отрицательным контролем; Elder52/52. Это scoped N2 lifecycle/export/frozen-path, не научная N4 сходимость. [M40](ValidationPlans/M40FinalizationRemaining23A1-20261112/RESULT.ru.md), [Elder](ValidationPlans/ElderFinalizationData52A1-20261112/RESULT.ru.md). |
| Stock N4 baseline | [8 actual cold probes](ValidationPlans/M40DataSdkCold8A1-20261112/RESULT.ru.md) complete/valid, физика и граф проверены, LTMembrane отсутствует. Это начальная характеристика, не результат обучения. |
| Предыдущий Classic N4 Train | [Native timeout2100.32s](ValidationPlans/M40DataSdkBudget16TrainA1-20261113/RESULT.ru.md), исходные state/summary сохранены; training=budget_exhausted,62 поисковые пробы/31 изменение, certificate=null. Полный compact primary51.30MB опубликован. Отсутствующий execution не достраивается по сохранённому состоянию. |
| Диагностика этого состояния | [8 полных frozen observations](ValidationPlans/M40Budget16FrozenDiagnostic8A1-20261113/RESULT.ru.md), completed/valid, unchanged model, TP0/FP0/FN1/TN7 при исходном threshold100. Target пропущен. Accuracy7/8 здесь означает только7 правильных молчаний foil. Калибровка не проводилась; работающая классификация не подтверждена. |
| Новый читаемый отчёт | [Восемь паттернов последнего сохранённого budget16 состояния](Budget16DiagnosticScientificReport-20261113.ru.md):32 pair, report2/2,14 просмотренных PNG; полная галерея1803 PNG/SVG/PDF остаётся M40 cache. |
| Более ранний читаемый N4 отчёт | [Classic и Branch:16 диагностических проб,19 просмотренных PNG](RecordedN4DiagnosticScientificReport-20261112.ru.md). Обе остановленные модели при threshold100 молчат. Compact primary28.1MB независимо повторно проанализирован на Elder; это другой снимок моделей. |
| Историческая научная опора | [Августовский cold Train→Test4/8–6/8](HistoricalAugustColdStart.ru.md), [saved-state order/ITI matrix](HistoricalFrozenProtocolMatrixScientificReport-2026-11-07.ru.md). Исходные визуальные наблюдения сохраняют силу для своего протокола; современные отрицательные результаты их не отменяют. |
| Компактное хранение | [Schema2:34/34 проверок M40](ValidationPlans/M40ContentReferencePrimaryA1-20261113/RESULT.ru.md),76.25→38.16MB для двух копий actual qz, byte-exact независимое восстановление. [Explicit384MiB original-model export/restore/rescore10/10 принят](ValidationPlans/M40DeclaredDiagnosticPrimaryA1-20261113/RESULT.ru.md):28 members/320.08MB в19.58MB XZ. [Независимый Elder replay1/1 принят](ValidationPlans/ElderBudget16CompactReplayA1-20261113/RESULT.ru.md), original M40 directories отсутствовали. |


## Приёмка по исходным этапам

| Этап | Подтверждено в ограниченной области | Что ещё требуется для полного этапа |
|---|---|---|
|0. Начальное объединение|Исходные merge commits/develop/gitlinks согласованы.|Новые этапы объединяются children-first через --no-ff после своей полной приёмки; текущая feature не объявлена завершённым develop-релизом.|
|1. Доказательства и параметры|Исторические anchors,217 property declarations и source review, реестры дефектов и режимов.|Обновить семантику изменившихся consumers/helpers и inherited Rdk properties; закрыть audit unknowns и runtime/effective-factor matrix.|
|2. Сборки/runtime|Изолированные source/build/runtime, manifests, owned processes, сохранение и восстановление primary.|Полная build/resource/fault matrix и доступная Git closure всех принятых результатов. [Полный Elder publication7 corpus сохранён](ValidationPlans/ElderPublicationReceipt7PrimaryA1-20261113/RESULT.ru.md):498 members/1.83MB XZ. Независимый semantic7-case replay ещё открыт.|
|3. Наблюдения/scorer|Strict ID/completeness/finite checks, arbitrary dimensions, реальные frozen observations и versioned metrics.|Все применимые исторические adapters/режимы/профили, единый verdict по полной области; распространить единый verdict на оставшиеся режимы; large-model primary прошёл independent Elder replay1/1.|
|4. Lifecycle/storage|Реальные native fixtures, readback графа/порядка/динамики и boundary checks.|Полная fresh/reuse/Copy/Load/Build/growth/heterogeneous physics и compatibility matrix. Не считать Alloc/Copy checkpoint динамики.|
|5. Export/import|Completed/stopped state, storage/graph archive, boundary continuation, fresh destination controls.|Остальные варианты физики/связей, сохранность индивидуальных Rs/C и independent corpus replay. Mid-probe resume не обещается.|
|6. Общий контроллер|Общий native service, configured controller, Classic/Branch adapters.|Оставшийся общий срез, legacy/V2 A/B, дублирующиеся hooks и отдельная multirate verification.|
|7. Алгоритмы|Measured bounded L/Ns/Rs search, N0 repeats, final verification, explicit invalid/budget outcomes.|Полная bounds/quantization/nonmonotonicity/invalid-probe/physics/reset matrix, приёмка bounded C-search, полный разбор stock measurement/search. C-trim по умолчанию Off.|
|8. Recognition/PostTune/calibration|Versioned solo/recognition, transactions, measured threshold confirmation и scoped frozen controls.|Все реализованные PostTune/inhibition/reset modes, commit/rollback/interruption, independent frozen evaluation. Старый Exact не переносится после преобразования.|
|9. Скрипты|Корневой пакет и CLI; manifest357=353 retired+4 moved, complete=false.356 records ранее проверены production CLI.|Production verification357, оставшиеся Bin analysis/matrix/shared tools и callers; общий scope review. Не оставлять wrappers/копии на старых местах.|
|10. Запуск/provenance/publish|Owned groups, leases/budgets, fail-closed publisher, coordinator/ConditionSpec controls.|Полная effective-factor attestation и scheduler/cancel/recovery/publication fault matrix; declared binding не равен effective execution.|
|11. Научные проверки|Исторические replay/cold results; реальные современные отрицательные Train и diagnostic; читаемые временные отчёты прежних снимков.|Продолжить разбор измеренного stock поиска после принятого полного N4 опыта; legacy/V2 A/B, target в каждой позиции, order/ITI/reset, физические профили и independent frozen matrix.8/8 не обязательно.|
|12. Документация|Текущие сводки отделены от истории, исходные наблюдения сохраняются.|Сквозная сверка root/PulseLib/Bin/config/ClDesc/defaults и ссылок после завершения миграции.|


## Следующий научный шаг и ограничения

После принятой A4 сборки выполняется same-budget cold Branch N4/N1. По завершении — анализ фактически потреблённых candidates: изменились ли исследованные длины/Rs, достигнуто ли simultaneous timing/amplitude, сохранены ли остальные входы. Exact требует свежей проверки всех входов. Sign bracket, local timing readiness, Done и завершённый процесс не заменяют это требование. BudgetExhausted/SearchUnresolved не доказывают PhysicalInfeasible.

Дальше остаются legacy/V2 A/B и полная физическая/режимная матрица, frozen order/ITI/reset и согласованные stage merges children-first через--no-ff. Полные открытые требования перечислены выше; этот научный шаг не подменяет их.

При Train используется максимум закреплённого импульса: настоящая слившаяся вершина неоднозначна; раздельная ранняя вершина с хвостовым влиянием допустима. При Test рассматривается полный отклик, причём ранний event до последнего входа выделяется отдельно. Порог подтверждается реальным прогоном.

Build/Calculate/Reset возвращают true; ошибки имеют специализированное состояние. Общая физика задаётся storage-образами и native lifecycle. C-trim Off по умолчанию. SeriesD не возобновляется автоматически. [Готовность и читаемые научные отчёты](ExperimentReadiness.ru.md).

Предыдущая сводка сохранена в Git commit87283983db82aa4df63306af5212a347076cc4f1 по тому же пути. Более ранние записи: [история до publication Train](ImplementationStatus-History-through-20261113-before-publication-train.ru.md). Старые слова «сейчас» относятся к своим снимкам, измерения и исходные outcomes не переписаны.
