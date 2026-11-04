# Дополнительные кандидаты миграции: readback04.11.2026

Уточнён конкретный пробел path-based inventory: отсутствовало расширение.mjs, в том числе generate_timelearner_chart_workbook.mjs в Bin. Восемь root scripts с нейтральными именами содержат прямые TimeLearner/StructTrain references и также не попадали в прежний поиск. Старый снимок188 Bin/0 выбранных root остаётся верным для своего селектора; он не доказывает отсутствие прочих инструментов.

Подготовлен candidate `0497d934d666d883903f3a8ff504169009982dbe`: поддержка JavaScript/PowerShell modules, Perl/Ruby и явный --include-related для поиска по committed содержимому. Default остаётся schema2, новый режим — schema3 с selection_reasons/path_tokens/content_tokens. Root production package исключается из historical candidates; symlink читается как Git blob без чтения цели. Удаление, импорт и исполнение выбранных инструментов не выполняются.

На M40 прошли15/15 actual Git snapshot/CLI tests без failures/errors/skips. Читаются целые pinned Pulsecc headers/sources. Исходный source0497 доставлен отдельным Git pack без alternates. Metadata-only lease и bounded parent kernel group закрыты, память ограничена512MiB. Реальный нейронный расчёт K1 продолжался отдельно; его runtime/source не изменялись. [Полная проверка](RelatedScriptInventoryM40Verification.json), [primary bundle](../../../Reports/StructTrain/TimeLearner/s01-related-inventory-m40-normal-a1/bundle.json). Evidence commit `fe745988ae9bb29b3db4d26b02310e355c0e5cff`; primary17 408 bytes,8 members. Независимо сверены279 root Python blobs и4 целых Pulse blobs.

Elder gate15 A2 (worker2220929; точный start/binding в linked artifact) стоит после live-routing проверки и освобождения ресурсов. Runtime pass на Elder ещё не получен; код селектора не объединён в develop. Численные/integration tests локально не выполнялись. Отдельно выполнено только чтение Git metadata через production candidate inventory в временных sparse clones с записанными root/child commits. Их working status не описывает пользовательские checkout или SDK.

Первая Elder A1 постановка завершилась до reserve и tests из-за ошибочного s01-prefixed пути к предыдущему s10 заданию. Ошибка только в launcher, source0497 неизменён. Полный failed archive5 members/16 684 bytes и свежая классификация closed/not_created сохранены; A2 подтверждён живым/pending. [Проверка](RelatedScriptInventoryElderQueueVerification.json), [Git primary и binding](../../../Reports/StructTrain/TimeLearner/s01-related-inventory-elder-queued-a2/SHA256SUMS). Очередь не является runtime PASS.

## Полный список для следующего review

[Компактный каталог](related_script_review.json) содержит197 candidates:189 Bin,8 root. Поиск только по пути с добавленными suffixes даёт189 Bin; прочие8 найдены по содержимому.217 properties и4 source records точно совпали с прежним property catalog, поэтому они не дублируются в новом JSON. Migration manifest пока150 records/complete=false; новые197 candidates не удалены и не считаются перенесёнными.

| Дополнительный root script | Что требует проверки до переноса/удаления |
|---|---|
| Scripts/audit-probes/generate_branch_update_probes.py | Старое извлечение тела функций; CMake caller и соответствие реальным native fixtures. |
| Scripts/audit-probes/generate_training_core_probes.py | Старые извлечённые gates/контроллеры; native coverage и сохранение исторического смысла. |
| Scripts/audit-probes/review-20260924/metrics_probes.py | Импорт старого scorer/auditor и исторического Git source, создание результатов при import. |
| Scripts/audit-probes/review-20260924/n_stim_csv_probe.py | Старый диагностический CSV протокол и входящие ссылки отчётов/launcher. |
| Scripts/audit-probes/review-20260924/posttune_probes.py | Исторические PostTune probes, имитация lifecycle и входящие зависимости. |
| Scripts/audit-probes/review-20260924/pulse_delay_probes.py | Извлечение NPulseDelay::ACalculate в stand-alone C++ с заменой Reset/объектов; не native integration proof. |
| Scripts/audit-probes/review-20260924/verifier_probes.py | Mock simulator/gates, monkeypatch CASES и старые XML overlays; не актуальный production verifier. |
| Scripts/audit-probes/run_fixed_threshold_grid.py | Старый запуск threshold sweep сохранённого Test и удаление логов; актуальную функцию должен обеспечивать managed calibration/report path. |

Таблица — предварительная постановка review, не заверенное решение по удалению. Нужны полный разбор вызывающих файлов и сохранение repository/full commit/path/blob. Comments и string literals могут давать ложноположительные находки; непрямые imports, computed paths, standalone C++/CMake probes, nonexecutable unknown suffixes и внешние callers не покрыты этим selector. Ни полный этап9, ни весь план не закрыты.
