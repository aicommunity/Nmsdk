# Статус TimeLearner — 18 ноября 2026

Актуализация 13:42UTC. Полная цель этапов0–12 активна. Принят только этап0;
этапы1–12 остаются частичными. Научные8/8 не являются условием завершения.
Accepted root develop `87e7da0205b6bb0d582f7b4f2551c935fd7f2350` не менялся;
новый непроверенный код не объединялся в develop. Пользовательские деревья
E:/Science-Repo/nmsdk-git и C:/Projects/Nmsdk не используются для изменений.

## Получены два новых классификационных результата

| Топология | Порог | TP | FP | FN | TN | Верных ответов |
|---|---:|---:|---:|---:|---:|---:|
|Classic|0.019405139380343855|1|2|0|5|6/8|
|Branch|0.07383352212183064|1|2|0|5|6/8|

Это actual native Test всех8 PhaseA паттернов на каждую фактически сохранённую
cold cap16 модель. Все16 окон complete/valid,2с/reset-per-trial,2000Hz,
по4001 sample на окно; criterion — полное окно от onset. Модели frozen;
ложные ответы rows4/6, остальные5 foils молчат. Штатные manifests обоих
cases completed/valid; общий controller завершился без ошибки, все группы
закрыты, lease освобождён. Это не offline threshold sweep одного CSV.

Обе исходные Train-сессии BudgetExhausted, без certificate. Порог выбран на
той же матрице: Same-Matrix diagnostic stopped models. **Сходимость и
независимое обобщение не подтверждены**. Требуемый для включения в DOCX
критерий TP>=1/TN>=2 выполнен; обновление примеров следует после публикации
primary и визуальной проверки графиков.

[Постановка и ответы каждого паттерна](FairInputColdThresholdStudy-20261118.ru.md).
[Полный компактный readback](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/threshold-confirmation-closed.json).
Native Root445c834/Pulsec54d9c0, actor RootEA0b039; новый frozen DATA API в
этих научных результатах не использовался.

## Primary и временные графики

Original Train primary уже опубликован:48281492 bytes, catalog
`experiments/2026-11-18/fair-input-cold/primary-a1.json`.
[CAS refs](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/primary-publication.archive.json).
Первичная подпороговая matrix16 при100 сохранена: обе модели молчат;
её исходный общий owner wall-timeout и отсутствие Branch run manifest
не переписываются. Новый threshold16 выполнен отдельно и полностью.

На M40 завершён `s11-fair-cold-threshold-primary-m40-a1`, controls
`90f20e278702e754a5f15378fc9dc3c16bb4f3e1`: lossless collection обеих matrix16
с их разными исходами и всеми source/summary/model/trial/closure файлами.
Полный primary171725152 bytes,15176675667 expanded bytes,3979 members;
catalog `experiments/2026-11-18/fair-input-cold/baseline-and-threshold-primary-a1.json`.
[CAS refs и4 controls Git bundles](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/baseline-and-threshold-primary.archive.json).
Выполняется `s11-fair-input-threshold-report-m40-a1`, controls
`a7974c08821902a00b114b142aac3d8ef9f5d1b7`. Он
использует штатный report_matrix и2 declared-report tests:16 проб/40 trial-soma
pairs, actual input overlays, полные масштабы и zoom>=8pixels/native tick,
без downsampling. Подтверждены live kernel unit/lease, PID2469972,
start_ticks407772835, unit `timelearner-12031cef-c7a5-4f26-9c1d-16ae3b1005f2`.
[Handle выполнения](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/temporal-report-running.json).
Задание завершилось:2/2 declared-report tests PASS, без failures/errors/skips;
все40 trial-soma pairs покрыты (Classic32/Branch8), построено4591 PNG и
соответствующие SVG/PDF. Kernel group отсутствует/закрыта, lease освобождён.
[Квитанция закрытия и coverage](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/temporal-report-closed.json).
Первые Classic target/TN/FP графики просмотрены. Галерея опубликована во внешнем CAS и report cache; обзорные графики всех40
пар просмотрены. [Квитанция](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/temporal-gallery.archive.json).
Каждый из4591 рисунков вручную не просмотрен. Новые примеры включены в
исходники третьей редакции DOCX; отрисовка и приёмка новой редакции впереди.
Большие архивы и рисунки остаются во внешнем M40 хранилище, в Git — ссылки.

## Elder: модель сохранена и DATA проверены без повторного Train

Исходный `s10-single-complete-sweep-branch-elder-a3` остановлен во время
экспорта по `owned_native_disk_budget`: лимит1.5GiB, peak1677475840 bytes,
свободно не менее1309941760 bytes. Все units закрыты. Это отрицательный
execution outcome; успешное завершение оригинального job не приписывается.
Полный primary опубликован:28666564 bytes, SHA
`ccfc316d1da3d9ee84f66092e02c674153891c0aaef7a6ff44d9ca9cc711ec85`.
[Корпус и provenance](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/primary-publication.archive.json).

