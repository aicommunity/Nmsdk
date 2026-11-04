# Readback: восемь исторических audit/probe entrypoints

Candidate source `a93097a10902d7c46ea2ce36064b5ec470a17546` удаляет8 tools, добавляет точные Git retrieval records и снимает два зависимых standalone CMake target. Source branch codex/timelearner-historical-audit-probe-retirement опубликована. До проверки второго worker код не объединяется в develop: принятый manifest остаётся150, candidate содержит158 (156 retired/2 moved), complete=false.

На M40 production history CLI подтвердил все158 records и negative restored-path refusal. Exact16 changed paths и surviving CMake prefix проверены. audit_existing_gui/audit_counterexamples сохраняются; нового build/test результата для них не заявляется. Root production package, Tests, App, Root CMake, Pulse/Bin/Rdk gitlinks не менялись. Скрипты истории не исполнялись и не materialized; negative fixture существует только как Git-tree object.

[Подробный независимый readback](AuditProbeRetirementM40Verification.json), [primary bundle](../../../Reports/StructTrain/TimeLearner/s09-audit-probe-retirement-m40-a1/bundle.json). Evidence commit `29c49d45aa57e706dd79992f328a9573d0df6aa3`; compressed primary134 028 bytes,17 members, SHA256 `943159b12f7dacf27149b5e98fd8df6c5351b51915263d2a7015b3c5daa1a146`. Сверены279 production Python blobs и все158 исходных Root/Bin historical blobs. Kernel group закрыта, metadata lease освобождён.

Elder gate подтверждён живым в ожидании inventory A2 и освобождения ресурсов; exact invocation записан в [progress snapshot](../../../Reports/StructTrain/TimeLearner/s06-shared-lifecycle-build18-progress-a2/readback.json). Это не PASS Elder и не native model experiment. Runtime M40 K1 не изменялся.

## Назначение удаляемых инструментов

- generate_branch_update_probes.py и generate_training_core_probes.py извлекают тела методов/loops в fake properties/neuron/dataset/env; CMake callers удаляются вместе с ними. Это исторические body tests, не проверка native lifecycle/graph.
- review-20260924/metrics_probes.py и n_stim_csv_probe.py используют старый Bin scorer, синтетические CSV и optional old gold; часть работы/создания каталогов происходит при import. Старые критерии остаются историческими.
- review-20260924/posttune_probes.py извлекает методы и AST prefix другого генератора, подменяет clock/neuron и вручную очищает result. pulse_delay_probes.py заменяет реальный NPulseDelay собственным классом/Reset. Эти tests не доказывают полный scheduler/storage contract.
- review-20260924/verifier_probes.py подменяет external process/gates, CASES и flags/XML overlays. run_fixed_threshold_grid.py меняет saved Test XML, останавливается по числу CSV rows и удаляет generated traces; не обеспечивает полный frozen evaluation contract.

Literal caller search в committed Root Scripts/Tests/App/CMake/Docs Markdown, Bin script/docs и Pulse source/script/docs нашёл два CMake callers, внутренний posttune→Branch-generator и historical/readme links. В выбранных Bin/Pulse scopes callers не найдены. Dynamic imports/paths, standalone general probes и внешние jobs требуют дальнейшего review. Ни scientific outputs, ни August4/8–6/8 observations не удаляются/переоцениваются.

## Lifecycle candidate: свежий прогресс, не окончательная приёмка

Отдельный неизменяемый SDK root `1eab24decb6432947afc928e7f049f3a07de2709` / Pulse `8644c50984c45a2211de13a75fe05cffc5bb3154` собран. Focused native18/18 прошёл; actual XML содержит18 testcases без failure/error/skip. Реальный полный133 процесс PID2228382/start338236752 подтверждён живым. Source scope сохраняет Tests/App/Root CMake baseline33fc; Pulse Core меняет только5 declared lifecycle files. [Progress readback](../../../Reports/StructTrain/TimeLearner/s06-shared-lifecycle-build18-progress-a2/readback.json).

Progress snapshot содержит metadata/XML/ownership и явно не является финальным acceptance bundle: полные model exports/primary последующей133 gate ещё не опубликованы, runtime lease пока удерживается. Candidate не принят в develop; общий контроллер, legacy/V2/multirate/physics matrix и весь план остаются незавершёнными.
