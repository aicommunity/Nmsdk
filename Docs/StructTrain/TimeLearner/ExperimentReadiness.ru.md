# Готовность к научным экспериментам — 13.11.2026

## Текущий научный шаг — 13.11.2026, фактические пороговые ответы

[Реальный Classic N4 fixed-threshold опыт](ActualThresholdScientificReport-20261113.ru.md): оба native runs completed/valid,16 complete observations, source unchanged. Контроль100 воспроизводит исходные8 массивов samples/model_before точно и остаётся silent. При0.013048873000159292 production scorer: TP1/FP2/FN0/TN5. Target event0.2645s предшествует last input0.49s;3 из4 событий относятся к foils. Это partial Same-Matrix selectivity6/8, не рабочее распознавание завершённого паттерна и не completed training. Full32 soma pairs+8LT decision-channel report строится отдельно.

Общий acquisition test A2 остаётся FAILED на cleanup после complete result.json: пропущен обязательный note у Reservations.release. Исправлениеa36d3db932f43394412df7581069a1d3c0a757bb, exact closed-worker recovery одного lease; original error сохранён, нативные эксперименты не повторялись. [Raw результаты и отказ](ValidationPlans/M40DiagnosticThresholdScienceA2-20261113/RESULT.ru.md). Нельзя объявлять исходный тест1/1 PASS по валидности данных.

[Branch physical Rs control принят1/1](ValidationPlans/M40BranchSharedBankRsA2-20261113/RESULT.ru.md): replay/matched86M/all-bank21.5M на[27,27,27,1], clocks/inputs/source preserved. Общий максимум0.005456576369859967→0.02235560254260882, около4.10×; три selected originals просмотрены. Assigned-peak certificate/классификация не измерены. [Научный отчёт Branch](BranchSharedBankScientificReport-20261113.ru.md) уточняет52 domains:27 locked/25 unlocked, все51 candidates при86M. [Следующее исправление N1](N1TimingReadyNormalizationFollowup-20261113.ru.md) — bounded local normalization на timing-ready unlocked geometry; код ещё не изменён.

[Полный исходный Branch Train corpus44.06MB](ValidationPlans/M40BranchFullDomainPrimaryA1-20261113/RESULT.ru.md) уже в Git, [независимый Elder replay1/1 принят](ValidationPlans/ElderBranchFullDomainPrimaryReplayA2-20261113/RESULT.ru.md), corrupt extracted CSV отвергнут. Для новых intervention/threshold studies идёт отдельная lossless source-envelope collection; первые legacy bundles превысили compact output limit и не опубликованы. Full galleries остаются M40 cache.

Scoped diagnostic API имеет native2/2 и DATA5/5; общий SDK10-case cohort остаётся failed8 upstream completed-training fixtures. Два отказа воспроизведены на прежнем SDK Elder; остальные шесть старых baseline cases не перепроверены. Цель всего плана активна: полностью принят только этап0, этапы1–12 частичны; диагностические результаты не закрывают весь план.

Реальные N4 эксперименты уже выполняются. Надёжная классификация современными остановленными моделями пока не подтверждена. Полностью завершённого научного сравнения всех моделей/режимов исходного плана ещё нет.

[Единая карта этапов, принятых результатов и текущих handles](ImplementationStatus.ru.md) — источник текущего состояния. [Все прежние оперативные записи сохранены без изменения исходных байтов](ExperimentReadiness-History-through-20261113-before-publication-train.ru.md); их статусы работающих заданий относятся к своим снимкам.

## Что уже можно читать

- [L22: сопротивление и принадлежность ранней вершины — диагностический отчёт](L22BurstResistanceScientificReport-20261113.ru.md). Полная численная сетка86/64.5/43/21.5МОм, report2/2, restore1/1,8 выбранных PNG просмотрены; классификация не заявляется.

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

Текущий шаг: [N4 fixed-geometry Rs study уже запущен](ValidationPlans/M40L22BurstResistanceStudyA1-20261113/STATUS.ru.md) на фактическом graph3b8a160f... с L=[22,1,1,1]. Перед ним прошли исправленная сборка Console/2 roundtrip,13 Elder DATA/declaration controls,5 actual-file reader checks и [все6 реальных Console процессов Classic/Branch](ValidationPlans/M40BurstReadbackConsoleSixA4-20261113/RESULT.ru.md). Последние дали10 observations; scope N=2 не подменяет N4. Ошибки monitor и schema dispatch исправлены, настройки обучения не менялись. Серия N4 проверяет ограниченные Rs с matched control и графиками всех сом; все5 per-run readbacks и итоговый comparison получены; validation ERROR возник после них на render из-за system Python безmatplotlib. Численная часть завершена, отчёт и визуальная приёмка ещё ожидаются. Усиление Soma1 пока не добавило отдельной вершины; global maxima не используются как результат обучения.

[Диагностический отчёт об обрыве Train L22](ValidationPlans/M40L22CensoredTemporalA2-20261113/STATUS.ru.md) проверяется на M40 по уже имеющимся original primary, без нового Train. У terminal input0 есть два полных observations и один415-sample censored; недостающие пробы не достраиваются. Это адресный анализ причины остановки, не новая оценка классификации.

Read-only отчёты и compact collection/restore завершены. [Rs/censored report2/2](ValidationPlans/M40L22RecordedReportsA1-20261113/RESULT.ru.md), [L14/L15/L21 report1/1](ValidationPlans/M40L14L15TransitionA1-20261113/RESULT.ru.md), [large restore1/1](ValidationPlans/M40L22PrimaryRestoreA1-20261113/RESULT.ru.md). Все перечисленные группы закрыты; original failures сохранены.

[Большой N4 primary restore принят](ValidationPlans/M40L22PrimaryRestoreA1-20261113/RESULT.ru.md):3301 regular restored files/3306 logical members,15 exact jobs, original source и5 native audits после восстановления,1/1 passed351.980s. Collector иrestore закрыты, native data сохранены в48.78MB Git package. Read-only report job завершён2/2; его handle находится в [M40L22RecordedReportsA1](ValidationPlans/M40L22RecordedReportsA1-20261113/STATUS.ru.md). [Сопоставление18 CSV](ValidationPlans/M40L22RecordedReportsA1-20261113/REUSED_CONTROLS.json) доказывает переиспользование прежних графиков L3/L54/L45, не независимые повторы. Полные этапы1–12 остаются частичными.

## Последний завершённый научный разбор

[Переход L14→L15](L14L15AssignmentTransitionScientificReport-20261113.ru.md): полные controls подтверждают4→3 вершины и потерю unique assignment input0; приL14 выбран ранний меньший пик, но timing/amplitude residuals вне допусков. [Rs серия L22](L22BurstResistanceScientificReport-20261113.ru.md) усилила ответ без восстановления отдельной вершины на четырёх проверенных Rs.12 selected originals просмотрены; полные56 views остаются M40 cache. Во всех перечисленных jobs теперь terminal/closure подтверждены.

Следующий конкретный шаг — локальный Y focus слабой впадины L14 по исходным native frames310→331, без изменения peak criterion, tolerances или новых Train. Затем продолжить обязательную матрицу и исправления алгоритмов по измеренным причинам. Полные стадии1–12 остаются частичными; подтверждённой новой классификации нет.
