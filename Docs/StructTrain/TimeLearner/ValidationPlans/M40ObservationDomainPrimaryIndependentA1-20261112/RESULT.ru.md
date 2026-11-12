# Независимый full-domain N4 DATA replay: 2/2 PASS

Свежий Git-checkout e02389ed3d1255f737debe28e9b4f91f407d2754, package fingerprint ac53d7c6913d149ff1c234385e23271c9857ea592448f782d2f4f6639e227e94. Оба точных ID выполнены, без failures/errors/skips: [unittest](completed/worker/validation/unittest.log), [result](completed/worker/validation/result.json). Unittest289.879s, outer312.020s, execution completed/exit0 и diagnostics clear.

Восстановлены все2279 членов combined A1 и2107 членов Branch A2. Проверены archive hashes/полный namespace; production package7/summary8 readers заново проверили full/omission primary и измерения, физический граф, trained L, full-domain candidate frames, исходные допуски и recovery ledger. Порча извлечённого CSV отвергнута в обоих пакетах, embedded primary не подменил повреждённый внешний mirror. Исходные compressed archives не менялись.

| Модель/попытка | Подтверждённый исход | Измерения и структура |
|---|---|---|
| Classic A1 | valid / invalid_observation; certificate null |42 groups/252 probes, L45,1,1,1;5 recovery deliveries|
| Branch A1 | timeout / unverified_execution; training outcome unknown |652 CSV сохранены; итоговых package/summary нет|
| Branch A2 | valid / budget_exhausted; certificate null |105 groups/630 probes, L27,27,26,1; recovery deliveries0|

[Combined receipt](completed/worker/tmp/observation-domain-combined-independent.json), [Branch receipt](completed/worker/tmp/observation-domain-branch-independent.json). Graph audit сохраняет stock physics2000Hz, отсутствие LTMembrane, неизменные threshold/feedback. Этот тест не восстанавливает controller checkpoint/search traversal и не доказывает native execution или сходимость. Нулевой recovery_count Branch не проверяет эффективность recovery.

[Whole group closed и leases released](completed/closure-and-reservation.json); [controller](completed/controller-result.json). Tool/source/fixture snapshots до/после совпали побайтно, heartbeat_errors пуст. [SHA256 всех15 raw proofs](completed/readback-integrity.json). Полные исходные пакеты остаются в [combined corpus](../M40ObservationDomainCombinedClosedCorpusA3-20261112/RESULT.ru.md) и [Branch corpus](../M40ObservationDomainBranchClosedCorpusA3-20261112/RESULT.ru.md). Оригинальные ORIGIN.independent_semantic_replay_accepted=false сохраняются как сведения на момент публикации; эта приёмка записана отдельно.

Это независимая Python-проверка сохранённых DATA на M40, без новых native запусков. Ordinary Test этих незавершённых обучений не выполнялся. Temporal отчёт, большой native import/export/performance, Elder и остальные этапы исходного плана остаются открытыми.
