# Exact compact primary и rescore:10/10 приняты

Job s11-declared-diagnostic-primary-m40-a1 завершён completed/exit0 за1261.9628s.10/10 actual production checks прошли без failures/errors/skips; diagnostics clear, heartbeat_errors=[], whole group closed, lease released. Source/tool/fixture before/after bytes совпадают. [14 raw подтверждений](completed-readback/integrity.json).

Исходный native/model.json282794133B и все8 trial JSON сохранены в original bytes:28 logical members/320078865B в19575080B XZ. Schema2 archive SHA256 fe5fb13532f0ea0155bf3c4aaa3b1d2e179f583f74eef44ce4e0125fc2b7ef1e. Explicit384MiB member limit применён через production API; default256MiB, archive128MiB/expanded768MiB/64members ограничения не повышались.

После restore production audit_primary повторно проверил модель, binding/план восьми проб, полноту и исходные метрики. Model revision89681f2f4ee996b4a1208b18cbdaa3c3c2c2b487e78d7aa56ccec1d37a8a1f0b, training=budget_exhausted, TP0/FP0/FN1/TN7, diagnostic_only=true, scientific_verdict=null. Семь молчаний foil не подтверждают target detection. Source Train timeout не исправлен задним числом.

[Git primary](../../../../../Reports/StructTrain/TimeLearner/Budget16DiagnosticPrimary-M40-20261113/bundle.json) — selected DATA subset с полным model и observations; это не полный runtime directory и не самостоятельная аттестация native execution. Producer61314dcca822705eb45ee4105e7a26b60465aade; независимый bundle-only Elder replay ставится отдельно, его успешность пока не заявляется.
