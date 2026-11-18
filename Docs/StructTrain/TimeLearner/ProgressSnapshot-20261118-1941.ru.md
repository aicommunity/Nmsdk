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
