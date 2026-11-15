# Полный контроль coordinator schema1/schema2: запуск06.11

Статус: выполняется; PASS не объявлен. Это инженерная проверка контура,
а не независимая научная серия.

На Elder создан отдельный immutable Git checkout
`/home/user/timelearner-refactor/source-pipeline-condition-matrix-a1`:
root `83a82844a6792e23f39106d1d3f41e8638920077`, code pack3884550 bytes,
SHA256 `ec6d6dd17167878d7cf8e06189cd88f6c48b0804364a10b4070ce8467cd6e419`.
Runtime прежний, compiled SDK `2e0618110a9abb48b94f6edc6b63c51f829ec810`,
Console SHA256 `b2d98c8f85be0ff5d87769ddd4285bbc2ee2fc8b39609d2bd4833149865c5153`.

Запущены два неизменённых production unittest класса: по8 случаев schema1/schema2,
с отдельными output/declaration/controller bindings. Ожидаются16 проверок,
40 различных actual native phase units: Classic/Branch ModelSpec1/2 positive
cold/boundary/continue/calibration/frozen и N0/N1 stopped без export/Test.
Дополнительная проверка сопоставит declared ConditionSpec fingerprints и все
реальные CSV по относительному пути, размеру и SHA256 между схемами.
Несовпадение не будет скрыто или автоматически нормализовано.

A1 `s10-pipeline-condition-native-matrix-a1` завершилась до запуска модели:
временный producer передал строку вместо Path в native_evidence.load.
Исправлен только producer; source/runtime/test classes неизменны. Оба исходных
процесса A1 подтверждены отсутствующими перед отдельным запуском A2.
A1 сохраняется для публикации вместе с результатами A2.

A2 output `/home/user/timelearner-refactor/readbacks/s10-pipeline-condition-native-matrix-a2`.
Подтверждены wrapper PID3866827/start351579822 и worker PID3866839/start351579834.
Первый наблюдавшийся native PID3868101/start351581901 был R, start совпал с
owned-process.json. Это подтверждение фактического начала, не итоговый verdict.

Parent cap512MiB, каждый native4GiB, последовательный запуск; global lease
slot1/RAM4.5GiB/output1280MiB, heartbeat и отмена только принадлежащих фаз
при свободном месте менее1GiB. Это учёт бюджета, не filesystem quota.
После завершения требуются fresh closures, leases, full primary/source hashes,
проверка всех16 IDs без skips и публикация Git; затем временные отчёты/visual QA.

Независимый M40 ASan133 не перезапускался. При последнем просмотре реально
выполнялся case0113 NativeLearnerDimensions.ClassicSixInputs2000,
PID795359/start302113506, состояние R. Завершение не установлено.
Этапы1–12 исходного плана остаются частичными.
