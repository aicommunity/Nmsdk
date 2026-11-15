# DATA directory-tree controller:18/18 PASS

Source d33af820e8a5fb57afca4b7a78767887a643fd7b, package ab147bce6ca40e2eb8ab864f5cb9e4c502dc0ea4781d30b12f8bb3e6c92f3cf4. Все18 exact IDs без failures/errors/skips, unittest0.022s/outer23.319s. Production stock registry admission принимает READ parent dirs, дедуплицирует общий parent и отвергает file lease штатным ReservationError. Остальные request/identity/limits/path/runtime guards сохранены.

Execution completed, diagnostics clear, heartbeat_errors пуст, whole group closed, ровно один lease released; tool/source/fixture before/after byte-equal. Raw13files сохранены в completed, hashes в readback-integrity.json. Это metadata/actual resource-admission API; actual native consumer и crash/recover model cases этим не подтверждаются. Первые metadata18A1 и native2A1 отказы сохранены, A2 native не запускался. Следующий separate native2A3 использует тот же tested Tool и прежний принятый SDK36.
