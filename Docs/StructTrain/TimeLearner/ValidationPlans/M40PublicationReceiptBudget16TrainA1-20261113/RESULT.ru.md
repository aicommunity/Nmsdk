# Classic N4: полный конечный запуск принят, сходимости нет

Job s07-publication-receipt-budget16-train-m40-a1 завершён completed/exit0 за3070.1564s,1/1 actual production CLI check, без failures/errors/skips. Full run-manifest/package/physical readbacks приняты; heartbeat_errors=[], diagnostics clear, outer и оба native child закрыты, lease released. Source/tool/fixture before/after bytes совпадают. [15 raw подтверждений](completed-readback/integrity.json).

Native Console завершён за2070.9213s в прежнем2100s лимите; [state/summary/execution и исходные runtime proofs](NATIVE_COMPLETED.ru.md) сохранены. Это устраняет прежний native finalization timeout в данном ограниченном опыте, не доказывая универсального ускорения и не меняя старый timeout outcome.

Training outcome budget_exhausted/native_training_time_budget_exhausted; reference_complete=true, certificate=null, completed_boundary=false.58 search probes/28 edits,15 complete candidate evidence records,13 rejected candidate windows,28 assessed resistance domains. Actual state3b8a160f2fe6f5ace6aa377f5d42117bcc922bcdd746358ca8d7c34fc67a6b1c: L22,1,1,1, Rs86MΩ/Ns1.

**Конечный L22 не является измеренным успешным кандидатом.** Все15 retained valid candidate records относятся к input0: L1 при86MΩ и2.880071555MΩ, затем L2..14 при86MΩ. Ни один не within_timing. Последний L14 имеет timing residual−0.3494999999999777s и amplitude residual−0.01055690138491372 при исходных sync0.02/amplitude1e-5. Ни один candidate model_revision не равен actual terminal revision; final_group_ids=[] — fresh final certificate не получен. Legal/assessed Rs domain не равен фактически предъявленному измерению.

Исходный signed scientific job совпадал с прежним, но wall-budget при параллельных Python задачах дал58 вместо62 probes. Поэтому сравнение execution/export допустимо, а равенство конечных L или speedup алгоритма не заявляется. N1 амплитудные остатки у несинхронизированных геометрий не доказывают физическую недостижимость нормализации.

Полный закрытый corpus1279 regular files/865242819B+2 glog aliases сохраняется отдельным compact collector. Новый обычный Test/calibration не запускается автоматически. Следующий адресный шаг — воспроизводимый анализ candidate/domain/terminal distinctions и отдельно объявленная конечная L/Rs диагностика, если она требуется после анализа; без автоматического увеличения бюджетов/допусков или изменения assigned-peak смысла. SeriesD не возобновляется.

[Полный primary corpus сохранён](../M40PublicationReceiptBudget16PrimaryA1-20261113/RESULT.ru.md):1281 logical members/46.04MB XZ, без потери original bytes.