Отдельный `s05-retained-stopped-export-audit-elder-a2` прошёл1/1, без
failures/errors/skips. Штатные readers на Root926dc94 проверили внутренний
digest958170225-byte schema7 пакета,158 групп,948 проб,3413748 sampled frames,
before/after source/fixture fingerprints. Отсутствующий summary не создан.
Пакет сообщает BudgetExhausted/maximum_sweeps_exhausted, certificate=None.

Длины239/201/121/1; Rs первых трёх8090169.943749473, anchor86000000;
Ns=1 для всех. Revision
`d26d9620dd453539c2446b41fcc2f07d971115bd045206b8dda7497f525d5caa`.
[Проверка и ограничения восстановления](RetainedStoppedExportRecovery-20261118.ru.md).
[Полный audit/provenance во внешнем CAS](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/retained-model-data-audit.archive.json).
Native import/readback уже подтверждены отдельным фактическим процессом
(квитанция ниже); Test выполняется. DATA аудит сам не заменяет native
проверку и не меняет исходный execution failure.

## Frozen DATA: проверенная часть и оставшиеся отказы

Root28f748a/Pulse5f8b281: **7/7 NativePhysicalModelData PASS** на .14,
без skips/errors/failures;3 исправленных fixture cases и4 прежних regressions.
Исправление — Init свежих owners и реальный ModelArchiveError, без смены
физики, алгоритма или допусков.
[Matching native readback](../../../Reports/StructTrain/TimeLearner/WindowsPhysicalModelData-20261118/frozen-native7-observed.json).

Новый Console процесс Classic и затем Branch проверены на этих N2 fixtures:
4 complete observations, штатные job parser/scheduler/audit/scorer, неизменная
DATA модель и совпавшие response counts. Recovery использует уже завершённый
Classic; повторно рассчитан только ранее не запускавшийся Branch. Исходный
ошибочный metadata-wrapper outcome сохранён. Это проверка интерфейса,
**не научный N4 результат и не общий Windows worker admission**.
[Квитанция](../../../Reports/StructTrain/TimeLearner/WindowsPhysicalModelData-20261118/frozen-console-recovery-observed.json).

Python8 на actual native artifacts:7 PASS/1 FAIL, без errors/skips. Отказ
в CLI fixture: она сравнивала весь стандартный envelope с внутренними
метриками. CLI вернул execution completed/valid и штатный analysis envelope;
fixture исправлена на проверку envelope и точное сравнение его analysis.
Повторная серверная проверка `python8-a3` прошла8/8 без failures/errors/skips;
controls698b489, PythonRooted2 и неизменные native fixtures Root28/Pulse5f8.
[Новая квитанция](../../../Reports/StructTrain/TimeLearner/WindowsPhysicalModelData-20261118/frozen-python8-a3-observed.json).
[Исходный log/result](../../../Reports/StructTrain/TimeLearner/WindowsPhysicalModelData-20261118/frozen-python8-rejected.json).

Полный прошлый247-case gate остаётся отрицательным:230 PASS/9 failures/8 skips.
Отдельный7-case gate не превращается в full247 PASS.6 старых readout/calibration
preconditions и8 ownership data prerequisites ещё не закрыты; один singleton
A/B подтвердил одинаковый отказ исходной learning fixture на старом/новом коде.
[Причины, опубликованный отрицательный corpus и данные для дальнейших проверок](WindowsFrozenDataGate-20261118.ru.md).
Linux248 и полная матрица режимов остаются открытыми. Новый DATA release
не объявляется принятым по одному Windows7 или Console4.

## Следующие действия по основной цели

1. Опубликовать завершённую40-pair gallery, визуально проверить все
   паттерны и обновить DOCX примерами двух новых6/8. Primary уже опубликован.
2. Проверить native import и actual frozen Test сохранённой Elder модели;
   source уже целостен, повторять Train ради утраченного summary не требуется.
3. Python8-a3 завершён8/8; сохранить полный corpus во внешнем архиве.
   Подтвердить Linux/native coverage и поддерживаемые режимы по исходному плану.
4. Продолжить алгоритмы: global terminal best-state restoration остаётся
   не реализованным; нельзя заменять её scalar overlay или переносить Exact
   после изменения модели. [Контракт](TerminalBestStateBoundary-20261118.ru.md).

Предыдущий лучший Branch TP1/FP1/FN0/TN6, его order/window проверки и DOCXv2
сохраняются отдельными результатами. Новые6/8 не являются независимым
повторением прежнего алгоритма и не отменяют августовские4/8–6/8.


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

Запущен `windows-elder-single-sweep-baseline8-a1`, controls
`9f988b67aa3f94549f2497450743b65e7a6ccfe1`: исходный порог100, identity recognition
conversion, все8 PhaseA паттернов/2с/reset-per-trial. Preparation уже завершена;
native PID15516/creation_filetime134394840822181093 подтверждён живым в Job
`Local\TimeLearner-d5794517-50ae-475e-ad91-c44603fb5cff`, лимит16GiB.
Конечная классификация и полный audit ещё не приняты.
