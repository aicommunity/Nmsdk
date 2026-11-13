# Готовность к научным экспериментам — 13.11.2026

Реальные N4 эксперименты уже выполняются. Надёжная классификация современными остановленными моделями пока не подтверждена. Полностью завершённого научного сравнения всех моделей/режимов исходного плана ещё нет.

[Единая карта этапов, принятых результатов и текущих handles](ImplementationStatus.ru.md) — источник текущего состояния. [Все прежние оперативные записи сохранены без изменения исходных байтов](ExperimentReadiness-History-through-20261113-before-publication-train.ru.md); их статусы работающих заданий относятся к своим снимкам.

## Что уже можно читать

- [Историческое холодное Train→Test:4/8–6/8](HistoricalAugustColdStart.ru.md). Сохраняется значение августовских визуальных наблюдений исходного протокола.
- [Историческая frozen matrix порядка и ITI](HistoricalFrozenProtocolMatrixScientificReport-2026-11-07.ru.md). Это отдельная проверка одной сохранённой модели, а не универсальная устойчивость обучения.
- [Classic full-domain: почему некоторые вершины не назначены input0](ClassicFullDomainAssignmentScientificReport-20261112.ru.md). Три просмотренных full/omission графика с реальными входами; no_necessary_input не означает отсутствие влияния импульса.
- [Реакции Classic и Branch на все8 паттернов](RecordedN4DiagnosticScientificReport-20261112.ru.md).16 complete/valid observations,19 просмотренных PNG, независимый compact replay Elder. Обе остановленные модели при threshold100 имеют TP0/FP0/FN1/TN7.
- [Последнее сохранённое budget16 состояние:8 frozen проб](ValidationPlans/M40Budget16FrozenDiagnostic8A1-20261113/RESULT.ru.md). Новый completed/valid diagnostic, неизменная модель, тот же отрицательный счёт0/0/1/7. Порог не калибровался; исходный Train остаётся timeout/budget_exhausted без certificate.

## Что выполняется сейчас

1. [Один новый cold Classic N4/N1 после исправления экспорта](ValidationPlans/M40PublicationReceiptBudget16TrainA1-20261113/PLAN.ru.md). Root92ad/Pulsedfb, production runtime принят7/7 на M40 и Elder. Полный scientific job равен прежнему; search1800s+finalization300s, original tolerances, stock безLTMembrane. Native Console подтверждён живым; итог не принят. Это проверка завершения большого экспорта и честного training outcome, без обещания сходимости.
2. [Временной отчёт последнего diagnostic](ValidationPlans/M40Budget16DiagnosticReportA1-20261113/STATUS.ru.md):32 пары pattern×soma, actual inputs, полный обзор и zoom≥8pixels/native tick, без downsampling. Пока идёт полный DATA audit, ручная визуальная приёмка открыта.
3. [Exact compact export/restore/rescore](ValidationPlans/M40DeclaredDiagnosticPrimaryA1-20261113/PLAN.ru.md): original model.json282794133B и8 observations, explicit384MiB member budget.10 объявленных checks, результат ожидается. Предшествующие34/34 schema2 archive checks не заменяют этот запуск.

У работающих заданий разные output/runtime/source bindings; их каталоги не обновляются. При потере связи сначала проверяется тот же kernel handle. Timeout наблюдения не является основанием перезапуска. Полные gallery — M40 cache; Git содержит сжатые primary, модели, метрики и выбранные рисунки.

## Что отделяет нас от итогового научного сравнения

- Завершить новый Train и проверить полный execution/model/summary/primary. При отрицательном outcome разбирать конкретные измерения и решения поиска; не повышать бюджеты автоматически и не выдавать остановленное обучение за Exact.
- Закончить опубликованный отчёт текущего состояния с читаемыми временными графиками всех паттернов, сохранением масштаба и actual input overlay; проверить compact replay исходных данных.
- Выполнить оставшиеся legacy/V2 A/B и обязательную матрицу моделей, нормализации, физики, частот, bounds, reset/inhibition/PostTune/calibration. Для независимого Test сначала фиксируются модель и подтверждённый реальным прогоном порог. Same-Matrix отмечается отдельно.
- Проверить target в каждой позиции, order/ITI и reset-per-trial/continuous отдельно. Partial observations и all-silent7/8 не являются успешной детекцией. Не требовать8/8 как условия завершения рефакторинга; валидные отрицательные и unresolved результаты входят в карту.
- Закрыть оставшиеся требования этапов1–12 и children-first --no-ff merges в develop. Подробный список находится в [карте приёмки](ImplementationStatus.ru.md), а не подменяется этими научными шагами.

Во время Train используется максимум закреплённого импульса; при Test — полный отклик паттерна. Общий максимум пачки не исправляет неоднозначность принадлежности при обучении. Ни современный отрицательный результат, ни новая процедура оценки не отменяют августовские4/8–6/8 в исходных условиях. Series D автоматически не возобновляется.
