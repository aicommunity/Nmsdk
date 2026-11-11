# Ранняя проверка лимитов worker

Повод: stock fair-domain launcherA1 задал36h при штатном максимуме24h.
Контейнер корректно отказал, но только после ожидания prerequisites.
Native worker и Train не запускались; исправленный A2 использует24h и прежние
бюджеты каждой пробы/Train. Это ошибка постановки outer execution, а не модели.

Новый production-модуль `process_limits.py` содержит один side-effect-free
`validate_limits`, используемый `contained_process.start/_start` и
`contained_runner.execute`. Правила прежние: целые memory_bytes/tasks с прежними
пределами, finite wall1..86400s, boolean вместо числа не принимается.
Лимиты не обрезаются и не заменяются автоматически. Runner сохраняет прежний
`invalid_contained_wall_budget`; start — `contained_limits_invalid`.
Public start проверяет лимиты до создания managed reservation context.

Перед постановкой в очередь можно выполнить на worker:

```text
python -m Scripts.StructTrain.TimeLearner.process_limits --memory-bytes 4294967296 --tasks 128 --wall-seconds 86400 --output NEW.json
```

Exit0 означает только допустимость лимитов. Никакой сервис, резервирование,
расчёт модели или scientific PASS эта команда не создаёт. Существующий output
не перезаписывается;36h отвергаются до создания результата. Проверка свободных
ресурсов, namespace/runtime, очереди и эффективной конфигурации остаётся
обязанностью следующих production-путей, а не подменяется этим preflight.

Подготовлены два адресных checks: реальный CLI24h/36h и отказ обоих actual
entry points до manifest/context/output side effects. Вместе с ними требуется
серверная регрессия всех13 ContainedProcess и11 ContainedRunner cases:
реальные kernel caps, suffix binary, capture/maps, timeout/cancel/descendants,
ошибки и tamper/reuse. Тесты не исполняют нейронные модели.

Ветка создана от develop9b380a3 с отдельным no-ff merge pending fair-domain
prerequisites. Это не их promotion в develop. Идущая stock-серия сохраняет
свои замороженные source/runtime; этот Python-кандидат её не меняет.

Первый серверный gateA1 выявил зависимость двух прежних crash-controller
fixtures от cwd: дочерний `python -c` не находил Scripts при запуске тестов
из `/tmp`. В fixtures явно задан root пакета; источники crash/recovery,
ассерты17/19 и настоящее cgroup поведение сохранены. На M40 первые26 дали
24 passed/2 failed именно по этому import. Elder остановился до tests из-за
обязательных declared demands в существующем capacity-schema2 ledger;
новый worker объявляет slot1/memory2GiB/disk128MiB, сохраняя прежнюю capacity.
Эти отказы не являются приёмкой26 cases и сохраняются отдельно от исправления.

Исправленный [gateA2 принят на обоих серверах](WorkerLimitPreflightVerification.json):
26/26 без failures/errors/skips на каждом, одинаковые26 IDs и353 source hashes.
Сверены301/302 archive members и по20 actual final-membership records;
обе worker groups закрыты, leases released. Сохранены исходные failedA1
archives281/5 members и их353 source hashes. Source correction не затрагивает
идущую нейронную серию. Общая scheduler/fault matrix и миграция всех временных
launchers этим отдельным substage не завершены; develop ещё не обновлён.
