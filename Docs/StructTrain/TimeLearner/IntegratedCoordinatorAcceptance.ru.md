# Integrated coordinator: normal8 принят, ASan цепочка исправлена

## Coordinator8 на новой SDK

Native SDK root `2e0618110a9abb48b94f6edc6b63c51f829ec810`, Pulse12d:8/8 actual CLI tests, без errors/failures/skips. В отличие от A2, отказавшего до моделей, A3 прошёл резервирование и весь pipeline. Для четырёх positive случаев Classic/Branch × ModelSpec1/2 выполнены cold Train, завершённая boundary continuation, export, измеренная same-matrix calibration/confirmation и frozen evaluation. Четыре N0/N1 stopped controls не запускают export/Test.

[Полный primary](../../../Reports/StructTrain/TimeLearner/s10-integrated-coordinator-normal-a3/bundle.json), data commit `26a602e84adef89056021a671055d8272330d810`:2233 файла,526188809 несжатых байт,10214688 compressed, SHA256 `599d9659b3a1692ca0081dacbaf65a2fded5c54899337e5a839cc7b06007c13c`. Каждый архивный файл сверён; восемь SQLite registries прошли integrity_check. [Независимая проверка](IntegratedCoordinatorVerification.json) выводит20 фактических уникальных native units/CLI interface receipts из primary и проверяет all_processes_closed/bound_cgroup каждого результата. Fresh operational dependency после закрытия всей группы подтверждает released lease.

Все четыре positive frozen controls:TP2/FP0/FN0/TN2. Это инженерные двухвходовые same-matrix проверки переноса/калибровки на конкретных условиях; не stock4-input/8-pattern scientific PASS и не независимое обобщение. ModelSpec1/2 — варианты сериализации, не независимые повторения. В derived scorer остаются source_training_evidence_checked=false, native_execution_verified=false, condition_identity_attested=false: сам scorer не является свидетельством этих проверок. Адресная проверка actual native units/loaded-runtime делается по отдельным process artifacts; общий production condition/provenance контур по всему исходному плану не принят.

[Запланирован полный temporal report](../../../Reports/StructTrain/TimeLearner/s11-integrated-coordinator-visual-a1-pending/job.json):16 Train/calibration/frozen/negative-Train reports. Primary восстановлен на Data M40 через Git, все2233 файла повторно rehashed. Renderer source8c9ee9f6, без нового обучения; все зарегистрированные паттерны и сомы, реальные shared-input импульсы, native samples без downsampling, PNG1920×960 и zoom≥8px/tick. Полный HTML/PNG/SVG/PDF — cache на M40; в Git остаются compressed primary и выбранные рисунки после visual QA. Пока генерация/QA не завершены, графики не считаются принятыми.

## Исправленные зависимости ASan

Старые queue151566/start294496748 и168864/start294783992 проверены по kernel identity, UID, exact command и отсутствию created build/native unit. Обе прекращены pidfd SIGTERM, exit подтверждён; working ASan304 не затронут. Old build worker также импортировал worker_dependency из bootstrap, где файла нет; A2 использует точный существующий source-worker-dependency-normal-a2.

Новая цепочка:

1. Текущий isolated SDK802 ASan304 завершает все304 tests и archive; agent публикует его данные в origin и проверяет closure.
2. Owner/readers A3 ждёт completed/valid/passed304, fresh closed/released и native304-published-origin.json с точным evidence commit/archive hash. После этого отдельные fresh-process owner8 и readers128.
3. Build A2 ждёт их PASS/closure и ресурсов; собирает отдельный SDK2e/Pulse12d, -O1 -g1 ASan, cap4GiB/21600s. Явно NMSDK_BUILD_PARALLEL_JOBS=1 и CMAKE_BUILD_PARALLEL_LEVEL=1, помимо --parallel1. SDK802/runtime не меняются.
4. Focused8 A3 ждёт новую сборку; отдельная группа42GiB/25200s, native budget21600.
5. Lifecycle133 A3 ждёт focused8 PASS/closure; отдельная группа42GiB/86400s, native budget82800 и3600s на archive/закрытие.

Старый единый parent129600s не поддерживался backend (максимум86400). Вместо обхода проверки создано два bounded этапа. В обоих новый explicit native_partition запускает каждый case отдельным процессом; список8+133 сохранён, каждый actual XML/loaded mapping/identity остаётся primary. Численные tolerances/model times не меняются; budget exhaustion или invalid observation не даёт PASS. Если предшественник не был запущен, downstream queue завершается явным отказом, а не бесконечно ждёт.

[Exact deployed scripts, cancellation и live readback](../../../Reports/StructTrain/TimeLearner/s10-asan-chain-replacement-a1/embedded-source-verification.json), data commit `a241fc84b7783ccceba30f4998dcc94631992cfc`; [checksums и проверка](ASanChainRecoveryVerification.json). Четыре новые очереди были kernel-live, waiting; это не запущенные будущие builds/tests. Source scripts сравниваются с AST literals; source roots/tool861 и fixtures103+6 остаются явно разделены. Git-публикация304 — работа агента, не дополнительное согласование пользователя.

Исходные этапы1–12 и общая цель открыты. Normal8+133 иcoordinator8 не подменяют ASan, остальные модели/режимы/математические проверки, научную матрицу или финальную документацию.
