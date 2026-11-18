# Проверка сохранённого экспорта после прерывания задания

Исходный Elder `s10-single-complete-sweep-branch-elder-a3` закрыт с
`owned_native_disk_budget` во время экспорта. Отрицательный исход и отсутствие
execution/run manifest сохраняются. Все948 trial JSON/CSV и958170225-byte
stopped-state файл сохранены lossless.
[Полный корпус, manifest и provenance](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/primary-publication.archive.json).

Следующая проверка относится только к DATA. Новый production test
`tests/test_retained_stopped_export.py` получает отдельные явные fixtures:
исходный native каталог и ожидания exact raw bytes/SHA из проверенного
collector manifest. Он использует штатные `load_case/audit_stopped_state`,
проверяет внутренний digest и replay embedded measurement history без
восстановления native execution, импорта или полномочий обучения. Наличие
summary не подставляется и не фабрикуется. Параметры, revision и причина
остановки берутся из проверенного пакета, не из последних скаляров истории.

До выполнения это лишь реализация и постановка проверки. Возможны отказ
схемы, повреждённый/незакрытый файл, несовместимость или недостаточный ресурс;
наличие архивного файла не доказывает пригодность модели. Положительный DATA
аудит также не означает успешный исход оригинального job. После него всё
равно нужны native import/readback и фактический frozen Test.

Проверка выполняется на освобождённом Elder в отдельной contained группе с
объявленными memory/wall/disk limits и before/after fingerprint всех fixtures.
Новый Train не требуется. Полные результаты остаются во внешнем архиве;
в Git публикуются источник проверки, её декларация и компактная квитанция.

## Выполненная DATA проверка

`s05-retained-stopped-export-audit-elder-a2`, controls
`135b3170d0714cd6232ec9bace914df1a3e2ca92`, Root926dc94:1/1 PASS.
Все before/after source и fixture snapshots совпали. Проверены schema7 digest,
158 групп/948 проб/3413748 sampled frames. Summary отсутствует и не подставлен.
Модельd26d9620dd453539c2446b41fcc2f07d971115bd045206b8dda7497f525d5caa,
L239/201/121/1, Rs8090169.943749473 на первых трёх и86000000 на anchor,Ns1.
Пакет сообщает budget_exhausted/maximum_sweeps_exhausted, certificate=None.
[Полный144319-byte audit и полный provenance](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/retained-model-data-audit.archive.json).
Native import, исходный successful execution и классификация этим не доказаны.
