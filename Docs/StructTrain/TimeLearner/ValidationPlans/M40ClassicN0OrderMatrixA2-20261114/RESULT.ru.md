# A2: неверно выбран штатный режим validation

Outer process_error590.3652878827415с, whole group закрыта; unit1 выполнен,1 error,0 failures. После source audit и подготовки job reserve отказал с managed_controller_not_lease_owner: unittest был дочерним процессом. Новая native модель не запускалась; результатов64 проб нет.

Причина — operation.kind=python-validation в launcher, тогда как штатный python-controller-validation выполняет suite в главном owned worker. Строгая проверка PID/start_ticks/budgets в resource API корректна и не меняется. [A3](../M40ClassicN0OrderMatrixA3-20261114/PLAN.ru.md) исправляет режим и проверяет initial PID/cgroup до большого source audit. Научный протокол неизменён. Предыдущая попытка A1 остановилась раньше на той же неверной постановке запуска.

[Log](completed/worker/validation/unittest.log), [closure](completed/process/whole-group-closure.json), [integrity](integrity.json). Literal producer 5e6c978d71f0fdad749249df0519e30871ae78f9, pack SHA256 4c51512674ba1186139d3b599bb9128eb7e0147aa636b6b20c81a6227b0fc029.
