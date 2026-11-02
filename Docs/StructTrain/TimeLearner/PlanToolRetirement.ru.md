# Исторические инструменты плана20 октября

Снимок для извлечения: `0c12a71757d4eb34412f043028f56edfa38ba974`. Удалены16 файлов без wrappers;
семь cable-model файлов побайтово совпадают с отдельным evidence-каталогом.
Остальные девять относятся к старому campaign workflow, а не текущему native runner.
Ни одна модель, конфигурация, primary trace или историческая оценка не пересчитана.

| Прежний путь относительно tools | Основание |
|---|---|
| `audit_matrix_wiring.py` | Старая campaign-specific утилита; retrieval содержит полный исходный commit/blob/hash. |
| `cable_model/cable.c` | Точная копия evidence; исходники обеих копий доступны в Git. |
| `cable_model/cable2.c` | Точная копия evidence; исходники обеих копий доступны в Git. |
| `cable_model/classic_full.py` | Точная копия evidence; исходники обеих копий доступны в Git. |
| `cable_model/ideal_delay.py` | Точная копия evidence; исходники обеих копий доступны в Git. |
| `cable_model/library.py` | Точная копия evidence; исходники обеих копий доступны в Git. |
| `cable_model/oracle.py` | Точная копия evidence; исходники обеих копий доступны в Git. |
| `cable_model/sweep.py` | Точная копия evidence; исходники обеих копий доступны в Git. |
| `check_model_wiring.py` | Старая campaign-specific утилита; retrieval содержит полный исходный commit/blob/hash. |
| `compare_sweep.py` | Старая campaign-specific утилита; retrieval содержит полный исходный commit/blob/hash. |
| `repair_matrix_inputs.py` | Старая campaign-specific утилита; retrieval содержит полный исходный commit/blob/hash. |
| `repair_model_wiring.py` | Старая campaign-specific утилита; retrieval содержит полный исходный commit/blob/hash. |
| `select_cases.py` | Старая campaign-specific утилита; retrieval содержит полный исходный commit/blob/hash. |
| `summarize_run.py` | Старая campaign-specific утилита; retrieval содержит полный исходный commit/blob/hash. |
| `tl_probe_kernels.py` | Старая campaign-specific утилита; retrieval содержит полный исходный commit/blob/hash. |
| `trace_soma_peaks.py` | Старая campaign-specific утилита; retrieval содержит полный исходный commit/blob/hash. |

`script_migration.json` хранит все16 точных записей. Runtime эквивалентность
старого regexp wiring/repair, fixed-four-soma analyzer, kernel-vs-offline-cable
сравнений и новой native модели не заявляется. Эти предположения нельзя
механически переносить в maintained pipeline: native graph readback, arbitrary-N
observations и native probes уже имеют отдельные контракты.

Текстовых code consumers в текущих Scripts/App/Tests, Bin и PulseLib не найдено.
Это проверка tracked source, не произвольных внешних consumers. Исторические
карточки/README сохранены и явно помечены как снимки с Git-ссылкой на инструменты.

Требуется серверная metadata-приёмка всех64 migration records (62 retired +2 moved),
включая отрицательный fixture, возвращающий старый путь. Длительные numerical
jobs используют прежние immutable sources/builds/runtimes и не изменяются.
Полный этап9 открыт: прочие Docs/Bin/PulseLib scripts, активный специализированный
анализ и declarative job specs ещё требуют миграции.
