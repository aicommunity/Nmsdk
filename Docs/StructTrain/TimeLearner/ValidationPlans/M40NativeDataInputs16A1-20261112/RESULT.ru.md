# Native DATA inputs5:16/16 IO и legacy reader проверок приняты

Source85dffd2de, package fingerprint231f28fd3d60ca856d96b6c0754e884dad2eb3231dd49748dc584ab6c08ef3ea. Выполнены все16 точных ID, без failures/errors/skips: [исходный unittest](completed/worker/validation/unittest.log), [result](completed/worker/validation/result.json). Unittest0.020s, outer25.021s; completed/exit0, diagnostics clear.

Восемь новых IO controls проверяют exact staging, изменённый source, повреждение native working copy, лишние entries/descriptor, исходный wrong digest, traversal/aliases/bool/unknown fields, symlinks и явную schema5. Восемь прежних controls проверяют настоящий11-case JUnit/common-codec-11 и восстановление environment, без запуска нового нейрона.

[Whole group closed/lease released](completed/closure-and-reservation.json), [controller](completed/controller-result.json). Source/tool/fixture snapshots до и после совпали побайтно; heartbeat_errors пуст. [SHA256 всех13 raw proofs](completed/readback-integrity.json). Это адресная проверка IO/schema/reader, не actual native consumption файлов, не kernel validation нового model consumer и не весь этап10. Следует свежий SDK с двумя NativeRecordedRecoveryArchive cases и явными DATA inputs5.
