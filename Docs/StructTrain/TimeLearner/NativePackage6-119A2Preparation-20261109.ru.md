# Native119 A2: полный повтор после timeout

Предыдущий A1 собрал оба targets и подтвердил 19 cases. Classic N6 routing остановлен внешним лимитом 2400 s; сохранены 60 частичных файлов для input0..4, итогового XML нет. Частичные данные не подтверждают завершение N6 и не подменяют оставшиеся 100 cases. Перезапуск исходного задания, изменение его каталога или ретроспективное изменение лимита не выполняются.

Новый запуск использует отдельные SDK/build/runtime/output/controller. Source root `877c1534686d4769142eb690b25799950c1fac81`, Pulse `6741b3c4c05855bf6b53102d27c07cba64378657`, Bin `918ae5e1a2d6085b9ff148f7162eb9e744126592`, Rdk `d6c9df759a3ee20ad42fa0a83841f19385fba60a`. Доставлены восемь самостоятельных clean Git projections; namespace содержит 4052 файла. Canonical preparation должна заново проверить материализацию, native imports, исходную выборку и закрытие 15 предыдущих bound groups до сборки.

По сравнению с A1 C++ и gitlinks не изменены. Python исправления раннего cold7 validation и сохранения typed timeout проверены на M40 22/22 и 13/13. Native Tool — source `b76f23f07a101bc4a9d1b0c9cc7de916a430e8bf`, его worker bytes должны точно совпасть с SDK. Canonical Tool остаётся ранее проверенным `ad3c32d0ae4a9a64991e4f30abfabf27fe98a95f`.

Сохранены **119 IDs, 42 leaves и все 308 artifact rules**. Только два N6 routing leaves получают внешний wall budget 7200 вместо 2400 s, whole-job budget — 43200 вместо 21600 s. Это бюджет выполнения инженерных checks, не изменение model time, timestep, числа входов/проб, шаблона импульсов или допусков обучения. Fixture по-прежнему имеет собственные ограничения 7200 s на attempt и 600 s на группу; их значения не изменяются. Если они исчерпаются, результат останется отрицательным/unresolved.

Такой выбор основан на реальном продвижении пяти входов за исходный внешний бюджет, а не на предположении, что алгоритм корректен. Удлинение бюджета не подтверждает производительность или сходимость. Stack при SIGTERM попал в ModelRevisionObserver; его read-only cache уже существует, поэтому убирать проверки физики или динамически игнорировать свойства ради скорости нельзя. Нужна отдельная атрибуция затрат, если повтор вновь покажет проблему.

Все старые runtime/source/output/controller защищены от записи. Ресурсы, runtime и исходники работающего A2 не обновляются. Сборка остаётся ASan RelWithDebInfo с теми же flags и двумя compilation jobs, оба targets обязательны. Никакого научного PASS этот запуск сам по себе не создаёт: после native acceptance нужны actual package6 Python roundtrip checks и реальный Console Train→export→calibration→frozen Test.

Декларации: [canonical plan](ValidationPlans/NativePackage6-119A2-20261109/canonical-plan.json), [точный cohort](ValidationPlans/NativePackage6-119A2-20261109/cohort.json), [native job](ValidationPlans/NativePackage6-119A2-20261109/native-job.json), [Git delivery observations](ValidationPlans/NativePackage6-119A2-20261109/source-delivery-observation.json). Состояние этого документа при подготовке — ещё не результат запуска.

## Фактический запуск A2

Canonical operation завершён на M40 с кодом 0 за 75.323 s, diagnostics clear. Root независимо сверил все поля 4052 namespace rows с Git-based ledger, 29 SDK imports, 119 cases/42 leaves/308 artifact rules, 15 prior bindings и SHA обоих сформированных native controls. Tool и входные контрольные файлы до/после совпадают, подготовительный lease `40311aab-a029-4d6e-b2dd-e429e4c2a31b` освобождён после закрытия группы.

Создан native controller `/media/user/Data/TimeLearnerRefactor/readbacks/s07-package6-native119-m40-a2-controller`; supervisor PID2168477/start331762638. Последняя непосредственная kernel-проверка подтверждает живой supervisor и running outer unit `timelearner-693a3e78-66f1-47d2-8c6a-eba12d47b3bb.service`, invocation `f965136fc14e4476904dc090fa6e222d`, MainPID2172881/start331763867. Binding SHA `f4e153f1b1a5906ab8cda586a63a418054671d89ea5ccdab69a5d03e5941e5a2`. Это подтверждение запуска, а не успешной компиляции или tests.

[Исходные сжатые canonical/readback/STARTED/kernel наблюдения](../../../Reports/StructTrain/TimeLearner/s07-package6-native119-a2-launch-root-observation/index.json) опубликованы в Git. Полного native результата и нового scientific verdict пока нет. Отдельно остаётся полная compact preservation отрицательного A1: текущий collector schema1 требует завершённые JUnit для всех записанных children и не может честно принять timeout leaf без XML; имеющиеся terminal/частичный inventory не выдаются за полный архив всех A1 primary.
