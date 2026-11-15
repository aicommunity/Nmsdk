# DATA audit сохранённого индекса budget16

Production audit_candidate_window_archive проверил исходный composite-measurements/index.json из закрытого failed job, без повторного Train. Process completed/0,66.815637s, whole group closed, diagnostics clear. Проверены67 records и398 primary files; geometry/selection/reference set/counters и source bindings пересчитаны. [Исходные файлы](completed/readback-integrity.json).

Archive SHA1b49827ad66437a1eef5336cb2556e62bcb238b85a31d0c9e893cb12d4210565. Текущие runtime budgets этим вызовом не привязывались: current_runtime_budget_binding_checked=false. Native execution/certificate/live authority не восстанавливаются. Поэтому успешный DATA audit не делает failed Train завершённым и не устанавливает training outcome или финальную модель.

Сохранённый индекс содержит исходные67 групп, включая неполную последнюю; он позволяет анализировать отдельные измерения без повторного обучения. Для итогового learned-state и Test необходим исправленный production export.
