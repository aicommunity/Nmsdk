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


Актуализация после native roundtrip: отдельный Windows job
`windows-elder-retained-physical-export-a2-recovery-a1`, controls
`78a737b330f359c1ab64cd7ee46e81077a073212`, завершён exit0/valid за341.15с.
Cooperative loaded-files capture выполнен, все процессы закрыты; kernel Job
и исходный PID отсутствуют. Native импорт и полный физический export/import
сохранили revision d26d9620dd453539c2446b41fcc2f07d971115bd045206b8dda7497f525d5caa.
DATA audit остаётся отдельно byte-only и сам не утверждает native execution.
[Фактическая native квитанция](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/native-import-roundtrip-observed.json).
Новый Train не выполнялся. Исходные отрицательные a1/a2 metadata outcomes
сохраняются; успешная recovery использует уже проверенный источник и явно
связанный backend, без повторного восстановления архива.

`windows-elder-single-sweep-baseline8-a1`, controls
`9f988b67aa3f94549f2497450743b65e7a6ccfe1`: исходный порог100, identity recognition
conversion, все8 PhaseA паттернов/2с/reset-per-trial.
Проверка18 ноября14:48UTC: native Test завершился exit0/valid за1682.26с,
все процессы закрыты, исходные kernel Job/PID отсутствуют. Созданы8 trial files,
но последующий production audit завершился exit1 с `recognition_images_changed`:
`class_definitions` recognition archive не совпали с исходным stopped neuron.
Это обнаруженное несовпадение ещё не классифицировано как сериализация или
изменение физики; проверка не ослаблена. Metrics и положительный scientific
verdict не опубликованы. Новый результат классификации не принят; повторный
Train/Test не запускался. Требуется сравнить реальные образы и устранить
причину, затем повторить аудит сохранённых наблюдений, если они применимы.
[Закрытие процессов и отказ](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/baseline8-audit-rejected-observed.json).
[Точный traceback и inventory](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/baseline8-audit-rejection-diagnosis.json).


Дополнение: причина `recognition_images_changed` установлена — разные native
XML encodings Linux/Windows и диагностический DebugSysEventsMask. Физические
identity всех31 образов совпали. Аудиторversion3 использует общий semantic
storage contract с проверками hashes/closure и отдельным native import gate.
Адресные проверки11/11 прошли на .14, без skips/errors/failures. Полный аудит
прежних8 наблюдений сейчас выполняется в отдельном bounded Python Job;
native Test и Train не повторяются. Итоговая классификация Elder пока не принята.
[Причина, исправление, проверки и handle](CrossPlatformStorageImageAudit-20261118.ru.md).
