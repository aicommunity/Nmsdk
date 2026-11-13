# Научные результаты TimeLearner и готовность — 13.11.2026

Современные реальные эксперименты уже выполнены и опубликованы с первичными данными. Успешное завершение обучения и надёжная классификация завершённого паттерна на современных моделях пока не подтверждены. Исторические визуальные4/8–6/8 сохраняют силу для своего исходного протокола. Полный план остаётся активным: полностью принят этап0, этапы1–12 частичны.

## Что уже можно читать

| Отчёт | Основной результат | Что нельзя из него заключать |
|---|---|---|
|[Branch N1: измеренный интервал нормализации](N1LocalTurnScientificReport-20261113.ru.md)|Same-budget холодное обучение завершено completed/valid, но BudgetExhausted. На одной геометрии Rs86M/2.880071555M дают opposite amplitude residuals при timing-valid. Есть четыре просмотренных временных графика с полными пачками, actual inputs и omission controls.|Bracket не является сходимостью. Ни один consumed candidate не удовлетворяет обоим допускам; классификация не измерялась.|
|[Classic: фактический fixed-threshold опыт на8 паттернах](ActualThresholdScientificReport-20261113.ru.md)|TP1/FP2/FN0/TN5 при заранее выбранном пороге0.013048873000159292. Реальные спайки и полные окна; report1/1, выбранные Soma/LT figures, полная32-soma/8-LT gallery.|Target event0.2645s раньше последнего входа0.49s. Partial6/8 Same-Matrix остановленной модели не является детекцией завершённого паттерна или независимым Test.|
|[Branch: coherent shared-bank Rs intervention](BranchSharedBankScientificReport-20261113.ru.md)|Общий максимум Soma1 растёт примерно4.10× при86M→21.5M; replay/source/clocks/inputs проверены, три originals просмотрены.|Глобальный максимум не заменяет максимум закреплённого импульса. Assigned certificate/классификация не получены.|
|[Classic budget16: все8 паттернов](Budget16DiagnosticScientificReport-20261113.ru.md)|32 pattern×soma пары,14 просмотренных originals. При фиксированном100 модель молчит.|Accuracy7/8 означает7 правильных молчаний foil при пропущенном target, а не рабочую детекцию.|
|[Classic и Branch: современные диагностические ответы](RecordedN4DiagnosticScientificReport-20261112.ru.md)|16 completed/valid frozen observations,19 просмотренных PNG, независимый compact replay Elder.|Это остановленные модели другого снимка; нельзя смешивать их с последним Train или переносить успех выполнения на обучение.|
|[L14→L15: переход assignment](L14L15AssignmentTransitionScientificReport-20261113.ru.md), [L22 Rs sweep](L22BurstResistanceScientificReport-20261113.ru.md)|Full/omission traces показывают4→3 вершины и потерю unique assignment. Изменение Rs усиливает сигнал без восстановления отдельной вершины на проверенных четырёх Rs.|Отсутствие уникального assignment не означает отсутствия влияния импульса. Переназначение глобального максимума не является исправлением.|
|[Августовские cold Train→Test4/8–6/8](HistoricalAugustColdStart.ru.md)|Сохранены рабочие результаты исходного протокола с плохой разделимостью.|Порядок/ITI тогда не проверялись. Современные результаты их не отменяют.|
|[Историческая frozen order/ITI matrix](HistoricalFrozenProtocolMatrixScientificReport-2026-11-07.ru.md)|Отдельно проверена зависимость одной сохранённой модели от протокола.|Это не универсальная устойчивость всех моделей и не новое независимое обучение.|

Временные графики используют записанные мембранные потенциалы и фактические входные импульсы. Избранные originals сохраняются в Git; полные воспроизводимые PNG/SVG/PDF galleries — кэш M40. Область ручного просмотра указана в каждом отчёте; наличие сгенерированной gallery не означает просмотра всех её картинок. Для нового Branch endpoint report обе полные группы содержат6 complete traces по3601 samples; его overview/detail имеют одинаковый диапазон0..1.8s и не выдаются за дополнительный zoom.

## Что выполняется сейчас

[Cold Branch N4/N1 coupled-search Train](ValidationPlans/M40N1CoupledBranchTrainA1-20261113/STATUS.ru.md) запущен на M40:preflight completed/closed, подтверждены живой native handle и реальные raw CSV. Outcome и остатки нового варианта пока не установлены. Работающий source/runtime не меняется.

