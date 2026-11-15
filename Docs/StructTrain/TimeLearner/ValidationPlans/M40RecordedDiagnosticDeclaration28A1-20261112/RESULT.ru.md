# Диагностический controller: 28/28 адресных checks

M40 job `s10-recorded-diagnostic28-m40-a1`, source `742bc6618f47054e9db72b91be6b0b3e27c15cd2`, Tool40e28802. Все28 точных IDs прошли без failures/errors/skips; execution completed за22.300 s, whole group closed, lease released, diagnostics clear. Source/tool/fixtures snapshots before/after побайтно равны;13 raw proofs сохранены в `completed/`.

Область:18 прежних controller schema1/path/identity/runtime/resource guards,9 новых schema2 diagnostic declarations и1 тест production Qt decoder с корректным payload и wrong-size/truncation/trailing/wrong-hash negatives. Закрыты произвольные операции и поля, отсутствующие/лишние/reused input roles, подмена raw binding, escaping/alias cases, неполная матрица и неподтверждённая revision. Один case требует только собственные inputs; legacy schema1 не получает диагностический режим молча.

Эти28 checks не запускают нейронные модели и не подтверждают качество классификации. Новый полный Console запуск двух stopped N4 моделей и16 trial observations объявлен отдельно в `../M40RecordedN4Diagnostic16A1-20261112`. Статус его actual execution определяется только собственными kernel/terminal/primary proofs.
