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
