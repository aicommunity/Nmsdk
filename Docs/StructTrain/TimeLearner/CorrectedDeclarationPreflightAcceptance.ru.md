# Corrected declaration preflight13,04.11.2026

На Elder source `b7bb1dba24107cb310519e76da4933d67344fc46` прошёл13/13 actual metadata/CLI tests на полном реальном public coordinator corpus. Нет failures/errors/skips. Проверки используют реальные declarations из четырёх завершённых cold Train pipelines, не создают поддельные learned models и не запускают компоненты. Прежний df5/A3 результат12/13 сохранён в [предыдущем evidence](../../../Reports/StructTrain/TimeLearner/s10-completed-dependent-gates-elder-a2/outcomes.json).

Дефект был в CLI fixture: policy JSON null отклоняется generic object loader до run_pipeline. Изменён только test file и doc: unauthorized{} допускает semantic preflight, не предоставляет права запускать native process. Ожидания unknown_response_criterion и отсутствия output каталога прежние. Git blobs production managed_declaration/managed_pipeline/scorer совпадают сdf5. Этот результат не является изменением алгоритмов или ослаблением criterion.

[Полный primary bundle](../../../Reports/StructTrain/TimeLearner/s10-declaration-preflight-corrected-elder-a4/bundle.json), evidence `47e5316c628f24183afe7e2c07deefac3af27eaf`; [независимый readback](CorrectedDeclarationPreflightVerification.json). Архив18 448 bytes,9 members,SHA256 `d8d8b6e5870ef57808e9a5b43b86aa199b712b51a8bf1d7932f99ab92a02007c`. Проверены18 published checksums,все9 members,292 production Python blobs и точный two-path test-only diff. Whole parent group закрыта, operational lease released. Локально только Git/hash/archive metadata; tests выполнены на worker.

Actual live routing A3 на том же sourceb7 и baseline33 runtime продолжает6 tests/10 ожидаемых native units. Новый полный coordinator/scorer regression, все physics/modes/fault/cancel cases и научная матрица не подтверждаются13 metadata tests. Pending code branch не объединяется в develop по этому результату; весь план остаётся частичным.

## Место для следующей сборки

На Elder свободно около5.7GiB, recognition helper ждёт6GiB. [Очередь maintenance](../../../Reports/StructTrain/TimeLearner/s02-obsolete-object-cleanup-queued-a1/job.json) подтверждена живой и ждёт actual live whole-group closure/release. Она не запускает компилятор или нейронные модели и не расходует их slot; отдельная path-only maintenance lease дополняется проверкой disjointness со всеми held production resources.

Разрешены только воспроизводимые.o/.obj/.a/.pch из точных старых build-test-switch-off-b3/build-test-switch-on-b3. Сохраняются все остальные build files, CMakeCache, runtime, source и experiment primaries. До удаления проверяются canonical paths, отсутствие symlinks/Git внутриbuild, текущие process cmdline/cwd/exe/maps и фактический deploy root внеbuild. Hash inventory и CMakeCache сохраняются до unlink; неизменность прочих файлов/runtime проверяется после. Recursive directory deletion не используется. Старый gate test-switch принят ранее, evidence57383f8d; эти build products можно восстановить из source/cache.

Maintenance ограничена512MiB и начинает собственный3600s limit после завершения очереди. Никакие logs/models/data не удаляются; runtime нового build не переиспользуется. На момент этого readback удаление не началось; освобождение места не заявлено выполненным. Результат и failure должны публиковаться отдельно. Общая вместимость production registry не меняется.
