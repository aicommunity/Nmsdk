# Полные native32 корпуса двух workers: DATA replay16/16 — принято12.11.2026

**16/16 PASS**, без failures/errors/skips: [исходный log](completed/worker/validation/unittest.log), [машиночитаемый результат](completed/worker/validation/result.json). Анализатор7e4fa2a9df79ec0d76e0bc251acf80e49b5d2288, package506905b877593ac598388bf6f5cc9fc560fb6f8cd20aed5a6ed712dbbdb8ecb9; actor40e28802c29014ec8a5af0f8763aa607ad9a986a. A1 не запускалась: различие original ORIGIN dialect исправлено до исполнения, исходные архивы не менялись.

| Исходный корпус | Размер xz | Members | SHA256 xz |
|---|---:|---:|---|
| [Elder](../../../../../Reports/StructTrain/TimeLearner/RecoveryConsole32NativeClosedCorpus-Elder-20261112/bundle.json) |6041800|2735|ecd6a2570e4cdbac1aaac6c1f0d6e604cfc13f38032188732434fbbe46b8e42a|
| [M40](../../../../../Reports/StructTrain/TimeLearner/RecoveryConsole32NativeClosedCorpus-M40-20261111/bundle.json) |6137372|2735|3e17d8a92a7ede6e0d23be7b21a82749ffc5564d7756c08e957641db6b857d36|

Production portable reader восстановил и сверил каждый member обоих архивов. Все32 materialized log aliases каждого корпуса сохранены; перед исключением aliases из подсчёта исходных regular-file artifact rules проверены hash/размер соответствующего сохранённого log target. Это не восстановление live authority или исходной формы symlink.

Для каждого worker отдельно проверены:

- все32 исходных JUnit IDs, их статусы и totals:4 active-Build guards,7 recovery Console producers,11 legacy wire controls,10 recognition cases; каждый artifact rule исходного job;
- четыре настоящих publication datasets source7/summary8 и обе сохранённые execution5 wrappers, по8 проверок wrappers на корпус;
- десять conversions, включая stopped diagnostic и asymmetric C0, и20 реальных полных target/foil trials; неизменность frozen model, повторное преобразование, соответствие количества спайков и глобальных максимумов сохранённым samples;
- отказы на coherently rehashed wrong factor, relabel stopped→ordinary recognition, ошибочный spike count и изменение frozen model hash.

Использованы существующие production readers и шесть унаследованных recognition checks без копирования алгоритмов. Wrapper arguments остаются исходными unit inputs; их повторная проверка не создаёт внешнего Console execution. Отрицательные Build/pre-source/foreign-ledger и legacy C++ результаты здесь повторно проверены по исходным JUnit/artifact rules; их тела не исполнялись заново в Python. Все64 исходных C++ cases и40 trials являются сохранёнными данными, а не новыми native запусками.

Unittest438.779s, outer457.142s. [Controller](completed/controller-result.json):completed, whole group closed, diagnostics clear. [Closure/leases](completed/closure-and-reservation.json):закрыто, released; heartbeat_errors отсутствуют. Actor/source/fixtures snapshots до и после совпадают. [Контрольные суммы точных readbacks](completed/readback-integrity.json). Временные835MB восстановления создавались последовательно на Data и удалены штатными class cleanups; нового удаления исходных файлов не выполнялось.

Scope: SDK8362d58f4d6576a0c8b0cc7633270976dff1df7b/Pulse1110808f4ad1f67538dadc6fe1d3f097e00c0630; технические N2/Sync0.2 fixtures. Не N4/default0.02, не независимая научная матрица и не полная приёмка этапов0–12. Поле independent_python_replay_accepted=false в исходных ORIGIN сохранено как знание producer на момент публикации; новая отдельная приёмка зафиксирована здесь и не переписывает происхождение архива.
