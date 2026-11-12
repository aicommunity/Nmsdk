# Classic budget16: два временных ограничения, итог обучения неизвестен

Задание s07-full-domain-budget16-train-m40-a2 закрыто. Native execution timeout2100.362201920245s; outer controller process_error/2130.3581641232595s; один адресный test выполнен и failed, без errors/skips. Whole group закрыта, lease released, source/tool/fixtures до и после совпали побайтно. [17 исходных подтверждений](failed-timeout/readback-integrity.json).

Последняя физическая проба398 содержит native_status=cancelled, complete=false, end_reason=native_training_time_budget_exhausted,2287 samples. Это search/125/composite/67/native/1; номер в ID не подменяет счётчик search probes. После окончания search-time budget процесс формировал summary: SIGTERM stack показывает EncodeAndValidateNativeCandidateWindowServiceArchive → CompositeSummary → EncodeNativeCandidateWindowRecoveryTrainingState → EncodeNativeTrainingState. Дополнительных300s на финализацию не хватило.

Финальные state/summary/execution отсутствуют; package_audit/physical_audit null, validity unverified_execution. Runtime capture cooperative_capture_not_ready также не завершён. Поэтому outcome learner, final parameters, сертификат и результат классификации **не подтверждены**. Последний отменённый probe не является сертификатом BudgetExhausted всего learner.

[Состав данных](packet-census.json):398 native packets,397 отмечены valid/complete, один incomplete. CSV-файлов796, но SHA-различных398: это две записи тех же временных данных — train_stopped_trial_N.csv и composite-measurements/group/...csv. Их нельзя считать796 независимыми пробами. [Исходный последний packet](last-packet/native-trial-398.json). Полный primary сохраняется отдельно компактным Git corpus; результат не перезапускается автоматически.

Вопрос о пользе budget16 против4 остаётся открытым из-за незавершённой финализации. Новый scoped блокер — [повторное построение архива при summary8](../../RecoverySummaryExportTimeout-20261112.ru.md). До адресного исправления и его проверки не увеличиваем поисковое время, recovery budget или допуски и не проводим Test шаблонной модели.

[Позднейший production DATA audit сохранённого индекса](../M40Budget16RetainedArchiveAuditA1-20261112/RESULT.ru.md) принят:67 records/398 primary files, без привязки текущего runtime budget и без восстановления learning outcome.

## Что удалось установить по сохранённым измерениям

Все252 CSV первых42 групп побайтно совпали с прежним budget4 опытом. Далее budget16 действительно продолжил тот же измеренный путь: valid input0 measurements стало15 вместо14, появились L14, Rs86MΩ/Ns1. Для группы44 найден соседний anchor43 с теми же revision/epoch и всеми физическими параметрами; записанные arrivals0.1450/0.4945s дают временной остаток−0.3495s, амплитудный остаток−0.0105569014 к собственной цели0.0157814416. Оба остатка далеко от допусков20ms/1e-5.

Это производный DATA-разбор: [числа, пары и252 SHA](measured-prefix-analysis.json), [все67 групп](audited-group-table.json). Он не восстанавливает отсутствующий итог learner. Максимальная длина среди valid measured input0 здесь14; более длинные геометрии исследовались, но не считаются валидными измеренными кандидатами только по наличию реакции. Конечная модель и сертификат по-прежнему не подтверждены.

[Полный первичный корпус сохранён компактно](../../ClassicBudget16TimeoutPrimaryPublication-20261112.ru.md):1368 members/32.49MB XZ.
