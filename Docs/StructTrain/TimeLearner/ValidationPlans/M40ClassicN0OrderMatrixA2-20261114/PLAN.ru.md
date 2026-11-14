# Classic N0: повтор неизменённого контроля порядка A2

[Полный протокол A1](../M40ClassicN0OrderMatrixA1-20261114/PLAN.ru.md) сохраняется:64 реальные пробы, target на каждой позиции, тот же stopped graph, порог0.012765548843211696,2000Гц,2с/reset-per-trial; без Train, новых tolerances и подбора порога.

A1 завершён process_error до записи нового job/native execution: unit сравнил PID дочернего unittest с initial_main_pid родительского owned worker. Исправлена только служебная проверка: running и точное совпадение /proc/self/cgroup с зарегистрированным control_group. PID различаются штатно. Managed reservations/native policy продолжают проверяться production-путём.

A2 использует новый immutable source и отдельный job/request/output; A1 receipts сохраняются. Все проверки source/runtime, первой матрицы,64 complete observations, frozen hashes, actual timestamps и неуспешного Train прежние. Научные counts не являются ожидаемым условием PASS. Статус на момент декларации: подготовлено; фактический запуск и результат фиксируются отдельно.
