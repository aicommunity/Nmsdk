# Готовность к научным экспериментам — 13.11.2026

Реальные N4 эксперименты уже выполняются. Надёжная классификация современными остановленными моделями пока не подтверждена. Полностью завершённого научного сравнения всех моделей/режимов исходного плана ещё нет.

[Единая карта этапов, принятых результатов и текущих handles](ImplementationStatus.ru.md) — источник текущего состояния. [Все прежние оперативные записи сохранены без изменения исходных байтов](ExperimentReadiness-History-through-20261113-before-publication-train.ru.md); их статусы работающих заданий относятся к своим снимкам.

## Что уже можно читать

- [Новый полный временной отчёт Classic budget16](Budget16DiagnosticScientificReport-20261113.ru.md):32 пары pattern×soma,14 просмотренных originals, все8 паттернов. Source training=budget_exhausted; fixed threshold100, target пропущен.
- [Историческое холодное Train→Test:4/8–6/8](HistoricalAugustColdStart.ru.md). Сохраняется значение августовских визуальных наблюдений исходного протокола.
- [Историческая frozen matrix порядка и ITI](HistoricalFrozenProtocolMatrixScientificReport-2026-11-07.ru.md). Это отдельная проверка одной сохранённой модели, а не универсальная устойчивость обучения.
- [Classic full-domain: почему некоторые вершины не назначены input0](ClassicFullDomainAssignmentScientificReport-20261112.ru.md). Три просмотренных full/omission графика с реальными входами; no_necessary_input не означает отсутствие влияния импульса.
- [Реакции Classic и Branch на все8 паттернов](RecordedN4DiagnosticScientificReport-20261112.ru.md).16 complete/valid observations,19 просмотренных PNG, независимый compact replay Elder. Обе остановленные модели при threshold100 имеют TP0/FP0/FN1/TN7.
- [Последнее сохранённое budget16 состояние:8 frozen проб](ValidationPlans/M40Budget16FrozenDiagnostic8A1-20261113/RESULT.ru.md). Новый completed/valid diagnostic, неизменная модель, тот же отрицательный счёт0/0/1/7. Порог не калибровался; исходный Train остаётся timeout/budget_exhausted без certificate.

## Что выполняется сейчас

Новый cold Classic N4/N1 полностью завершён: native2070.92s и внешний CLI/DATA audit3070.16s,1/1 passed, все группы закрыты/lease released. [Полный исход](ValidationPlans/M40PublicationReceiptBudget16TrainA1-20261113/RESULT.ru.md), [1281-member compact primary46.04MB](ValidationPlans/M40PublicationReceiptBudget16PrimaryA1-20261113/RESULT.ru.md). Training=budget_exhausted, сертификата нет. Конечный L22 не совпадает с15 valid candidate records L1..14; это остановленный снимок, не обученный input.

Следующая адресная работа — [production анализ search history](TrainingSearchHistoryReport.ru.md): отдельные candidates/rejections/domains/terminal graph,7 unit+1 actual CLI check на исходных данных. [Elder7/7 unit controls приняты](ValidationPlans/ElderNativeSearchHistoryA1-20261113/RESULT.ru.md), [M408/8 actual corpus gate принят](ValidationPlans/M40NativeSearchHistoryA1-20261113/RESULT.ru.md). Этот анализатор принят в объявленной области; полные исходные этапы остаются частичными. Новых Train, изменения budgets/tolerances и возобновления SeriesD нет.

[Report2/2 и visual review14 originals завершены](ValidationPlans/M40Budget16DiagnosticReportA1-20261113/RESULT.ru.md). [Exact original-model export/restore/rescore10/10](ValidationPlans/M40DeclaredDiagnosticPrimaryA1-20261113/RESULT.ru.md) также принят:28 members/320.08MB в19.58MB XZ. [Независимый Elder compact replay1/1 принят](ValidationPlans/ElderBudget16CompactReplayA1-20261113/RESULT.ru.md): весь original readback совпал без original M40 directories. Эти результаты относятся к прежнему frozen model89681..., а не новому native model3b8a160f... из пункта1.

У работающих заданий разные output/runtime/source bindings; их каталоги не обновляются. При потере связи сначала проверяется тот же kernel handle. Timeout наблюдения не является основанием перезапуска. Полные gallery — M40 cache; Git содержит сжатые primary, модели, метрики и выбранные рисунки.

## Что отделяет нас от итогового научного сравнения

- Разобрать проверенную историю поиска нового Train и подтвердить production анализатор; затем поставить только обоснованную конечную L/Rs диагностику. Не повышать бюджеты автоматически и не выдавать остановленное обучение за Exact.
- Читаемый отчёт предыдущего budget16 состояния опубликован; independent compact replay принят; далее анализировать новый Train по его собственным данным и outcome.
- Выполнить оставшиеся legacy/V2 A/B и обязательную матрицу моделей, нормализации, физики, частот, bounds, reset/inhibition/PostTune/calibration. Для независимого Test сначала фиксируются модель и подтверждённый реальным прогоном порог. Same-Matrix отмечается отдельно.
- Проверить target в каждой позиции, order/ITI и reset-per-trial/continuous отдельно. Partial observations и all-silent7/8 не являются успешной детекцией. Не требовать8/8 как условия завершения рефакторинга; валидные отрицательные и unresolved результаты входят в карту.
- Закрыть оставшиеся требования этапов1–12 и children-first --no-ff merges в develop. Подробный список находится в [карте приёмки](ImplementationStatus.ru.md), а не подменяется этими научными шагами.

Во время Train используется максимум закреплённого импульса; при Test — полный отклик паттерна. Общий максимум пачки не исправляет неоднозначность принадлежности при обучении. Ни современный отрицательный результат, ни новая процедура оценки не отменяют августовские4/8–6/8 в исходных условиях. Series D автоматически не возобновляется.
