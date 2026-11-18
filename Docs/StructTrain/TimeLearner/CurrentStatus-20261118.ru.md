# Статус TimeLearner — 18 ноября 2026

Актуализация 17:58UTC. Полная цель этапов0–12 активна. Принят только этап0;
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
критерий TP>=1/TN>=2 выполнен; оба примера включены в опубликованную
третью редакцию DOCX после публикации primary и визуальной проверки графиков.

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
Завершён `s11-fair-input-threshold-report-m40-a1`, controls
`a7974c08821902a00b114b142aac3d8ef9f5d1b7`. Он
использует штатный report_matrix и2 declared-report tests:16 проб/40 trial-soma
pairs, actual input overlays, полные масштабы и zoom>=8pixels/native tick,
без downsampling. Исходный handle unit `timelearner-12031cef-c7a5-4f26-9c1d-16ae3b1005f2`
сохранён; последующее фактическое закрытие подтверждено ниже.
[Handle выполнения](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/temporal-report-running.json).
Задание завершилось:2/2 declared-report tests PASS, без failures/errors/skips;
все40 trial-soma pairs покрыты (Classic32/Branch8), построено4591 PNG и
соответствующие SVG/PDF. Kernel group отсутствует/закрыта, lease освобождён.
[Квитанция закрытия и coverage](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/temporal-report-closed.json).
Первые Classic target/TN/FP графики просмотрены. Галерея опубликована во внешнем CAS и report cache; обзорные графики всех40
пар просмотрены. [Квитанция](../../../Reports/StructTrain/TimeLearner/FairInputCold-20261118/temporal-gallery.archive.json).
Каждый из4591 рисунков вручную не просмотрен. Третья редакция DOCX опубликована:
Classic15/Branch14 страниц,9 подходящих примеров; все29 страниц отрисованы
и визуально проверены. [Документы и квитанция](AlgorithmDescriptions/README.ru.md).
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
(квитанция ниже); baseline Test и исправленный re-audit завершены. При100
модель молчит, проверка выбранного порога выполняется. DATA аудит сам не заменяет native
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

1. Завершить actual native fixed-threshold8 Test сохранённой Elder модели:
   заранее выбран0.09874840158355691; исходный baseline100 уже полностью
   проверен и молчит. Proxy TP1/FP1/FN0/TN6 не заменяет реальные спайки.
2. Принять затронутые readout/physical проверки M40 после свежей сборки,
   затем candidate/ownership coverage. Галерея40 пар и DOCXv3 опубликованы;
   независимая frozen оценка остаётся отдельным следующим шагом.
3. Python8-a3 завершён8/8; сохранить полный corpus во внешнем архиве.
   Подтвердить Linux/native coverage и поддерживаемые режимы по исходному плану.
4. Продолжить алгоритмы: global terminal best-state restoration остаётся
   не реализованным; нельзя заменять её scalar overlay или переносить Exact
   после изменения модели. [Контракт](TerminalBestStateBoundary-20261118.ru.md).

Предыдущий лучший Branch TP1/FP1/FN0/TN6, его order/window проверки и датированные DOCX
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


Последнее подтверждённое состояние: полный baseline audit3 Elder завершён,
TP0/FP0/FN1/TN7 при100; исходный export failure и certificate=None сохранены.
[Новый поддерживаемый отчёт](ElderRecoveredBranchBaseline-20261118.ru.md).
Порог0.09874840158355691 зафиксирован controls793af920 до нового Test.
Подготовка выполнена за453.08с, начался Console native phase:
PID12440/creation_filetime134394974366004162, Job
`Local\TimeLearner-1c08540e-f900-40e1-b0fe-a70df9158f3a`,16GiB.
Итог новой классификации не принят. Одновременно на M40 строится новый
runtime и21-case native gate, sourceRoot6433f59/Pulse5f8; отдельный kernel
unit `timelearner-a0a35042-5a34-4ff7-a7a4-2b324ce07cd3.service`,
PID3087990/start_ticks409920358. [Исправление fixtures и его область](CalibrationReadoutFixtureRepair-20261118.ru.md).
Глобальный возврат terminal best-state остаётся не реализованным; эти
эксперименты и исправления документации не закрывают полный этап7.


Позднейшее native-наблюдение: Console завершился exit0/valid за1866.83с,
cooperative capture47 файлов, все процессы закрыты, исходные Job/PID отсутствуют.
В8 complete/valid native trials фактически записано TP1/FP1/FN0/TN6:
один спайк target в0.4925с, то есть2.5мс после последнего входа0.49с;
один спайк foil phasea-row-4, также через2.5мс после последнего входа.
Остальные6 foils молчат. Recognition revision
`3e7234958d0539f9ee022580ab6149ea4255cb5536a6c9123e75f226ba9d7985`.
Это чтение фактических спайков; полный common source/model audit **ещё работает**,
поэтому новый итог не объявлен принятым научным результатом и не внесён в DOCX.
Порог после просмотра новых ответов не менялся.
[Native observations с hashes](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/fixed-threshold8-native-observations-pending-audit.json),
[закрытие Console и живой audit Job](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/fixed-threshold8-native-closed-audit-running.json).
Текущий audit PID14404/creation_filetime134394993034044420,
Job`Local\TimeLearner-6b944518-9edf-4637-9ce3-6de6e5a64d62`,20GiB.


Последняя проверка18.11,18:46UTC: actual fixed-threshold8 и полный common
source/model/scorer audit **завершены успешно**. TP1/FP1/FN0/TN6 при
0.09874840158355691; все8 окон полны, valid, frozen. Native1866.83с и
audit1436.79с завершились exit0/valid, все процессы закрыты, Job/PID отсутствуют.
Это Same-Matrix Test остановленной BudgetExhausted модели, без TrainingCertificate
и без независимой оценки обобщения. Порог после новых ответов не менялся.
Публикация нового полного primary и его временные графики ещё не завершены;
этот пример пока не добавлен в DOCX.
[Квитанция закрытия и фактические метрики](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/fixed-threshold8-common-audit-closed.json).

Свежая сборка M40 Root6433f59/Pulse5f8 завершена. Все21 заявленных C++ case
выполнены:19 PASS,2 FAIL — NativeCalibrationPersistence/ClassicN1_2000 и
NativeCalibrationPersistence/BranchN1_2000. Gate отклонён; причина двух
отказов ещё не диагностирована, они не объявляются только проблемой fixtures.
Outer supervisor и все зарегистрированные дочерние группы закрыты.
[Отрицательная квитанция](../../../Reports/StructTrain/TimeLearner/CalibrationReadoutCompletion-20261118/linux21-closed-rejected.json).
Расширенная матрица262Linux/261Windows ещё не выполнена. Оба последних
проверенных задания завершены; эта запись заменяет их прежние live-статусы выше.
Этап0 полностью принят,1–12 частичны; глобальный возврат лучшей модели при
остановке, полная режимная приёмка и independent frozen evaluation открыты.
