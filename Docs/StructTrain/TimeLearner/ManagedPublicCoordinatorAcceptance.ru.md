# Проверка public managed coordinator,04.11.2026

На Elder успешно выполнены8 actual CLI integration tests без failures/errors/skips. Source package `2cc27b9f3192ccd5a11d5dcc8189f68205205b15`, runtime root `f679d0410dd00a36995f9d32cc03812438819bb7` / Pulse `541bf89b9966f63ca5131fa57a31a9ae3f5820ea`. Это приёмка адресного поведения кандидата; production-код этой ветки ещё не объединён в develop.

Четыре положительных инженерных случая: Classic/Branch×ModelSpec1/2, cold Exact N1 Train→export→measured calibration grid с отдельным подтверждением выбранного порога→frozen evaluation. Команды run с остановкой после Train, continue на завершённой границе и повторный continue проверены через public CLI. Уже завершённые этапы повторно не запускаются. Четыре отрицательных случая Classic/Branch×N0/N1: Train остановлен, export и Test отсутствуют. Готовый обученный граф вместо cold Train не устанавливался.

Все20 independently managed native units свежо проверены закрытыми, общий operational lease освобождён. У каждого случая сохранён исходный SQLite registry; все8 баз проходят integrity_check. Полные журналы, learned states, declarations, наблюдения, runtime и process bindings находятся в [primary bundle](../../../Reports/StructTrain/TimeLearner/s10-managed-public-coordinator-normal-a2/bundle.json). Сжатые первичные данные10 175 056 bytes; SHA256 `a7c0d181d73cb5263657fb4f4275e1850aaf9e20d72ab462a0544c964fe7c9e1`. Git evidence commit `c40e992d9729b0f1b2c881668e00042b066c14ef`.

Независимая локальная проверка метаданных сверила20 опубликованных файлов,2215 архивных members,288 production Python blobs с Git source,20 различных unit IDs и8 SQLite primary databases. Численные тесты локально не выполнялись. [Подробный readback](ManagedPublicCoordinatorVerification.json).

## Ограничения

Same-Matrix engineering cases с двумя входами не подтверждают stock4-input/8-pattern классификацию, независимую оценку, устойчивость к перестановкам/ITI или влияние LT-мембраны. Return true, закрытый процесс и completed_boundary не подменяют научный PASS. Состояние ресурсов и успешность тестов проверены отдельно.

Первый A1 не запускал модели: obsolete prerequisite guard отказал до reserve из-за гонки между закрытием процесса и записью release-event. Полный отрицательный readback сохранён в [прежнем архиве](../../../Reports/StructTrain/TimeLearner/s06-corrected-baseline-and-dependency-readbacks-a1/outcomes.json). У A2 ожидание основано на принятом worker_dependency API, фактическом kernel closure и registry release.

Для последующих проверок поставлена последовательная очередь: corrected shared-lifecycle SDK build/core18/full133→reconciliation7→declaration13→live recognition routing6. Очередь не означает PASS. Reconciliation и preflight используют фактический корпус A2; live routing использует отдельно подтверждённый baseline33fc runtime. Отрицательный результат сборки не запрещает независимую проверку Python после подтверждённого освобождения ресурсов. Live routing дополнительно требует успешной declaration13 и baseline133. [Постановка очереди](../../../Reports/StructTrain/TimeLearner/s10-managed-followups-queued-a2/job.json).

Остаются full coordinator regression на объединённом candidate package, scorer readers, active cancel/fault/reboot/reconciliation matrix, semantic ConditionSpec binding, queue dispatch, публикация, все физические профили/режимы и полная научная матрица. Общий контроллер и совместный ASan ещё не приняты. Полностью закрыт только этап0 исходного плана; этапы1–12 частичны.
