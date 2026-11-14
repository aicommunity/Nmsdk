# Контроль порядка A3: штатный владелец native reservations

[Полный научный протокол A1](../M40ClassicN0OrderMatrixA1-20261114/PLAN.ru.md) неизменён:64 пробы/8 позиций target, та же модель, threshold0.012765548843211696,2000Гц,2с/reset-per-trial, прежние budgets и все baseline/frozen/DATA проверки. Нового обучения/порога/физики нет.

A1/A2 неверно объявили operation.kind=python-validation, создающий дочерний unittest. Для managed native reservations штатно нужен python-controller-validation: run_suite работает внутри main owned worker, что сохраняет строгие PID/start_ticks/budgets. Это уже реализованный production путь owned_python_job; API reservations не меняется. A1 отказал на PID, A2 — на managed_controller_not_lease_owner; оба до нового native execution.

A3 задаёт python-controller-validation. Worker до большого source audit проверяет initial_main_pid==os.getpid(), running и точное членство cgroup. Неподходящий режим теперь отклоняется сразу. Снятие/ослабление managed-controller проверки запрещено. Новые source/request/output отдельные, исторические failures сохраняются. На момент декларации подготовлено, запуск/результат отдельно.
