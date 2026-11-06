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
