# Сохранённая Branch-модель Elder: исходный Test и проверка порога

18 ноября: исходный native Test всех8 PhaseA паттернов и полный повторный
аудит завершены. При унаследованном пороге100 модель молчит на всех паттернах:
TP0/FP0/FN1/TN7. Это валидный отрицательный результат, **не работающая
классификация**, несмотря на семь правильно отклонённых foils.
[Закрытие процессов, метрики и8 наблюдений](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/baseline8-audit-recovery-closed.json).

Взят фактический958170225-byte stopped export Elder, revision
`d26d9620dd453539c2446b41fcc2f07d971115bd045206b8dda7497f525d5caa`:
L239/201/121/1; Rs8090169.943749473 на первых трёх,86000000 на anchor; Ns1.
Нового Train нет. Исходный disk-budget отказ при экспорте не превращён в
successful execution; сохранённый Train сообщает BudgetExhausted, certificate=None.
Identity recognition conversion не меняла Rs, все входы включены штатно.

## Протокол и проверка

Каждый из8 паттернов предъявлен с reset-per-trial, окно2с,2000Hz,
4001 native samples, criterion от stimulus onset до конца полного окна.
Native Root28f748a/Pulse5f8b281, отдельный Python actor Root7207184.
Native процесс завершился exit0/valid за1682.26с с47 loaded-file records.
Первоначальный audit2 отказал на Linux/Windows XML representations.
После [исправления сравнения storage](CrossPlatformStorageImageAudit-20261118.ru.md)
и11/11 regression tests полный audit3 прежних файлов завершился за1325.00с,
exit0/valid,33 loaded-file records, все процессы закрыты, Job/PID отсутствуют.
Полные source и recognition physics, XML hashes/dependency closure,
полнота всех проб и frozen model-before/after проверены.

DATA-аудитор по-прежнему сообщает native_import_verified=false и
native_execution_verified=false: сам reader не является запуском модели.
Факт настоящего Console execution и native roundtrip подтверждён отдельно.
Исходная история обучения без утраченного summary не объявляется полностью
восстановленной; evidence omissions не достраиваются.

## Заранее зафиксированный кандидат порога

| Паттерн | Метка | Максимум LT в исходном полном окне |
|---|---|---:|
|0|target|0.1011774808657887|
|1|foil|0.07856864547469888|
|2|foil|0.07956829422265843|
|3|foil|0.05689868496316586|
|4|foil|0.10161009559353007|
|5|foil|0.07980352187443518|
|6|foil|0.09631932230132512|
|7|foil|0.0715893775677715|

По прежнему midpoint rule между target и ближайшим строго меньшим foil
выбран **один** кандидат0.09874840158355691. Предварительная nonspiking
оценка TP1/FP1/FN0/TN6 не заменяет реальный прогон: спайк меняет динамику.
Для этого же набора данных это Historical Same-Matrix calibration,
независимость Test не заявляется. Никакой иной порог после просмотра ответа
нового Test автоматически не выбирается.
[Фактические8 файлов и гипотеза](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/baseline8-raw-lt-threshold-hypothesis.json).

Controls`793af9201fdffc32f9bef9a2bc74479b9bf8fd62` зафиксированы **до** нового
прогона. После успешного baseline audit запущен
`windows-elder-fixed-threshold8-a1`: тот же полный source, identity conversion,
2с/reset-per-trial, все8 паттернов, один фиксированный порог. Подтверждена
живая подготовка в bounded Windows Job; результат ещё не принят.
[Объявление](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/fixed-threshold8-declared.json),
[первый handle](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/fixed-threshold8-preparing-observed.json).

После завершения нужны common audit/scorer, native threshold confirmation,
внешний primary и временные графики всех8 Soma responses с actual input
overlays в читаемом масштабе. До этого вариант не включается в DOCX как рабочий.
Большие новые Windows-артефакты пока в private worker cache; перенос всего
корпуса во внешний M40 архив остаётся открытым. Ни один большой архив/рисунок
не добавлен в корневой Git.


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
