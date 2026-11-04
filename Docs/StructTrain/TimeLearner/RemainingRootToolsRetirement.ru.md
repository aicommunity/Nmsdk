# Последние девять path-selected исторических root tools

Snapshot cb0bb0c322736406d9e73a0b5542b3b3a5ba33ec. Девять файлов удалены в candidate без wrappers/copies; каждый full commit/path/blob/SHA256/size/retrieval_command внесён в manifest. Candidate150 records:148 retired/2 moved, complete=false. Production gates150/negative/exact13 прошли на обоих workers; группа принята.

## Зависимости и применение

Группа: sample_host_metrics.py, timelearner_margin_model.py, be_prep.py, c1_dose_response_console.py, e05_e0_compare.py, e05_e0_kernel_probe.py, e05_job.py, run_iti.py и Scripts/audit_timelearner.py. run_iti импортирует c1_dose_response_console; e05_job использует be_prep. Исходящие зависимости на Bin repro_cold_lib/posttune_verify/phase9 helpers не делают эти файлы текущими production workers. Literal imports/call paths проверены в root Scripts/Tests/App/CMake/workflow и Bin99f58da9296a794374cef679bbb878cb62af979a; входящих исполняемых ссылок не найдено. Probe preparation identifiers — совпадение подстроки, не вызов be_prep. В Scripts/audit-probes/README.md осталась историческая команда snapshot-аудита; она помечена ниже своего исходного раздела. Произвольные внешние/dynamic users этим поиском не исключаются.

## Почему старые протоколы не переносятся в новый launcher

- E05 выполняет работу при import, monkeypatch глобального soft_cold_reset_train и CASES, XML overlays и частичный Train→Test sync. Jitter последнего Rs сам обозначен неэффективным. Gate требует роста всех non-reference L>1 и может отвергнуть корректное обучение; этот критерий не переносится.
- be_prep — диагностический overlay отказанной структуры, не доказательство completed Train. Новый diagnostic-evaluate сохраняет stopped provenance, а complete export/import отдельно проверяет полный граф.
- run_iti использует общий Bin/Platform binary и фиксированную форму8×4. Возврат процесса, множество проб и полнота окна не являются единым обязательным gate перед подсчётом margin. Новые frozen observation/scorer contracts отдельные; вся научная order/ITI матрица ещё не закрыта.
- E0 compare выбирает первый trace, пропускает повреждённые строки, сравнивает пересечение timestamps, вызывает standalone segsim без обязательной проверки return code. Совпадение отдельной kernel curve не доказывает общую native эквивалентность. E0 kernel probe использует исторические overrides/templates, не effective heterogeneous storage audit.
- C1 dose инструмент вручную выбирает классы/параметры и ссылки торможения. Сохраняются его mechanism-checks как исторические свидетельства; текущий native intervention protocol обязан заново читать реальный graph/physics. Полная equivalence не заявляется.
- margin_model — линейный matched-filter surrogate с фиксированными alpha kernels, без native LT/spiking dynamics. Его оценки не отменяют визуальные августовские4/8–6/8 исходного протокола.
- sample_host_metrics — разовый host sampler старого аудита. Удаление не является реализацией нового continuous thermal monitor.
- audit_timelearner использует фиксированный прежний BASE и legacy Bin scorer для snapshot/counterexamples. Production inventory/history/evidence/scorer сохраняют собственные версии и receipts; старые выводы не пересчитываются задним числом.

## Проверки и незавершённая работа

Все данные, модели, JSON/TSV/CSV, графики и численные тексты отчётов сохраняются. Исторические команды требуют source snapshot, не повторный запуск текущей очереди. SeriesD не возобновляется. Никакая новая научная оценка не выводится из удаления scripts.

verify-migration150, restored-path negative control и exact13 scope прошли на обоих workers. Native production package/Tests/App/CMake/child gitlinks не менялись в retirement candidate; отдельное принятое добавление worker_dependency имеет собственную двухсерверную приёмку. Исторические программы не исполнять. Нижняя граница после candidate188 Bin/0 выбранных root/0 Pulse не означает, что проверены все неименованные scripts: Scripts/audit-probes и другие callers вне path filter остаются для отдельного review. Весь этап9 и исходный план остаются частичными.

M40 A2 прошёл150/negative/exact13 controls; A1 не прочитал manifest из-за неполной доставки blob и сохранён отдельно. Проверены13 опубликованных файлов,24 archive members,277 source blobs: [receipt](RemainingRootToolsM40Verification.json). Elder также прошёл150 и negative control: [primary](../../../Reports/StructTrain/TimeLearner/s06-corrected-baseline-and-dependency-readbacks-a1/README.ru.md), proof871280a11a36016476723b00d121cff53979c7ea. Текущий принятый manifest150 records; все9 старых путей отсутствуют. Более широкий review неименованных scripts остаётся обязательным.
