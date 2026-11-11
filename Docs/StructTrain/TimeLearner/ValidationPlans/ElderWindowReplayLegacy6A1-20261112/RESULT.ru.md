# Независимый legacy6 diagnostic replay — Elder,12.11.2026

**1/1 PASS**, без failures/errors/skips. Текущий dispatcher source46a2ba55223fdf1630d6f1a2f4592534c920e186 восстановил настоящий463-member Git primary archive и production replay воспроизвёл groups12/14/18:recorded valid/missing/missing; full observation valid/ambiguous/ambiguous. Training outcome invalid_observation и отсутствие сертификата сохранены.

[Unittest](completed/worker/validation/unittest.log), [результат](completed/worker/validation/result.json), [полное восстановление и replay](completed/worker/tmp/legacy6-diagnostic-replay.json). Это анализ реальных сохранённых CSV, без расчёта новой модели; full-window ответ не повышается до Train certificate.

[Outer result](completed/controller-result.json), [closure/released lease](completed/closure-and-reservation.json):процессы закрыты, lease released, diagnostics clear. Source/fixtures до и после побайтно одинаковы; original Git archive unchanged. [SHA256 полученных исходных readbacks](completed/readback-integrity.json). Новый source7 Branch replay и native-window zoom ещё требуют отдельной приёмки.
