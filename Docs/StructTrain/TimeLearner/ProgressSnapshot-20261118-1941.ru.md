# Продвижение по TimeLearner —18 ноября,19:41UTC

Цель0–12 сохраняется полностью: принят этап0,1–12 частичны. Accepted develop
Root87e7da0205b6bb0d582f7b4f2551c935fd7f2350 не менялся. Новый непроверенный
подэтап не объединён в develop. Работа идёт в собственных feature деревьях.

## Научные данные

Actual Branch baseline100 и actual fixed-threshold0.09874840158355691 полностью
проверены; при выбранном пороге TP1/FP1/FN0/TN6. Lossless primary теперь
опубликован в M40 CAS:251652344 bytes,166 verified members,6278048157 expanded
bytes; сохранены прежний неуспешный audit и его успешная recovery.
[Квитанция](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/baseline-and-fixed-threshold-native-primary.archive.json).
Это Same-Matrix Test остановленной модели, без certificate и independent
training. DOCXv3 пока содержит прежние9 примеров, новый сюда ещё не добавлен.

До новых наблюдений объявлен [протокол трёх unseen foils и seen target control](ElderHeldoutScientificProtocol-20261118.ru.md).
Prepare458.31с завершён, actual native phase подтверждена живой на .14:
PID13716/creation_filetime134395033327393688,
Job`Local\TimeLearner-9a5c0a66-ce0c-4739-827f-3cb1b5d9cf5e`.
Модель и порог не выбираются заново; исхода новой классификации пока нет.
[Handle](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/frozen-heldout4-running.json).

Для всех16 baseline/threshold проб подготовлен production temporal report:
16 trial-soma pairs, actual input overlays, native>=8px/tick zoom, без
downsampling. Используется общий renderer/scorer на фактическом архиве,
без выдуманного run-manifest. Controls14173b71d2990eebe7a51fd77c962d686025b4f3,
Scripts actorBfa2c23. Задание ещё не запущено: единственный слот M40 занят
native29. Политика capacity не изменена; launcher готов и проверяет закрытие
предыдущих групп. [Подготовка](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/native-temporal-report-prepared.json).

## Проверки реализации

Все failures прежнего Linux21 относятся к NewOnly открытию одинаковых имён
артефактов readout/persistence. Исправлены namespace persistence и сообщение
об ошибке; защита от перезаписи сохранена. Исходный negative не переписан.
[Диагноз и ограничения](CalibrationReadoutFixtureRepair-20261118.ru.md).

Свежая сборка Rootb14edff/Pulse5f8 уже перешла к native29. Первые N0 threshold
candidate cases Classic/Branch2000Hz не получили исходного certificate
(maximum_sweeps_exhausted), до downstream candidate assertions. Это новые
найденные отказы области, которую прежний frozen248/247 не выбирал. Они
не маскируются и не объясняются исправлением имён. Остальные cases ещё идут;
ни итог29, ни полная262/261 матрица не объявлены PASS.
Owned supervisor3268949/start410453420, unit
`timelearner-8355b7a9-485e-4af7-bf7f-1be573373a76.service` подтверждены живыми.
[Handle](../../../Reports/StructTrain/TimeLearner/CalibrationReadoutCompletion-20261118/linux29-running.json).

В Pulse5f6792f подготовлено сохранение controller SelectedMeasuredBoundary
после AdvanceInput/Stop: действующий Rank, serial/input/sweep context и полное
CandidateEvidence. Три новые kernel regressions ещё не выполнялись и не
входят в текущий Gate29. Это **не** native graph restoration и не новый научный
вариант; дальнейшие capture/terminal transaction/C/owner/export проверки
обязательны. [Оставшийся контракт](TerminalBestStateBoundary-20261118.ru.md).

## Дальше

Завершить существующий heldout4 и его полный common audit; получить исход29,
разобрать N0 source preconditions, затем запустить уже подготовленный report
после освобождения слота. Проверить новые3 kernel cases и подключить native
graph capture/terminal restoration по полной спецификации. Ownership fixture
binding, расширенная матрица, migration/defaults/docs и остальные пункты
исходных этапов остаются обязательными.8/8 не является условием завершения.


## Последующее состояние: три работающих задания

Actual heldout4 native phase завершена за1420.02с, exit0/valid,47 captured loaded
files, все процессы закрыты, исходный Job отсутствует. Записано TP1/FP0/FN0/TN3:
seen target control в0.4925с (2.5мс после последнего входа), три новых foil
без спайков, все4 complete/valid по4001 samples. Полный common audit **ещё идёт**:
PID5572/creation134395047527903832,
Job`Local\TimeLearner-3db3f428-c6ff-4a94-aec7-a3b5c0b94585`.
Это предварительные реальные ответы, а не принятый independent scientific
verdict. [Raw и hashes](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/frozen-heldout4-actual-responses-pending-audit.json),
[закрытие native и живой audit](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/frozen-heldout4-native-closed-audit-running.json).

M40 native29 завершён:25 PASS/4 FAIL, без скрытия отрицательного общего итога.
Обе persistence-проверки теперь прошли в одном процессе с readout; коллизия
имён устранена. Четыре N0 ThresholdCandidate (обе топологии,2k/20k) остановились
на исходном certificate precondition, maximum_sweeps_exhausted; им нужен
явно объявленный валидный source для transport gate, без подстановки certificate
или скрытого расширения допуска. Все группы и supervisor закрыты.
[Отрицательная общая квитанция](../../../Reports/StructTrain/TimeLearner/CalibrationReadoutCompletion-20261118/linux29-closed-rejected.json).

Освободившийся слот M40 занят подготовленным temporal report16 baseline/threshold
проб. Он реально работает в unit`timelearner-8fb630c3-4574-46e4-be82-9754e5f7cce2.service`,
PID3402348/start410770896,24GiB. [Handle](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/native-temporal-report-running.json).

На Elder начата отдельная свежая сборка Root862837e8e45084449f8ad5ca787b201151af6251/
Pulse5f6792fcd346326cab7ed5cd43eebc68e603b38c для14 cases: три новых measured
selection, четыре прежних timing/probe-budget regressions, семь настоящих
physical DATA/storage/frozen cases. Canonical preparation прошла; native
supervisor1322921/start460190828 и unit`timelearner-de46affd-0bf2-4975-a8f3-1e5eea2d50eb.service`
подтверждены живыми. Старые sources/runtimes/builds сохранены; source projection
использует точные Git objects и отдельные hardlinks намеренно частичных old
repositories, не выдуманную доступность их отсутствующей истории. Полнота
4300 materialized code files сверена с Git namespace.512MiB disk reservation,
256MiB free floor заданы явно после проверки реального места.
[Источник, controls и handle](../../../Reports/StructTrain/TimeLearner/MeasuredBoundarySelection-20261118/elder14-running.json).
Новый getter не является native graph restoration; этот пункт этапа7 остаётся
открытым. Только этап0 полностью принят; весь план и independent evaluation
не объявляются завершёнными по raw counts или отдельным SDK cases.
