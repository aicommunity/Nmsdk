# Native process policy:15 portable tests на M40

Принят узкий evidence-подэтап:15/15 tests,0 failures/errors/skips, без нового
модельного расчёта. Proof0b02592ff40680787aca30df878b81c6479db8c5;
[независимая сверка](PipelinePolicyPortableVerification.json) проверяет54
archive members,279 Python source blobs source1fd77d34f и два точных набора
process records из ранее принятых real C++ normal/ASan codec/storage runs.
Новый metadata worker закрыт, lease восстановлена после kernel closure.

Проверены переносимость без исходного SDK и ошибки при замене policy/лимитов,
PID, terminal exit, cooperative ack, whole-group closure, duplicate mappings,
переподписанном request и подмене scope на launched_executable_only. Результат
не является authentication произвольного файла о kernel и не означает native
execution attestation либо scientific PASS.

Реализация pipeline/calibration/PostTune hooks, CLI и versioned manifests
находится в codex/timelearner-pipeline-containment source
1fd77d34feeabfb6026d4d8db880823bb03e90e7. Она не включена в develop:
реальные production jobs нового backend, legacy A/B, cancel/timeout и
аварийный recovery ещё требуют адресной серверной приёмки.

Выявлено дополнительное требование к recovery: contained_process запускает
отдельную user-systemd unit. Такая unit не обязана быть вложенной в cgroup
управляющего worker. Нынешний recover_closed_worker проверяет только unit
самого lease owner; это недостаточное основание освобождать SDK/runtime,
если из worker созданы дополнительные units. Нужны явная регистрация launch
intent до старта и проверка полного зарегистрированного графа при release/
recovery. Конкретный fault case следует воспроизвести на изолированном ledger,
не меняя leases и каталоги работающих normal304/ASan K1.

Этап10 остаётся частичным. Приняты только эти metadata evidence и их
ограничения; код pending worker integration и поддержка всей очереди не
получают приёмку по15 portable tests.