[SDK A4 принята93/93](ValidationPlans/M40N1CoupledSdkA4-20261113/RESULT.ru.md), native/outer groups закрыты. Source root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8; runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. Положительный SDK verdict не является научной сходимостью и не закрывает полную physical matrix.

Новый опыт использует прежний native job SHA25693556039955e15a3de1ec88b55d546b2f54bb7e680deb3fc1e499799a524c55d, initial model и reference-origin bytes. Изменён порядок исследования L/Rs:bounded coupled-family length proposals, finite local normalization allowance и safeguarded measured log-secant. CapturedPerInput, fixed anchor и исходные tolerances/budgets сохранены. Эффект совместного варианта ещё не измерен и заранее не приписывается одному изменению.

Исходные SDK A1(91/93),A2(compile failure) иA3(canonical fresh-build refusal) сохранены отдельно. A4 использовала чистую сборку; guard не ослаблялся. Synthetic helper bound64 не меняет controller allowance<=12 или scientific budget. Автоматический threshold100 Test очередной необученной остановленной модели не запускается.

## Что уже сохранено для повторного анализа

[Новый Branch Train44.21MB](ValidationPlans/M40N1LocalTurnPrimaryA1-20261113/RESULT.ru.md) содержит весь закрытый primary, включая незавершённую terminal group как незавершённую. Независимое восстановление именно этого нового пакета ещё ожидается. [Прежний Branch full-domain](ValidationPlans/M40BranchFullDomainPrimaryA1-20261113/RESULT.ru.md) имеет принятый независимый Elder restore/audit; [Branch Rs27.42MB](ValidationPlans/M40BranchSharedBankPrimaryReplayA1-20261113/RESULT.ru.md) — full restore/3 DATA audits; [threshold56.37MB](ValidationPlans/M40ThresholdPrimaryRecompressionA2-20261113/RESULT.ru.md) — byte-exact tar и full881-file production restore. [Индекс артефактов](../../../Reports/StructTrain/TimeLearner/README.md).

Первичный acquisition threshold test остался FAILED на cleanup после валидных результатов; исправлениеa36d3db932f43394412df7581069a1d3c0a757bb и recovery lease не переименовывают исходный запуск в PASS. Scoped native diagnostic2/2 и DATA5/5 приняты, но общий10-case SDK cohort имеет8 upstream completed-training fixture failures; два воспроизведены на прежнем SDK Elder, остальные шесть baseline cases не перепроверены. Это отдельная область от77 старых bounded-controller checks и93 принятых A4 checks.

## Что осталось до итогового научного сравнения

- Получить итог текущего same-budget Branch эксперимента; сопоставить фактические assigned timing/amplitude residuals, новые Rs/L и all-input verification. Bracket/Done/process completion не заменяют Exact. Отрицательный или unresolved исход допустим, если валиден.
- Завершить legacy/V2 A/B и обязательную матрицу моделей, N0/N1, физики, частот, bounds/quantization, reset/inhibition/PostTune/calibration. Детальная карта каждого исходного этапа — [ImplementationStatus](ImplementationStatus.ru.md).
- Зафиксировать модель и подтверждённый настоящим прогоном порог перед independent frozen Test. Same-Matrix оценивать отдельно; target в каждой позиции, order/ITI и reset-per-trial/continuous — отдельные протоколы. Partial observations не достраиваются до полной матрицы.
- Закрыть оставшиеся требования этапов1–12 и children-first--no-ff merges в develop. Нет требования получить8/8 ради завершения рефакторинга; необходимы корректная реализация и проверка полного заявленного scope.

При Train выбирается максимум закреплённого импульса: слившаяся неразличимая вершина неоднозначна; раздельная ранняя вершина с хвостовым влиянием допустима. При Test оценивается весь отклик, но event до последнего входа выделяется как ранний. Нельзя ослаблять критерий или повышать scientific budget ради PASS. SeriesD автоматически не возобновляется.

При потере связи проверяется прежний kernel handle; timeout наблюдения не означает остановку и не разрешает перезапуск. Работающие source/runtime/output bindings не обновляются. Источники, конфиги и compact results передаются через Git.

Предыдущая сводка доступна в Git commit87283983db82aa4df63306af5212a347076cc4f1 по тому же пути. [Более ранняя история](ExperimentReadiness-History-through-20261113-before-publication-train.ru.md) сохраняет прежние записи; их статусы относятся к своим снимкам, измерения не переписаны.
