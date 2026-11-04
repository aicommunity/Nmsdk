Принято после158 records/negative/exact16/CMake prefix на обоих workers: [приёмка](InventoryAndAuditRetirementAcceptance.ru.md). Manifest158 complete=false; ниже сохранена исходная постановка candidate.

# Candidate: исторические audit/probe entrypoints

Восемь Python tools из Scripts/audit-probes удалены из текущего feature tree без wrappers. Archive snapshot `147f6dbcdbc0c0c183ef1068152e4bbee9848dd9` содержит каждый исходник; полный commit/path/blob/SHA256/bytes и read-only retrieval command записаны в [manifest](script_migration.json). Получается158 records (156 retired/2 moved), complete=false. До серверных gate это candidate, не принятая миграция.

## Review и изменение

| Исторический tool | Причина retirement / сохраняемые границы |
|---|---|
| generate_branch_update_probes.py | Извлекает два Branch метода в fake property/neuron/dataset/env/logger;8 исторических C++ cases не проверяют native graph/scheduler или динамику. |
| generate_training_core_probes.py | Извлекает gate/TipR/selection методы и отдельные loops; fake detach/monotonicity, ручное состояние и собственные допуски fixture. Исторические11/11 остаются scoped body probes. |
| review-20260924/metrics_probes.py | Импорт old/current Bin scorer и auditor, синтетические first-row-target данные, запись артефактов при import. Исторический критерий не становится текущим verdict. |
| review-20260924/n_stim_csv_probe.py | Синтетические CSV v3, фиксированные4 soma/ISI columns, optional старый gold; полезные censoring/morphology контрпримеры остаются в отчётах. |
| review-20260924/posttune_probes.py | Читает AST prefix другого генератора, извлекает методы, подменяет clock/dataset/neuron и вручную сбрасывает result; это не транзакция полной физической модели. |
| review-20260924/pulse_delay_probes.py | Извлечённый NPulseDelay::ACalculate с отдельным fake class/buffer/Reset; не полный lifecycle/readback реального компонента. |
| review-20260924/verifier_probes.py | Mock external process/gates, monkeypatch CASES, regex XML overlays и прежние flag criteria. Нельзя считать проверкой current managed whole-model transfer. |
| run_fixed_threshold_grid.py | Копирует saved Test, regex меняет XML/Project.ini, завершает по числу строк, optional external analyzer, удаляет StatisticLog/EventsLog. Не доказывает complete trial windows, frozen model либо runtime closure. |

Прочитаны исходники и проверены literal references в committed Root Scripts/Tests/App/CMake/Docs Markdown, Bin script/docs и Pulse code/script/docs trees. Реальные входящие caller links: два configure-time генератора в standalone Scripts/audit-probes/CMakeLists.txt и внутренний posttune_probes→generate_branch_update_probes. Остальные найденные ссылки — README/исторические отчёты и snapshot review table. В выбранных Bin/Pulse scopes callers не найдены. Computed names, внешние users/jobs и неподходящие suffixes этим поиском не исключены.

CMake лишается только audit_training_core/audit_branch_update и связанных configure dependencies/execute_process. Префикс, создающий audit_existing_gui/audit_counterexamples, сохраняется дословно. Эти mixed GUI/component probes и generate_probes.py остаются для отдельного review. Нового PASS для них не заявляется. Root CMake, Tests, App, production package и child gitlinks не меняются.

Старые historical README ссылки переведены в Git source; прежние commands в review README становятся git show. Научные данные, graphs, models, CSV/XML outcomes не удаляются и не переоцениваются. Saved-state snapshot показывает доступность исходника, не утверждает, что именно этот Root commit использовался в историческом опыте. Августовские4/8–6/8 сохраняют исходный смысл.

## Проверки и оставшаяся работа

Подготовить на обоих workers production history verify-migration:158 полных records, exact16 path scope, CMake surviving-prefix equality и negative restored-path Git-tree fixture (без materialization/исполнения старого script). Полные primary, source hashes, bounded group closure и resource release сохраняются в Git. Старые probes не запускать как новые integration tests.

Функции strict observations/scorer, bounded training/final verification, full-model transport, native calibration/grid/confirmation/frozen reports проверяются production fixtures отдельно. Нет утверждения, что они уже покрывают каждый старый legacy probe/physics/reset case: общий план всё ещё частичен. В частности NPulseDelay whole-component lifecycle и оставшийся historical general generator требуют отдельного review; удаление fake-body теста не является доказательством его отсутствия дефектов.

Остаются189 Bin script candidates, indirect root dependencies, semantic property/storage review, обязательная матрица, общий контроллер, joint ASan, ConditionSpec/queue/publication и научные протоколы. Динамические imports и внешние callers должны быть проверены перед последующими удалениями. Это частичная миграция этапа9.
