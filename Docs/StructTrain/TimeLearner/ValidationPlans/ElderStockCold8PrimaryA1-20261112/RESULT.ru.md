# Независимое восстановление полного N4 primary — принято на Elder, 12.11.2026

**1/1 PASS**, без failures/errors/skips: [исходный unittest log](completed/worker/validation/unittest.log), [результат](completed/worker/validation/result.json). Один integration test проверяет обе настоящие остановившиеся модели, восстановленные из Git, без нового расчёта нейрона. Source41d880e33ffcc930c0515fa8793bf7101996f25f; actor40e28802c29014ec8a5af0f8763aa607ad9a986a; package de5fd75f66ac1b5d5b3f598faf2ba6731e818a2dc7a63d47df90d634f8465dd8.

[Архив](../../../../../Reports/StructTrain/TimeLearner/StockCold8N4StoppedPrimary-20261112/) —24627936 bytes, SHA256 fbffa754e4f6ecf18941e5b0112dc67db025ff5dc818c636eacf561841328c7c. Production portable reader проверил все1171 members. Explicit glog adapter исключил из временной производной копии четыре подтверждённых одинаковых alias, сохранив1167 regular files. Архив, исходные конфиги, модели и результаты не менялись; исходная форма symlink отдельно не аттестуется. [Полный receipt](completed/worker/tmp/stock-cold8-primary-independent-restoration.json).

| Случай | Logical groups | Native probes | Sampled frames | Исходный результат | Итоговые L |
|---|---:|---:|---:|---|---|
| Classic N4/N1 |24|144|518544|invalid_observation|7,1,1,1|
| Branch N4/N1 |28|168|604968|invalid_observation|7,7,7,1|

Для каждой модели общий production reader проверил source7/summary8, полные full/omission первичные данные и recovery ledger: четыре cursor_advanced, затем invalid_budget_stop. Проверены физические параметры конечного графа относительно архивного native preflight. Certificate/Exact отсутствуют. После добавления повреждённых байтов в настоящую извлечённую первичную трассу аудит отказал для каждой модели; embedded данные не скрыли повреждение внешнего файла.

Unittest173.133s, outer192.128s. [Controller result](completed/controller-result.json):completed, whole group closed, diagnostics clear. [Closure и leases](completed/closure-and-reservation.json):закрыто, ресурсы released; heartbeat_errors отсутствуют. Снимки actor/source/fixtures до и после совпадают; [контрольные суммы точных readbacks](completed/readback-integrity.json). TemporaryDirectory удалил временное восстановление штатно.

Это независимая DATA-приёмка доступности и повторного анализа полного корпуса, а не повторный Train, импорт исполняемого состояния или успех классификации. Исходные отрицательные результаты сохраняются. [Новый Train с исправленным доменом наблюдения](../M40ObservationDomainTrainA1-20261112/README.ru.md) является отдельной попыткой; его результат здесь не оценивается. Полный план0–12 не закрыт.
