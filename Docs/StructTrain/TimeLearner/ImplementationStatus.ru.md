# Состояние реализации TimeLearner — 13.11.2026

Полностью принят исходный этап 0. Этапы 1–12 выполнены частично: общий native контур и существенные адресные проверки существуют, но полная обязательная матрица и завершение миграции ещё не приняты. Число успешных инженерных тестов не является доказательством работающего классификатора.

Это текущая сводка. [Все прежние записи сохранены без изменения исходных байтов](ImplementationStatus-History-through-20261113-before-publication-train.ru.md). Их слова «сейчас», «следующий» и «не реализован» относятся к моменту записи. Область полного задания определяют [утверждённый план](RefactoringPlan.ru.md) и [аудит полноты](PlanCompletionAudit-2026-10-25.ru.md), а не только таблица ниже.

## Проверенное состояние

| Область | Фактический результат и граница вывода |
|---|---|
| Последний принятый SDK для нового запуска | Root92ad93cdf453967ac29108a9bbef5fd3905da59d / Pulsedfb9a98244f91b4f4029d8470465fd40116436ca. Свежие сборки и publication7: [M407/7](ValidationPlans/M40PublicationReceiptSdkA1-20261113/RESULT.ru.md), [Elder7/7](ValidationPlans/ElderPublicationReceiptSdkA1-20261113/RESULT.ru.md), процессы закрыты, reservations освобождены. Устранена повторная полная обработка пакета при публикации; [Большой native N4 export завершён в прежнем лимите](ValidationPlans/M40PublicationReceiptBudget16TrainA1-20261113/NATIVE_COMPLETED.ru.md); полный внешний DATA audit ещё выполняется. |
| Finalization/DATA перед этим изменением | На Root929/Pulsedfb проверены52 исходных IDs: M40 explicit composition с сохранённым исходным отрицательным контролем; Elder52/52. Это scoped N2 lifecycle/export/frozen-path, не научная N4 сходимость. [M40](ValidationPlans/M40FinalizationRemaining23A1-20261112/RESULT.ru.md), [Elder](ValidationPlans/ElderFinalizationData52A1-20261112/RESULT.ru.md). |
| Stock N4 baseline | [8 actual cold probes](ValidationPlans/M40DataSdkCold8A1-20261112/RESULT.ru.md) complete/valid, физика и граф проверены, LTMembrane отсутствует. Это начальная характеристика, не результат обучения. |
| Предыдущий Classic N4 Train | [Native timeout2100.32s](ValidationPlans/M40DataSdkBudget16TrainA1-20261113/RESULT.ru.md), исходные state/summary сохранены; training=budget_exhausted,62 поисковые пробы/31 изменение, certificate=null. Полный compact primary51.30MB опубликован. Отсутствующий execution не достраивается по сохранённому состоянию. |
| Диагностика этого состояния | [8 полных frozen observations](ValidationPlans/M40Budget16FrozenDiagnostic8A1-20261113/RESULT.ru.md), completed/valid, unchanged model, TP0/FP0/FN1/TN7 при исходном threshold100. Target пропущен. Accuracy7/8 здесь означает только7 правильных молчаний foil. Калибровка не проводилась; работающая классификация не подтверждена. |
| Новый читаемый отчёт | [Восемь паттернов последнего сохранённого budget16 состояния](Budget16DiagnosticScientificReport-20261113.ru.md):32 pair, report2/2,14 просмотренных PNG; полная галерея1803 PNG/SVG/PDF остаётся M40 cache. |
| Более ранний читаемый N4 отчёт | [Classic и Branch:16 диагностических проб,19 просмотренных PNG](RecordedN4DiagnosticScientificReport-20261112.ru.md). Обе остановленные модели при threshold100 молчат. Compact primary28.1MB независимо повторно проанализирован на Elder; это другой снимок моделей. |
| Историческая научная опора | [Августовский cold Train→Test4/8–6/8](HistoricalAugustColdStart.ru.md), [saved-state order/ITI matrix](HistoricalFrozenProtocolMatrixScientificReport-2026-11-07.ru.md). Исходные визуальные наблюдения сохраняют силу для своего протокола; современные отрицательные результаты их не отменяют. |
| Компактное хранение | [Schema2:34/34 проверок M40](ValidationPlans/M40ContentReferencePrimaryA1-20261113/RESULT.ru.md),76.25→38.16MB для двух копий actual qz, byte-exact независимое восстановление. [Explicit384MiB original-model export/restore/rescore10/10 принят](ValidationPlans/M40DeclaredDiagnosticPrimaryA1-20261113/RESULT.ru.md):28 members/320.08MB в19.58MB XZ. [Независимый Elder replay1/1 принят](ValidationPlans/ElderBudget16CompactReplayA1-20261113/RESULT.ru.md), original M40 directories отсутствовали. |

## Подтверждённые живые задания

Пути на M40 относятся к /media/user/Data/TimeLearnerRefactor/readbacks. Состояние «выполняется» ниже подтверждено живыми процессами в этой сессии, но не является итоговой приёмкой.

| Job | Задача | Подтверждённый handle |
|---|---|---|
| s07-publication-receipt-budget16-train-m40-a1 | Native completed/exit0 за2070.92s, state/summary/execution записаны; training=budget_exhausted, L22,1,1,1, certificate=null. [Native первичные записи](ValidationPlans/M40PublicationReceiptBudget16TrainA1-20261113/NATIVE_COMPLETED.ru.md). Внешний DATA audit ещё выполняется. | Outer2653098/start361127390; native2660868 закрыт. |

Повтор использовал тот же математический job и другой Console runtime; во время native Train параллельно работали два Python аудита на M40. Это последовательная инженерная проверка, не изолированный timing benchmark. При timeout не увеличивать бюджет и не запускать автоматический повтор.

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
|11. Научные проверки|Исторические replay/cold results; реальные современные отрицательные Train и diagnostic; читаемые временные отчёты прежних снимков.|Закончить внешний DATA audit текущего N4 опыта; legacy/V2 A/B, target в каждой позиции, order/ITI/reset, физические профили и independent frozen matrix.8/8 не обязательно.|
|12. Документация|Текущие сводки отделены от истории, исходные наблюдения сохраняются.|Сквозная сверка root/PulseLib/Bin/config/ClDesc/defaults и ссылок после завершения миграции.|

## Следующий критерий решения

После завершения нового Train проверить native execution, полный model/summary, архив проб и исходные остатки; затем решить по фактическому outcome. Exact требует свежей проверки всех входов в исходных допусках. BudgetExhausted/SearchUnresolved не доказывают PhysicalInfeasible. Увеличение бюджета или автоматическая замена назначенного пика максимумом пачки не являются исправлением.

При обучении выбирается максимум закреплённого импульса: слившаяся вершина неоднозначна, раздельная ранняя вершина с хвостовым влиянием допустима. При Test рассматривается полный отклик паттерна. Порог подтверждается настоящим прогоном; offline maxima не заменяют spiking evaluation.

[Готовность научных экспериментов](ExperimentReadiness.ru.md). Series D остаётся остановленной. Build/Calculate/Reset возвращают true; ошибки передаются специализированными состояниями. Общая физика задаётся storage-образами и штатным lifecycle. Компактный Git содержит primary/models/metrics/выбранные figures; полные воспроизводимые galleries остаются кэшем M40.
