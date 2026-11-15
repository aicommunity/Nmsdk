# Уточнение дискового резерва

A1 canonical preflight прошёл4166 files/7 IDs, whole group closed/lease released. Native launch отклонён owned_native_capacity_preflight до controller/lease: на Elder свободно3590393856B, MemAvailable29179621376B. Старые4GiB disk reserve +2GiB floor не помещаются.

Принятый тот же M40 SDK реально занимает: build208712KiB + runtime160684KiB + полный native readback116312KiB =485708KiB (около497MB); отдельно уже материализованный source107956KiB. A2 задаёт reservation_disk_bytes1342177280 (1.25GiB, более2.6x измеренного результата), сохраняя physical_free_floor2147483648, memory8GiB, parallel2, все guards/flags/assertions. Reserve+floor3489660928B помещаются в подтверждённое свободное место; live floor продолжает останавливать job при неожиданном росте. Удаление данных не выполнялось. Новый canonical A2 сверяет изменённый native-job SHA; старые A1 controls не меняются.
