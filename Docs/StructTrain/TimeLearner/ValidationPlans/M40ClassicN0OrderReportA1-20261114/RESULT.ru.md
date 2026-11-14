# A1: выбран Python без matplotlib

Outer process_error860.7315219710581с, whole group закрыта; unit1 error,832.163с. После большого source audit render отказал: ModuleNotFoundError matplotlib. Новая модель/порог не запускались; результат64 native проб TP8/FP32/FN0/TN24 остаётся принятым.

В launcher ошибочно указан /usr/bin/python3 вместо существующего проверенного plot-python-owned-copy-a1/bin/python. [A2](../M40ClassicN0OrderReportA2-20261114/PLAN.ru.md) выбирает это окружение и переносит plotting_runtime preflight до большого аудита; версии библиотек сохраняет в manifest. Код solver/scorer/data не меняется.

[Log](completed/worker/validation/unittest.log), [integrity](integrity.json). Literal producer 03c8c9785ff1c58155223513345c210e42a8ca68, pack SHA256ce58ab4e680f736af2ad6d64642601fc3c6edb97fb9888acf2cf99dea2d03fa6.

[Фактический A2 completed/closed,1/1 PASS](../M40ClassicN0OrderReportA2-20261114/RESULT.ru.md),13 selected originals просмотрены. Использовано ранее проверенное plot environment; исходный A1 отказ сохранён.
